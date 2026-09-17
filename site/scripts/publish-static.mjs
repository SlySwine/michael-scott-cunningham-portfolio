import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..','..');
const build=path.join(root,'site','dist','client');
if(!fs.existsSync(path.join(build,'index.html')))throw Error('Run npm run build first');
for(const entry of fs.readdirSync(build)){
 if(entry.startsWith('.'))continue;
 fs.cpSync(path.join(build,entry),path.join(root,entry),{recursive:true});
}
console.log('Static site copied to the GitHub Pages root.');
