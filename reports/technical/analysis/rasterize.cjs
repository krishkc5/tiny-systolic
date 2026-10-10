const fs=require('fs'),path=require('path');
const sharp=require('/Users/krishnachemudupati/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{const dir=path.resolve(__dirname,'../figures');for(const file of fs.readdirSync(dir).filter(x=>x.endsWith('.svg'))){await sharp(path.join(dir,file),{density:240}).png().toFile(path.join(dir,file.replace('.svg','.png')));}})();
