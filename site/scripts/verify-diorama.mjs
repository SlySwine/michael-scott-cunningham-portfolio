// Exercise the real viewer state with Three.js scene graphs and a renderer stub.
// This checks animation and interaction without launching a browser.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import * as Three from 'three';
import {GLTFLoader as RealLoader} from 'three/addons/loaders/GLTFLoader.js';
import ts from 'typescript';
const slugs=['ai','photography','graphic-arts','events','fabrication','family'];
const models=[];
const named=(root,prefix)=>{let found;root.traverse(o=>{if(o.name.startsWith(prefix))found??=o});return found};
for(const slug of slugs){
 const bytes=await fs.readFile(new URL('../public/dioramas/'+slug+'.glb',import.meta.url));
 const gltf=await new RealLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 assert.equal(gltf.scenes.length,1,slug+' contains one scene');
 let meshes=0;gltf.scene.traverse(o=>{if(o.isMesh)meshes++});assert.ok(meshes>70,slug+' has complete geometry');
 assert.ok(named(gltf.scene,'MICHAEL'),slug+' contains Michael');
 if(slug==='family'){assert.ok(gltf.scene.getObjectByName('DAUGHTER'));assert.ok(gltf.scene.getObjectByName('WIFE'));assert.ok(gltf.scene.getObjectByName('BMX_BICYCLE'));assert.ok(gltf.scene.getObjectByName('GARAGE_FRONT'));assert.ok(named(gltf.scene,'Wife_wrench'));gltf.scene.traverse(o=>assert.ok(!/laptop|tablet|sketch|crayon|beanbag/i.test(o.name),'family contains bicycle work, not screens or beanbags'))}
 models.push(gltf.scene);console.log(slug+': '+meshes+' meshes, valid character hierarchy');
}
let renderedScene,renderedCamera;const scheduled=new Map();let seq=0,time=performance.now();
globalThis.requestAnimationFrame=callback=>{scheduled.set(++seq,callback);return seq};
globalThis.cancelAnimationFrame=id=>scheduled.delete(id);
const canvas={setAttribute(){},addEventListener(){},removeEventListener(){},remove(){}};
class Renderer {domElement=canvas;shadowMap={};setPixelRatio(){}setClearColor(){}setSize(){}dispose(){}render(s,c){renderedScene=s;renderedCamera=c}}
class PMREM {fromScene(){return{texture:new Three.Texture(),dispose(){}}}dispose(){}}
let deferred=new Map();
class Loader {loadAsync(path){const id=slugs.indexOf(path.split('/').at(-1).replace('.glb',''));if(deferred.has(id))return deferred.get(id).promise;return Promise.resolve({scene:models[id].clone(true)})}}
globalThis.__dioramaThree={...Three,WebGLRenderer:Renderer,PMREMGenerator:PMREM};globalThis.__dioramaLoader=Loader;
const reduced={matches:false,addEventListener(){},removeEventListener(){}};
globalThis.window={devicePixelRatio:1,matchMedia:()=>reduced};
globalThis.document={hidden:false,addEventListener(){},removeEventListener(){}};
globalThis.ResizeObserver=class{observe(){}disconnect(){}};
globalThis.IntersectionObserver=class{observe(){}disconnect(){}};
const listeners=new Map();const host={clientWidth:600,clientHeight:520,appendChild(){},classList:{add(){},remove(){}},setPointerCapture(){},addEventListener(n,f){listeners.set(n,f)},removeEventListener(n){listeners.delete(n)}};
let source=await fs.readFile(new URL('../lib/diorama/viewer.ts',import.meta.url),'utf8');
source=source.replace("import * as T from 'three';",'const T=globalThis.__dioramaThree;').replace("import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';",'const GLTFLoader=globalThis.__dioramaLoader;').replace("import { WORLDS } from './catalog';",'const WORLDS='+JSON.stringify(slugs.map(slug=>({slug})))+';');
const js=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
const {createViewer}=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
let pauses=0;const states=[];const viewer=createViewer(host,s=>states.push(s),()=>pauses++);
const flush=()=>new Promise(r=>setImmediate(r));await flush();
const tick=(count=1)=>{for(let i=0;i<count;i++){time+=16;const tasks=[...scheduled.values()];scheduled.clear();tasks.forEach(fn=>fn(time))}};
tick();assert.equal(states.at(-1),'ready');
const lights=renderedScene.children.filter(o=>o.isLight);assert.equal(lights.length,1,'exactly one direct light');assert.equal(lights[0].shadow.intensity,.25,'all model shadows use 25 percent strength');assert.ok(lights[0].shadow.radius>=6,'shadow filter softens the edges');
const key=lights[0],lightPosition=key.position.clone(),turntable=renderedScene.children.find(o=>o.isGroup);
const initial=turntable.rotation.y;tick(60);assert.ok(turntable.rotation.y>initial+.05,'scene autoplays on arrival');
assert.deepEqual(key.position.toArray(),lightPosition.toArray(),'light stays fixed while scene rotates');assert.equal(key.parent,renderedScene);
viewer.pause(true);tick();const stopped=turntable.rotation.y;tick(60);assert.equal(turntable.rotation.y,stopped,'pause freezes rotation');
viewer.pause(false);tick(30);assert.ok(turntable.rotation.y>stopped,'play resumes motion');
listeners.get('pointerdown')({isPrimary:true,button:0,pointerId:1,clientX:100,clientY:100});
listeners.get('pointermove')({pointerId:1,clientX:160,clientY:120});tick();listeners.get('pointerup')();tick();
assert.equal(pauses,1,'drag informs the play/pause control');const dragged=turntable.rotation.y;tick(60);assert.equal(turntable.rotation.y,dragged,'drag leaves autoplay paused');
viewer.pause(false);tick(30);assert.ok(turntable.rotation.y>dragged,'explicit play resumes after drag');
await viewer.select(5);tick(100);const family=turntable.children.find(o=>o.visible);assert.ok(family.getObjectByName('WIFE'),'family transition completes');
viewer.pause(true);tick();const head=named(family,'HEAD'),rest=head.quaternion.clone();tick(90);assert.ok(head.quaternion.equals(rest),'pause also freezes character movement');
// A slower earlier load must never replace a later selection.
let resolveSlow;const promise=new Promise(r=>resolveSlow=r);deferred.set(2,{promise});
const slow=viewer.select(2);await viewer.select(3);resolveSlow({scene:models[2].clone(true)});await slow;tick(100);
assert.ok(turntable.children.find(o=>o.visible).getObjectByName('DIORAMA_events'),'latest selection wins');
viewer.dispose();assert.equal(scheduled.size,0,'dispose cancels animation');assert.equal(listeners.size,0,'dispose removes interactions');
reduced.matches=true;const accessibleViewer=createViewer(host,()=>{},()=>{});await flush();tick(60);const staticTurntable=renderedScene.children.find(o=>o.isGroup);assert.equal(staticTurntable.rotation.y,0,'reduced motion starts paused');accessibleViewer.pause(false);tick(30);assert.ok(staticTurntable.rotation.y>0,'explicit play works with reduced motion preference');accessibleViewer.dispose();
console.log('PASS: autoplay, fixed light, pause/play, drag takeover, six assets, transitions, selection races, reduced motion, cleanup.');
