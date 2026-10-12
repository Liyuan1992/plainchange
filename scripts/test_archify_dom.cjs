// DOM simulation only, not a browser or visual acceptance test.
// npm install --prefix artifacts/archify-dom-tests jsdom@30.1.2 --no-audit --no-fund
// node scripts/test_archify_dom.cjs path/to/review.html
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('../artifacts/archify-dom-tests/node_modules/jsdom');
const dom = new JSDOM(fs.readFileSync(process.argv[2], 'utf8'), {runScripts:'outside-only', url:'https://example.invalid/report'});
const w=dom.window, d=w.document;
w.HTMLElement.prototype.scrollIntoView=function(){};
w.HTMLElement.prototype.scrollTo=function(){};
const raw=JSON.parse(d.getElementById('flow-data').textContent);
const original=JSON.stringify(raw);
w.eval(d.scripts[d.scripts.length-1].textContent);
const frame=d.getElementById('archify-flow');
function content(f){return new JSDOM(f.srcdoc).window.document;}
function token(f){return f.srcdoc.match(/const token="(\d+)"/)[1];}
function message(f,kind,id,source=f.contentWindow,t=token(f)){
  w.dispatchEvent(new w.MessageEvent('message',{source,data:{channel:'plainchange-archify',token:t,kind,id}}));
}
const overview=d.getElementById('archify-overview');
assert.equal(content(overview).querySelectorAll('[data-node-id]').length,raw.flows.length);
for(const flow of raw.flows){
  const b=Array.from(d.getElementById('flows').children).find(x=>x.dataset.id===flow.id);b.click();
  const graph=content(frame);
  assert.deepEqual(new Set(Array.from(graph.querySelectorAll('[data-node-id]'),x=>x.dataset.nodeId)),new Set(flow.nodes.map(n=>n.id)));
  assert.deepEqual(new Set(Array.from(graph.querySelectorAll('[data-edge-id]'),x=>x.dataset.edgeId)),new Set(flow.edges.map(e=>e.id)));
  for(const node of flow.nodes){message(frame,'node',node.id);assert.equal(d.querySelector('#inspector h2').textContent,node.title);}
  for(const edge of flow.edges){message(frame,'edge',edge.id);assert.equal(d.querySelector('#inspector h2').textContent,edge.condition);assert.ok(d.getElementById('inspector').textContent.includes(edge.expected_result));}
  const before=d.getElementById('inspector').innerHTML;
  message(frame,'node',flow.entry_node,{},token(frame));
  message(frame,'node',flow.entry_node,frame.contentWindow,'old-token');
  message(frame,'node','unknown-id');
  assert.equal(d.getElementById('inspector').innerHTML,before,'untrusted/stale messages must not change evidence');
}
message(overview,'node',raw.flows[0].id);
assert.equal(d.getElementById('flow-title').textContent,raw.flows[0].title);
for(const link of raw.connections||[]){message(overview,'edge',link.id);assert.ok(d.getElementById('inspector').textContent.includes(link.explanation));}
d.getElementById('basic-view').click();assert.equal(frame.hidden,true);
d.getElementById('basic-view').click();assert.equal(frame.hidden,false);
assert.equal(JSON.stringify(JSON.parse(d.getElementById('flow-data').textContent)),original);
console.log(JSON.stringify({status:'passed',kind:'DOM simulation, not browser/visual proof',flows:raw.flows.length,nodes:raw.flows.reduce((n,f)=>n+f.nodes.length,0),edges:raw.flows.reduce((n,f)=>n+f.edges.length,0),messageIsolation:true,sourceDataUnchanged:true}));
dom.window.close();
