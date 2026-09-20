// Local browser acceptance; no model request is made by this script.
const fs = require("node:fs");
const path = require("node:path");
const {pathToFileURL} = require("node:url");
const {spawn} = require("node:child_process");
const [report, onboardingUrl, outputDirectory] = process.argv.slice(2);
if (!report) throw new Error("usage: node scripts/verify-system-flow.cjs <review.html> [onboarding-url] [output-directory]");
const output = path.resolve(outputDirectory || "artifacts/system-flow-browser");
fs.mkdirSync(output, {recursive:true});
const profile = path.join(output, `edge-${Date.now()}`);
const executable = process.env.PLAINCHANGE_TEST_BROWSER || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const browser = spawn(executable,["--headless=new","--disable-gpu","--no-first-run","--remote-debugging-port=0",`--user-data-dir=${profile}`,"about:blank"],{windowsHide:true,stdio:"ignore"});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let socket;
(async()=>{
  const portFile=path.join(profile,"DevToolsActivePort");
  for(let i=0;i<100&&!fs.existsSync(portFile);i++) await delay(100);
  const port=fs.readFileSync(portFile,"utf8").split("\n")[0];
  const targets=await fetch(`http://127.0.0.1:${port}/json`).then(r=>r.json());
  socket=new WebSocket(targets.find(t=>t.type==="page").webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  const pending=new Map(),errors=[];let seq=0;
  socket.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==="Runtime.exceptionThrown")errors.push(m.params);};
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));});
  const evaluate=async expression=>{const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  await send("Runtime.enable");await send("Page.enable");
  async function navigate(url,ready){await send("Page.navigate",{url});for(let i=0;i<100;i++){if(await evaluate(ready))return;await delay(100);}throw new Error("Page did not become ready");}
  const checks=[];
  for(const width of [1440,390]){
    await send("Emulation.setDeviceMetricsOverride",{width,height:1000,deviceScaleFactor:1,mobile:width<500});
    await navigate(pathToFileURL(path.resolve(report)).href,"Boolean(document.querySelector('.node'))");
    const result=await evaluate(`(() => {
      const count=document.querySelectorAll('.node').length;
      document.querySelectorAll('.node')[1].dispatchEvent(new MouseEvent('click',{bubbles:true}));
      const nodeSelected=document.querySelectorAll('.node.selected').length===1;
      const nodeDetail=document.getElementById('inspector').textContent.includes('输入');
      document.querySelector('.edge-label').dispatchEvent(new MouseEvent('click',{bubbles:true}));
      const branch=document.getElementById('inspector').textContent.includes('预期结果');
      const evidence=document.querySelector('#inspector details'); evidence.open=true;
      const code=Boolean(evidence.querySelector('pre').textContent.trim());
      const tests=document.querySelectorAll('.test-row').length;
      const buttons=[...document.querySelectorAll('#flows button')];
      const layoutProblems=[];
      buttons.forEach(b=>{b.click();const labels=[...document.querySelectorAll('.edge-label rect')].map(e=>e.getBoundingClientRect());
        const nodes=[...document.querySelectorAll('.node rect')].map(e=>e.getBoundingClientRect());
        const overlaps=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1;
        labels.forEach((a,i)=>{if(labels.slice(i+1).some(b=>overlaps(a,b))||nodes.some(b=>overlaps(a,b)))layoutProblems.push(b.textContent+':'+i);});
      });buttons[0].click();
      return {count,nodeSelected,nodeDetail,branch,code,tests,flows:buttons.length,layoutProblems,overflow:document.documentElement.scrollWidth>innerWidth};
    })()`);
    if(!result.count||!result.nodeSelected||!result.nodeDetail||!result.branch||!result.code||!result.tests||result.overflow||result.layoutProblems.length)throw new Error(JSON.stringify(result));
    const journey=await evaluate(`(() => {
      const data=JSON.parse(document.getElementById('flow-data').textContent);
      const start=document.getElementById('start-scenario'); start.click();
      const initial=document.querySelectorAll('#walk-trail button').length;
      const forward=[...document.querySelectorAll('#walk-actions button')].find(b=>b.textContent.startsWith('沿所选场景继续'));
      if(!forward) throw new Error('missing scenario forward action'); forward.click();
      const advanced=document.querySelectorAll('#walk-trail button').length;
      const marked=Boolean(document.querySelector('.edge-walked'));
      [...document.querySelectorAll('#walk-actions button')].find(b=>b.textContent==='退回一步').click();
      const restored=document.querySelectorAll('#walk-trail button').length;
      const overview=document.getElementById('overview');overview.open=true;
      const modules=document.querySelectorAll('#overview-map [role=button]').length;
      const links=document.querySelectorAll('#overview-links button');
      let crossFlow=true;
      if(links.length){links[0].click();const enter=[...document.querySelectorAll('#inspector button')].find(b=>b.textContent.startsWith('进入：')); if(!enter)throw new Error('missing cross-flow action');enter.click();crossFlow=document.getElementById('flow-title').textContent===data.flows.find(f=>f.id===data.connections[0].to_flow).title;}
      let requestBoundary = null;
      const boundary=(data.connections||[]).find(c=>c.kind==='next_request'&&data.flows.find(f=>f.id===c.from_flow).edges.some(e=>e.to===c.from_node));
      if(boundary){
        let index=0,selected=-1;
        data.flows.forEach(f=>f.edges.forEach(e=>{if(selected<0&&f.id===boundary.from_flow&&e.to===boundary.from_node)selected=index;index++;}));
        document.getElementById('scenario').value=String(selected);start.click();
        for(let i=0;i<40;i++){const step=[...document.querySelectorAll('#walk-actions button')].find(b=>b.textContent.startsWith('沿所选场景继续'));if(!step)break;step.click();}
        const next=[...document.querySelectorAll('#walk-actions button')].find(b=>b.textContent.startsWith('等待下一轮请求：'+boundary.condition));
        if(!next)throw new Error('missing next-request boundary');next.click();
        requestBoundary=document.getElementById('flow-title').textContent===data.flows.find(f=>f.id===boundary.to_flow).title;
        [...document.querySelectorAll('#walk-actions button')].find(b=>b.textContent==='退回一步').click();
        requestBoundary=requestBoundary&&document.getElementById('flow-title').textContent===data.flows.find(f=>f.id===boundary.from_flow).title;
      }
      return {initial,advanced,restored,marked,modules,crossFlow,requestBoundary};
    })()`);
    if(journey.initial!==1||journey.advanced!==2||journey.restored!==1||!journey.marked||journey.modules!==result.flows||!journey.crossFlow||journey.requestBoundary===false)throw new Error(JSON.stringify(journey));
    checks.push({width,journey});
    const reader = await evaluate(`(() => {
      const data=JSON.parse(document.getElementById('flow-data').textContent), review=data.product_review;
      if(!review) return {legacy:true,hidden:document.getElementById('reader-review')?.hidden ?? true};
      const cards=document.querySelectorAll('#reader-guide article');
      const disclosure=cards[0].querySelector('details');disclosure.open=true;
      const source=disclosure.querySelector('details');source.open=true;
      const citedCode=Boolean(source.querySelector('pre').textContent.trim());
      disclosure.open=false;
      const journey=document.querySelectorAll('#reader-journey article');
      const routes=[...journey].every((card,index)=>{card.querySelector('button').click();return document.getElementById('flow-title').textContent===data.flows.find(f=>f.id===review.journey[index].flow_id).title;});
      const findings=[...document.querySelectorAll('#finding-list>.finding')];
      const actionable=findings.every(card=>{card.open=true;const text=card.textContent;const valid=text.includes('何时发生')&&text.includes('为什么还不能确定')&&text.includes('如何核查（未执行）')&&Boolean(card.querySelector('pre'));card.open=false;return valid;});
      const reviewHistory=!review.challenge||document.getElementById('product-findings').textContent.includes('反证审阅记录');
      return {legacy:false,cards:cards.length,citedCode,journey:journey.length,routes,findings:findings.length,expectedFindings:review.findings.length,actionable,reviewHistory,overflow:document.documentElement.scrollWidth>innerWidth};
    })()`);
    if(reader.legacy ? !reader.hidden : reader.cards!==5||!reader.citedCode||!reader.routes||!reader.actionable||!reader.reviewHistory||reader.findings!==reader.expectedFindings||reader.overflow)throw new Error(JSON.stringify(reader));
    checks.push({width,reader});
    await evaluate("window.scrollTo(0,0);document.getElementById('overview').open=true");
    const screenshot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(output,`map-${width}.png`),Buffer.from(screenshot.data,"base64"));
    await evaluate(`(() => { const buttons=[...document.querySelectorAll('#flows button')]; (buttons[2]||buttons[0]).click();document.querySelector('.workspace').scrollIntoView(); })()`);
    const deep=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(output,`map-detail-${width}.png`),Buffer.from(deep.data,"base64"));
    checks.push({width,map:result});
    if (onboardingUrl && onboardingUrl !== "-") {
    await navigate(onboardingUrl,"Boolean(document.querySelector('#system-mode'))");
    const entry=await evaluate(`(() => {document.getElementById('system-mode').click();const system=!document.getElementById('system-workspace').hidden&&document.getElementById('change-workspace').hidden;document.getElementById('change-mode').click();const old=!document.getElementById('change-workspace').hidden;document.getElementById('system-mode').click();return {system,old,overflow:document.documentElement.scrollWidth>innerWidth};})()`);
    if(!entry.system||!entry.old||entry.overflow)throw new Error(JSON.stringify(entry));
    await delay(500);
    const screenshot2=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(output,`entry-${width}.png`),Buffer.from(screenshot2.data,"base64"));
    checks.push({width,entry});
    }
  }
  if(errors.length)throw new Error(JSON.stringify(errors));
  fs.writeFileSync(path.join(output,"checks.json"),JSON.stringify({checks,browserErrors:errors},null,2));
  console.log(JSON.stringify({ok:true,checks,browserErrors:errors}));
  await send("Browser.close").catch(()=>{});
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{if(socket)socket.close();browser.kill();});
