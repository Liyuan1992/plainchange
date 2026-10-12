// Maintainer-only build; end users need neither Node nor an Archify checkout.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';
import { gzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
const pin = '9e35d2b0b39b155553ba9fcfe0b4f2a5198dd993';
const repo = path.resolve(process.argv[2] || '../archify');
if (execFileSync('git', ['-C', repo, 'rev-parse', 'HEAD'], {encoding:'utf8'}).trim() !== pin)
  throw new Error('Archify revision does not match pin');
if (execFileSync('git', ['-C', repo, 'status', '--porcelain', '--untracked-files=no'], {encoding:'utf8'}).trim())
  throw new Error('Archify checkout has tracked modifications');
const { applyTemplate } = await import(pathToFileURL(path.join(repo,'archify/renderers/shared/utils.mjs')));
const template = fs.readFileSync(path.join(repo,'archify/assets/template.html'),'utf8');
const compiled = applyTemplate(template, {title:'__PC_TITLE__', subtitle:'__PC_SUBTITLE__', svg:'__PC_SVG__', cards:'', locale:'zh-CN', visualPreset:'classic', guidedViews:[]});
const out = path.resolve('src/plainchange/assets');
fs.mkdirSync(out,{recursive:true});
const bytes = gzipSync(Buffer.from(compiled));
fs.writeFileSync(path.join(out,'archify-viewer.html.gz'),bytes);
fs.copyFileSync(path.join(repo,'LICENSE'),path.join(out,'ARCHIFY-LICENSE.txt'));
fs.writeFileSync(path.join(out,'archify-viewer.json'),JSON.stringify({repository:'https://github.com/tt-a1i/archify',revision:pin,sha256:createHash('sha256').update(bytes).digest('hex'),integration:'Compiled upstream viewer; PlainChange supplies SVG topology and evidence bridge. Not upstream renderer/showcase validation.'},null,2)+'\n');
console.log('Built bundled viewer:',bytes.length,'bytes');
