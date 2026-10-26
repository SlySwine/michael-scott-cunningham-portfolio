'use client';
import {useEffect,useRef,useState,useId} from 'react';
import {ArrowLeft,ArrowRight,Pause,Play,RotateCcw} from 'lucide-react';
import {WORLDS} from '@/lib/diorama/catalog';
import type {createViewer} from '@/lib/diorama/viewer';

const ALT:Record<string,string>={
 ai:'Diorama of Michael at a dual-monitor desk, with a workflow diagram pinned on the wall behind him',
 photography:'Diorama of Michael shooting on a studio set with softbox lights, a seamless backdrop and a camera cart',
 'graphic-arts':'Diorama of Michael at a layout table with print proofs, color swatches and a sign on an easel',
 events:'Diorama of Michael on an event stage with lighting truss, speakers and a “Make it happen” banner',
 fabrication:'Diorama of Michael building a motorcycle on a lift in a fabrication shop',
 family:'Michael and his daughter working on a BMX outside a garage, with his wife helping',
};

export default function Diorama({initialIndex=0,selector=true}:{initialIndex?:number;selector?:boolean}){
 const container=useRef<HTMLDivElement>(null),host=useRef<HTMLDivElement>(null);
 const viewer=useRef<ReturnType<typeof createViewer>|null>(null),selection=useRef(initialIndex),motionPaused=useRef(false);
 const [index,setIndex]=useState(initialIndex),[status,setStatus]=useState<'ready'|'loading'|'error'>('loading'),[started,setStarted]=useState(false),[paused,setPaused]=useState(false);
 const statusId=useId();
 useEffect(()=>{
  let gone=false,initialized=false;
  const start=()=>{if(initialized||gone)return;initialized=true;
   import('@/lib/diorama/viewer').then(({createViewer})=>{
    if(gone||!host.current)return;
    try{viewer.current=createViewer(host.current,s=>{if(gone)return;setStatus(s);if(s==='ready')setStarted(true)},()=>{if(!gone){motionPaused.current=true;setPaused(true)}},selection.current,selector);
     motionPaused.current=window.matchMedia('(prefers-reduced-motion: reduce)').matches;setPaused(motionPaused.current);
    }catch{setStatus('error')}
   }).catch(()=>{if(!gone)setStatus('error')});
  };
  const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){start();observer.disconnect()}},{rootMargin:'180px'});
  if(container.current)observer.observe(container.current);
  return()=>{gone=true;observer.disconnect();viewer.current?.dispose();viewer.current=null};
 },[selector]);
 function change(value:unknown){const next=Number(value);if(!Number.isInteger(next)||next<0||next>=WORLDS.length)return;selection.current=next;setIndex(next);if(viewer.current)void viewer.current.select(next)}
 function toggleMotion(){motionPaused.current=!motionPaused.current;viewer.current?.pause(motionPaused.current);setPaused(motionPaused.current)}
 const disabled=!started||status==='error';
 const stage=<>
  <div className="world-stage" role="group" aria-label={`Interactive ${WORLDS[index].name} model`} aria-describedby={statusId}>
   <img src={'/dioramas/'+WORLDS[index].slug+'.webp'} alt={ALT[WORLDS[index].slug]} width="1100" height="1000" className={`world-poster ${started&&status!=='error'?'poster-hidden':''}`} loading={selector?'eager':'lazy'}/>
   <div className="world-canvas" ref={host} aria-hidden="true"/>
  </div>
  <div className="world-toolbar" role="group" aria-label="Model controls">
   <span className="world-title" aria-live="polite" aria-atomic="true">{WORLDS[index].name}</span>
   <div className="world-toolbar-actions">
    <button type="button" onClick={()=>selector?change((index+WORLDS.length-1)%WORLDS.length):viewer.current?.rotate(-1)} aria-label={selector?'Previous environment':'Rotate scene left'} title={selector?'Previous':'Rotate left'} disabled={!selector&&disabled}><ArrowLeft size={18}/></button>
    <button type="button" className="world-motion" aria-label={paused?'Play scene motion':'Pause scene motion'} title={paused?'Play':'Pause'} onClick={toggleMotion} disabled={disabled}>{paused?<Play size={17}/>:<Pause size={17}/>}</button>
    <button type="button" onClick={()=>selector?change((index+1)%WORLDS.length):viewer.current?.rotate(1)} aria-label={selector?'Next environment':'Rotate scene right'} title={selector?'Next':'Rotate right'} disabled={!selector&&disabled}><ArrowRight size={18}/></button>
    <button type="button" className="world-reset" onClick={()=>viewer.current?.reset()} aria-label="Reset scene view" title="Reset view" disabled={disabled}><RotateCcw size={15}/></button>
   </div>
  </div>
  <span id={statusId} className="sr-only" role="status">{status==='error'?'3D unavailable. A rendered image is shown.':status==='loading'?'':paused?'Motion paused. Drag to rotate or use the arrow controls.':'Scene slowly rotates. Dragging pauses motion.'}</span>
 </>;
 return <div ref={container} className={`diorama-experience ${selector?'with-selector':'single-model'} ${status==='error'?'world-render-error':''}`} style={{'--world-color':WORLDS[index].color} as React.CSSProperties}>
  {stage}
 </div>;
}
