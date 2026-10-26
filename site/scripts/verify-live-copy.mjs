import fs from 'node:fs';
import assert from 'node:assert/strict';
const decode=s=>s.replace(/&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi,(_,v)=>v[0]==='#'?String.fromCodePoint(v[1].toLowerCase()==='x'?parseInt(v.slice(2),16):Number(v.slice(1))):({amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '})[v.toLowerCase()]);
function copy(html){
 const body=html.match(/<body[^>]*>([\s\S]*?)<\/body>/i)?.[1]??html;
 const cleaned=body.replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi,'').replace(/<!--[\s\S]*?-->/g,'');
 const stack=[],chunks=[];const voids=new Set('area base br col embed hr img input link meta param source track wbr'.split(' '));
 for(const token of cleaned.match(/<[^>]*>|[^<]+/g)||[]){
  if(token.startsWith('</')){const tag=token.match(/^<\/([^\s>]+)/)?.[1];let i=stack.length-1;while(i>=0&&stack[i].tag!==tag)i--;if(i>=0)stack.length=i;continue;}
  if(token.startsWith('<')){const tag=token.match(/^<([^\s/>]+)/)?.[1];if(!tag||token.startsWith('<!'))continue;
   const ignored=stack.at(-1)?.ignored||/aria-hidden="true"|\bhidden(?:\s|=|>)/.test(token)||/class(?:Name)?="[^"]*\b(diorama-experience|sr-only)\b/.test(token);
   if(!voids.has(tag)&&!token.endsWith('/>'))stack.push({tag,ignored});continue;
  }
  if(!stack.at(-1)?.ignored)chunks.push(decode(token));
 }
 return chunks.join(' ').replace(/©\s*\d{4}/g,'©').replace(/\s+/g,' ').trim();
}
// User-approved changes: Instagram contact link, Email and Résumé links (Oct 2026), and revised Live experiences copy.
const original=copy(fs.readFileSync('content/live-site-2026-09-17.html','utf8')).replace(/ X ©/, ' X Instagram ©').replace('See the work LinkedIn','See the work LinkedIn Résumé').replace('all of them. LinkedIn','all of them. Email Résumé LinkedIn').replace("Strategy that survives contact with reality.","Make it happen. Then open the doors.").replace("A live activation has to look right, feel right, arrive on time, fit the space, satisfy compliance, and work when the doors open.","The idea is the beginning. Getting it into the room is the work.").replace("That is where creative direction and operations become the same job: concept, visual system, production, staging, vendors, logistics, installation, content capture, and the inevitable last-minute fix.","I connect the creative side of an event with the practical side: the visuals, vendors, print, staging, logistics, and content capture. There’s always a detail that needs solving before the doors open.");
const revised=copy(fs.readFileSync(process.argv[2]||'/private/tmp/portfolio-copy-check.html','utf8'));
if(original!==revised){let i=0;while(original[i]===revised[i]&&i<original.length)i++;console.error('First difference near:',{original:original.slice(Math.max(0,i-80),i+180),revised:revised.slice(Math.max(0,i-80),i+180)});}
assert.equal(revised,original,'All original page copy must remain unchanged and in order, excluding non-editorial model controls and the dynamic copyright year.');
console.log(`PASS: ${original.split(' ').length} words match the live-site copy plus the explicitly approved edits.`);
