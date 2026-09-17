import * as T from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { WORLDS } from './catalog';

type Part={node:T.Object3D;position:T.Vector3;scale:T.Vector3;index:number};
type Actor={node:T.Object3D;rotation:T.Euler;position:T.Vector3};
type Loaded={outer:T.Group;scene:T.Group;parts:Part[];actors:Actor[];id:number};
export function createViewer(host:HTMLDivElement,onState:(s:'ready'|'loading'|'error')=>void,onPause:()=>void,initialIndex=0,prefetch=true){
 const renderer=new T.WebGLRenderer({alpha:true,antialias:true,powerPreference:'low-power'});
 renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.8));renderer.setClearColor(0xf5f3f8,0);
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;renderer.outputColorSpace=T.SRGBColorSpace;
 renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 host.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-hidden','true');
 const scene=new T.Scene(),turntable=new T.Group();scene.add(turntable);
 const camera=new T.OrthographicCamera(-4.8,4.8,4.4,-4.4,.1,70),target=new T.Vector3(0,.75,0);
 // A neutral environment supplies diffuse bounce; there is just one direct light.
 // Both the camera azimuth and light stay outside the rotating model hierarchy.
 const environmentScene=new T.Scene();environmentScene.background=new T.Color(0xc9c9c9);
 const pmrem=new T.PMREMGenerator(renderer),environment=pmrem.fromScene(environmentScene,.04);
 scene.environment=environment.texture;scene.environmentIntensity=.48;pmrem.dispose();
 const key=new T.DirectionalLight(0xffedda,4.5);key.name='Fixed studio key';key.position.set(-3,8,5);
 key.castShadow=true;key.shadow.mapSize.set(1024,1024);key.shadow.intensity=.25;key.shadow.radius=8;
 Object.assign(key.shadow.camera,{left:-5,right:5,top:5,bottom:-5,near:.1,far:25});
 key.shadow.normalBias=.025;key.shadow.bias=-.00012;scene.add(key);
 const shadowGeometry=new T.PlaneGeometry(60,60),shadowMaterial=new T.ShadowMaterial({color:0x504861,opacity:.8});
 const ground=new T.Mesh(shadowGeometry,shadowMaterial);ground.rotation.x=-Math.PI/2;ground.position.y=-.48;ground.receiveShadow=true;scene.add(ground);
 const loader=new GLTFLoader(),cache=new Map<number,Promise<Loaded>>();
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 let destroyed=false,serial=0,current:Loaded|undefined,incoming:Loaded|undefined,transitionElapsed=0;
 let frame=0,visible=true,paused=reduced.matches,dragging=false,pointerId:number|undefined;
 let downX=0,downY=0,baseYaw=0,yaw=0,pitch=.6,basePitch=.6,last=0,elapsed=0;
 const disposeObject=(root:T.Object3D)=>root.traverse(o=>{if(o instanceof T.Mesh){o.geometry.dispose();const ms=Array.isArray(o.material)?o.material:[o.material];ms.forEach(m=>{for(const v of Object.values(m))if(v instanceof T.Texture)v.dispose();m.dispose()})}});
 function load(id:number):Promise<Loaded>{
  if(cache.has(id))return cache.get(id)!;
  const promise=loader.loadAsync('/dioramas/'+WORLDS[id].slug+'.glb').then(gltf=>{
   if(destroyed){disposeObject(gltf.scene);throw new Error('disposed')}
   const outer=new T.Group();outer.add(gltf.scene);outer.visible=false;turntable.add(outer);
   const world=gltf.scene.children.find(c=>c.name.startsWith('DIORAMA'))||gltf.scene;
   const parts:Part[]=world.children.map((node,index)=>({node,position:node.position.clone(),scale:node.scale.clone(),index}));
   const actors:Actor[]=[];
   gltf.scene.traverse(o=>{
    if(o instanceof T.Mesh){o.castShadow=true;o.receiveShadow=true}
    if(/^(HEAD|ARM_|TORSO|MOTION_paper|MOTION_roller|MOTION_bmx_wheel|Fader_cap|Code_line)/.test(o.name))actors.push({node:o,rotation:o.rotation.clone(),position:o.position.clone()});
   });
   return{outer,scene:gltf.scene,parts,actors,id};
  }).catch(error=>{cache.delete(id);throw error});cache.set(id,promise);return promise;
 }
 function reset(v:Loaded){v.outer.position.set(0,0,0);v.outer.rotation.set(0,0,0);v.outer.scale.setScalar(1);for(const p of v.parts){p.node.position.copy(p.position);p.node.scale.copy(p.scale)}}
 function snap(){if(incoming){if(current)current.outer.visible=false;current=incoming;incoming=undefined;reset(current);current.outer.visible=true}}
 async function select(id:number){
  if(!Number.isInteger(id)||id<0||id>=WORLDS.length)return;
  const request=++serial;onState('loading');
  try{const next=await load(id);if(destroyed||request!==serial)return;snap();if(current===next){onState('ready');return}
   reset(next);next.outer.visible=true;
   if(!current||reduced.matches){if(current)current.outer.visible=false;current=next;incoming=undefined;reset(next)}
   else{incoming=next;transitionElapsed=0;incoming.outer.scale.setScalar(.001)}
   onState('ready');wake();if(prefetch)void load((id+1)%WORLDS.length).catch(()=>{});
  }catch{if(!destroyed&&request===serial)onState('error')}
 }
 const ease=(v:number)=>1-Math.pow(1-v,3),clamp=(v:number)=>Math.max(0,Math.min(1,v));
 function animate(v:Loaded,t:number){
  v.actors.forEach(({node,rotation,position},i)=>{
   node.rotation.copy(rotation);node.position.copy(position);
   const phase=i*.37,n=node.name;
   if(n.startsWith('HEAD')){node.rotation.y+=Math.sin(t*.75+phase)*.11;node.rotation.x+=Math.sin(t*1.2+phase)*.035}
   else if(n.startsWith('TORSO'))node.position.y+=Math.sin(t*1.6+phase)*.009;
   else if(n.startsWith('ARM_')){
    const slug=WORLDS[v.id].slug,drawing=slug==='graphic-arts'||slug==='family',typing=slug==='ai';
    node.rotation.x+=Math.sin(t*(typing?4.7:drawing?2.2:1.5)+phase)*(typing?.045:drawing?.075:.035);
   }
   else if(n.startsWith('MOTION_paper'))node.rotation.x+=Math.sin(t*1.2+phase)*.06;
   else if(n.startsWith('MOTION_bmx_wheel'))node.rotation.z+=Math.sin(t*.9)*.20;
   else if(n.startsWith('MOTION_roller'))node.rotation.x+=t*.55;
   else if(n.startsWith('Fader_cap'))node.position.z+=Math.sin(t*.7+phase)*.035;
   else if(n.startsWith('Code_line'))node.scale.x=.85+Math.sin(t*1.2+phase)*.15;
  });
 }
 function render(now:number){
  frame=0;if(destroyed||!visible||document.hidden)return;
  const dt=Math.min((now-last)/1000,.04);last=now;
  if(!paused){elapsed+=dt;if(!dragging)yaw+=dt*.075}
  turntable.rotation.y=yaw;
  camera.position.set(Math.sin(.64)*12*Math.cos(pitch),.75+Math.sin(pitch)*12,Math.cos(.64)*12*Math.cos(pitch));camera.lookAt(target);
  if(incoming){
   transitionElapsed+=dt;const p=clamp(transitionElapsed/1.35),out=ease(clamp(p/.65));
   if(current){current.outer.rotation.y=out*1.25;current.outer.position.y=-out*2.1;current.outer.scale.setScalar(Math.max(.001,1-out));current.outer.visible=p<.66}
   const entry=ease(clamp((p-.28)/.72));incoming.outer.rotation.y=-1.15*(1-entry);incoming.outer.position.y=-1.1*(1-entry);incoming.outer.scale.setScalar(Math.max(.001,entry));
   for(const part of incoming.parts){if(part.index<2)continue;const delay=(part.index%9)*.022,local=ease(clamp((p-.3-delay)/(.7-delay)));part.node.position.y=part.position.y+(1-local)*1.8;part.node.scale.copy(part.scale).multiplyScalar(Math.max(.001,local))}
   if(p===1)snap();
  }
  if(current&&!incoming&&!paused)animate(current,elapsed);
  renderer.render(scene,camera);if(!paused||incoming||dragging)frame=requestAnimationFrame(render);
 }
 function wake(){if(!frame&&!destroyed){last=performance.now();frame=requestAnimationFrame(render)}}
 function pauseFromInteraction(){if(!paused){paused=true;onPause()}}
 const resize=()=>{const w=host.clientWidth,h=host.clientHeight;if(!w||!h)return;renderer.setSize(w,h);const aspect=w/h,viewH=Math.max(7.9,8/aspect);camera.left=-viewH*aspect/2;camera.right=viewH*aspect/2;camera.top=viewH/2;camera.bottom=-viewH/2;camera.updateProjectionMatrix();wake()};
 const ro=new ResizeObserver(resize);ro.observe(host);resize();
 const io=new IntersectionObserver(es=>{visible=es[0].isIntersecting;if(visible)wake()});io.observe(host);
 const down=(e:PointerEvent)=>{if(!e.isPrimary||e.button!==0)return;pointerId=e.pointerId;downX=e.clientX;downY=e.clientY;baseYaw=yaw;basePitch=pitch;host.setPointerCapture(e.pointerId)};
 const move=(e:PointerEvent)=>{if(pointerId!==e.pointerId)return;if(!dragging&&Math.hypot(e.clientX-downX,e.clientY-downY)<4)return;dragging=true;pauseFromInteraction();host.classList.add('is-dragging');yaw=baseYaw+(e.clientX-downX)*.009;pitch=Math.max(.28,Math.min(.95,basePitch+(e.clientY-downY)*.004));wake()};
 const up=()=>{pointerId=undefined;dragging=false;host.classList.remove('is-dragging')};
 host.addEventListener('pointerdown',down);host.addEventListener('pointermove',move);host.addEventListener('pointerup',up);host.addEventListener('pointercancel',up);host.addEventListener('lostpointercapture',up);
 const visibility=()=>{if(!document.hidden)wake()};document.addEventListener('visibilitychange',visibility);
 const motionChange=()=>{if(reduced.matches){paused=true;onPause();snap();wake()}};reduced.addEventListener('change',motionChange);
 const contextLost=(e:Event)=>{e.preventDefault();onState('error');cancelAnimationFrame(frame);frame=0};renderer.domElement.addEventListener('webglcontextlost',contextLost);
 void select(initialIndex);
 return{select,rotate:(direction:number)=>{pauseFromInteraction();yaw+=direction*.45;wake()},reset:()=>{yaw=0;pitch=.6;wake()},pause:(value:boolean)=>{paused=value;wake()},dispose:()=>{
  destroyed=true;serial++;cancelAnimationFrame(frame);ro.disconnect();io.disconnect();
  host.removeEventListener('pointerdown',down);host.removeEventListener('pointermove',move);host.removeEventListener('pointerup',up);host.removeEventListener('pointercancel',up);host.removeEventListener('lostpointercapture',up);
  document.removeEventListener('visibilitychange',visibility);reduced.removeEventListener('change',motionChange);renderer.domElement.removeEventListener('webglcontextlost',contextLost);
  cache.forEach(p=>void p.then(v=>disposeObject(v.scene)).catch(()=>{}));shadowGeometry.dispose();shadowMaterial.dispose();environment.dispose();renderer.dispose();renderer.domElement.remove();
 }};
}
