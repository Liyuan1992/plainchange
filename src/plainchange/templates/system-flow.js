(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("flow-data").textContent);
  const byId = id => document.getElementById(id);
  const el = (tag, text, parent) => { const item = document.createElement(tag); if (text !== undefined) item.textContent = text; if (parent) parent.append(item); return item; };
  const svgEl = (tag, attrs, parent) => { const item = document.createElementNS("http://www.w3.org/2000/svg", tag); Object.entries(attrs).forEach(([k,v]) => item.setAttribute(k, String(v))); if(parent) parent.append(item); return item; };
  const sources = new Map(data.sources.map(s => [s.id, s]));
  let current = data.flows[0], selectedNode = current.entry_node, selectedEdge = null, zoom = 1, baseWidth = 800;
  byId("title").textContent = data.title;
  byId("summary").textContent = data.summary;
  byId("version").textContent = `${data.project} · ${data.commit.slice(0,12)}`;
  byId("scope").textContent = `读取 ${data.coverage.read_files} / ${data.coverage.eligible_files} 个范围内文件 · ${data.coverage.read_excerpts} 段源码 · ${data.working_tree_excluded ? "项目有未提交修改，本图尚未包含" : "分析范围为所示提交"}`;
  byId("interview").textContent = data.interview_summary;
  byId("copy-summary").onclick = async () => { try { await navigator.clipboard.writeText(data.interview_summary); byId("copy-status").textContent = "已复制"; } catch { byId("copy-status").textContent = "浏览器未允许复制，请选中文字复制。"; } };
  byId("coverage").textContent = `共 ${data.coverage.tracked_files} 个受跟踪文件，${data.coverage.excluded_files} 个不在当前源码范围。引用和图连接校验不等于语义正确，也不证明已穷尽所有分支。`;
  data.unknowns.forEach(u => el("li", u, byId("unknowns")));
  byId("unread").textContent = data.coverage.unread_files.join("\n") || "范围内文件均有片段被读取；长文件仍可能只读取了一部分。";
  function evidence(items, parent) {
    items.forEach(ref => { const source = sources.get(ref.source_id), detail = el("details", undefined, parent);
      el("summary", `${source.path}:${ref.start_line}–${ref.end_line}`, detail);
      el("p", `固定提交 ${data.commit.slice(0,12)} · blob ${source.blob.slice(0,12)}`, detail).className = "muted";
      const lines = source.text.split("\n").slice(ref.start_line-source.start_line, ref.end_line-source.start_line+1);
      el("pre", lines.map((line,i) => `${ref.start_line+i}  ${line}`).join("\n"), detail);
    });
  }
  function field(parent, label, value) { const dl = el("dl", undefined, parent); el("dt", label, dl); el("dd", value, dl); }
  function inspectNode(id) {
    selectedNode = id; selectedEdge = null; draw();
    const node = current.nodes.find(n=>n.id===id), panel = byId("inspector"); panel.replaceChildren();
    el("span", "模型解读 · 运行未验证", panel).className = "badge";
    el("h2", node.title, panel); el("p", node.description, panel);
    field(panel, "输入", node.inputs); field(panel, "输出", node.outputs); field(panel, "数据与状态变化", node.state_changes);
    el("h3", "接下来会怎样？", panel);
    const outgoing = current.edges.filter(e=>e.from===id);
    outgoing.forEach(edge=>{ const button=el("button", `${edge.condition} → ${current.nodes.find(n=>n.id===edge.to).title}`, panel); button.onclick=()=>inspectEdge(edge.id); });
    const cross = links.filter(c=>c.from_flow===current.id && c.from_node===id);
    cross.forEach(c=>{const button=el("button",`${connectionKind(c)}：${c.condition} → ${flowById.get(c.to_flow).title}`,panel);button.onclick=()=>connectionDetail(c);});
    if (!outgoing.length && !cross.length) el("p", "此流程在这里结束；其他行为如无证据则未画出。", panel);
    el("h3", "代码依据", panel); evidence(node.evidence, panel);
    el("p", node.design_rationale, panel).className="muted";
  }
  function inspectEdge(id) {
    selectedEdge=id; selectedNode=null; draw();
    const edge=current.edges.find(e=>e.id===id), panel=byId("inspector"); panel.replaceChildren();
    el("span", "候选分支 · 测试未执行", panel).className="badge";
    el("h2", edge.condition, panel); el("p", edge.explanation, panel);
    field(panel, "触发输入 / 前置条件", edge.test_input); field(panel, "预期结果（待验证）", edge.expected_result);
    [edge.from,edge.to].forEach((nodeId,i)=>{const node=current.nodes.find(n=>n.id===nodeId);const button=el("button",`${i ? "去向" : "起点"}：${node.title}`,panel);button.onclick=()=>inspectNode(nodeId);});
    el("h3", "条件和处理的代码依据", panel); evidence(edge.evidence,panel);
    el("p", "代码存在此逻辑不代表该路径已实际运行。设计动机未提供独立记录。", panel).className="muted";
  }
  function accessibleClick(group, action, label) {
    group.setAttribute("tabindex","0");group.setAttribute("role","button");group.setAttribute("aria-label",label);
    group.addEventListener("click",action);group.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();action();}});
  }
  function draw() {
    const graph=byId("graph"); graph.replaceChildren();
    // Rank joins after their longest input path. Only cycle back edges are
    // excluded for ranking; every edge remains visible and selectable.
    const active=new Set(),done=new Set(),backEdges=new Set();
    function visit(id){active.add(id);current.edges.filter(e=>e.from===id).forEach(e=>{if(active.has(e.to))backEdges.add(e.id);else if(!done.has(e.to))visit(e.to);});active.delete(id);done.add(id);}
    visit(current.entry_node);
    const ranks=new Map(current.nodes.map(n=>[n.id,0])),incoming=new Map(current.nodes.map(n=>[n.id,0]));
    current.edges.filter(e=>!backEdges.has(e.id)).forEach(e=>incoming.set(e.to,incoming.get(e.to)+1));
    const queue=current.nodes.filter(n=>incoming.get(n.id)===0).map(n=>n.id);
    while(queue.length){const id=queue.shift();current.edges.filter(e=>e.from===id&&!backEdges.has(e.id)).forEach(e=>{ranks.set(e.to,Math.max(ranks.get(e.to),ranks.get(id)+1));incoming.set(e.to,incoming.get(e.to)-1);if(incoming.get(e.to)===0)queue.push(e.to);});}
    const rows=[]; current.nodes.forEach(n=>{const rank=ranks.get(n.id)||0;(rows[rank] ||= []).push(n);});
    const bodyWidth=Math.max(660,...rows.map(row=>row.length*320+80));
    const detours=current.edges.filter(e=>ranks.get(e.to)!==ranks.get(e.from)+1);
    baseWidth=bodyWidth+Math.max(40,detours.length*24+110);const height=rows.length*220+70;
    graph.setAttribute("viewBox",`0 0 ${baseWidth} ${height}`); graph.style.width=`${baseWidth*zoom}px`;graph.style.height=`${height*zoom}px`;
    const defs=svgEl("defs",{},graph), marker=svgEl("marker",{id:"arrow",viewBox:"0 0 10 10",refX:9,refY:5,markerWidth:6,markerHeight:6,orient:"auto-start-reverse"},defs);svgEl("path",{d:"M 0 0 L 10 5 L 0 10 z",fill:"#7893b5"},marker);
    const positions=new Map();rows.forEach((row,r)=>row.forEach((node,i)=>positions.set(node.id,{x:(bodyWidth-row.length*320)/2+i*320+50,y:r*220+35})));
    const labelBoxes=[];
    current.edges.forEach((edge,index)=>{
      const a=positions.get(edge.from),b=positions.get(edge.to),detour=detours.findIndex(e=>e.id===edge.id);
      let path,lx,ly;
      if(detour>=0){const rail=bodyWidth+35+detour*24,sy=a.y+85,ty=b.y;
        path=`M ${a.x+110} ${sy} L ${a.x+110} ${sy+28} L ${rail} ${sy+28} L ${rail} ${ty-24} L ${b.x+110} ${ty-24} L ${b.x+110} ${ty}`;
        lx=rail;ly=sy+56;
      } else {const sy=a.y+85,ty=b.y;path=`M ${a.x+110} ${sy} C ${a.x+110} ${(sy+ty)/2}, ${b.x+110} ${(sy+ty)/2}, ${b.x+110} ${ty}`;
        const fan=current.edges.filter(e=>e.from===edge.from).length>1;
        lx=(fan ? a.x*.2+b.x*.8 : a.x*.8+b.x*.2)+110;ly=sy+(ty-sy)*(fan?.65:.35);
      }
      svgEl("path",{d:path,class:`edge-path ${selectedEdge===edge.id?"edge-selected":""} ${trail.some(s=>s.flow===current.id&&s.via?.edge===edge.id)?"edge-walked":""}`,"marker-end":"url(#arrow)"},graph);
      const label=edge.condition.length>13?edge.condition.slice(0,12)+"…":edge.condition;const width=Math.max(64,label.length*11+16);
      lx=Math.max(width/2+4,Math.min(baseWidth-width/2-4,lx));
      const overlaps=(x,y)=>labelBoxes.some(r=>Math.abs(r.x-x)<(r.w+width)/2+5&&Math.abs(r.y-y)<30)||[...positions.values()].some(p=>x+width/2>p.x-4&&x-width/2<p.x+224&&y+13>p.y-4&&y-13<p.y+89);
      const originY=ly;for(const offset of [0,32,-32,64,-64,96,-96]){if(!overlaps(lx,originY+offset)){ly=originY+offset;break;}}
      labelBoxes.push({x:lx,y:ly,w:width});
      const group=svgEl("g",{class:"edge-label",transform:`translate(${lx},${ly})`},graph);svgEl("title",{},group).textContent=edge.condition;
      svgEl("rect",{x:-width/2,y:-13,width,height:26,rx:5},group);svgEl("text",{"text-anchor":"middle",y:4},group).textContent=label;
      accessibleClick(group,()=>inspectEdge(edge.id),`分支：${edge.condition}`);
    });
    const kinds={step:"处理步骤",decision:"条件判断",end:"流程结束",external:"外部边界"};
    current.nodes.forEach(node=>{const p=positions.get(node.id),group=svgEl("g",{class:`node ${node.kind} ${selectedNode===node.id?"selected":""}`,transform:`translate(${p.x},${p.y})`},graph);
      svgEl("rect",{width:220,height:85,rx:node.kind==="decision"?22:10},group);svgEl("text",{x:14,y:21,class:"kind"},group).textContent=kinds[node.kind];
      const title=node.title;[title.slice(0,15),title.slice(15,30)].filter(Boolean).forEach((t,i)=>svgEl("text",{x:14,y:44+i*20},group).textContent=t+(i===1&&title.length>30?"…":""));
      svgEl("title",{},group).textContent=node.title;accessibleClick(group,()=>inspectNode(node.id),`步骤：${node.title}`);
    });
  }
  function chooseFlow(flow, keepWalk = false) {
    if (!keepWalk) { trail = []; renderWalk(); }
    byId("overview").open = false;
    current=flow;zoom=1;selectedEdge=null;byId("flow-title").textContent=flow.title;byId("flow-purpose").textContent=flow.purpose;
    [...byId("flows").children].forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.id===flow.id)));
    byId("tests").replaceChildren();flow.edges.forEach(edge=>{const row=el("div",undefined,byId("tests"));row.className="test-row";
      const b=el("button",`${edge.condition} · 未执行`,row);b.onclick=()=>{inspectEdge(edge.id);byId("inspector").scrollIntoView({behavior:"smooth",block:"nearest"});};
      const input=el("div",undefined,row);el("strong","输入和前置条件",input);el("p",edge.test_input,input);
      const output=el("div",undefined,row);el("strong","预期结果（待验证）",output);el("p",edge.expected_result,output);
    });inspectNode(flow.entry_node);byId("graph-scroll").scrollTo(0,0);
  }
  data.flows.forEach(flow=>{const button=el("button",flow.title,byId("flows"));button.dataset.id=flow.id;button.onclick=()=>chooseFlow(flow);});
  byId("zoom-in").onclick=()=>{zoom=Math.min(1.8,zoom+.15);draw();};
  byId("zoom-out").onclick=()=>{zoom=Math.max(.3,zoom-.15);draw();};
  byId("zoom-reset").onclick=()=>{zoom=Math.max(.3,Math.min(1,byId("graph-scroll").clientWidth/baseWidth));draw();};
  const links = data.connections || [];
  const flowById = new Map(data.flows.map(f => [f.id, f]));
  let trail = [], planned = [];
  const scenarios = [];
  function shortestPath(flow, destination) {
    const queue = [{node: flow.entry_node, edges: []}], seen = new Set();
    while(queue.length) {
      const next = queue.shift();
      if(next.node === destination) return next.edges;
      if(seen.has(next.node)) continue;
      seen.add(next.node);
      flow.edges.filter(e => e.from === next.node).forEach(e => queue.push({node: e.to, edges: [...next.edges, e.id]}));
    }
    return null;
  }
  data.flows.forEach(flow => flow.edges.forEach(edge => {
    const path = shortestPath(flow, edge.from);
    if(path === null) return;
    scenarios.push({flow, edge, path: [...path, edge.id]});
    const option = el("option", `${flow.title} · ${edge.condition}`, byId("scenario"));
    option.value = String(scenarios.length - 1);
  }));
  byId("scenario").onchange = () => {
    const scenario=scenarios[Number(byId("scenario").value)];
    byId("scenario-description").textContent=scenario ? `候选输入：${scenario.edge.test_input}；预期：${scenario.edge.expected_result}。沿途前置条件需逐项核对。` : "暂无可推演分支。";
  };
  byId("scenario").onchange();
  function arrive(flow, node, via) {
    trail.push({flow: flow.id, node, via});
    chooseFlow(flow, true); inspectNode(node); renderWalk();
    const selected = byId("graph").querySelector(".node.selected");
    if(selected) {
      const scroll=byId("graph-scroll"), nodeBox=selected.getBoundingClientRect(), box=scroll.getBoundingClientRect();
      scroll.scrollTo({top:scroll.scrollTop+nodeBox.top-box.top-30,left:Math.max(0,scroll.scrollLeft+nodeBox.left-box.left-30)});
    }
  }
  function followEdge(edge) {
    const here = trail[trail.length-1];
    if(planned[0] === edge.id) planned.shift(); else planned = [];
    arrive(flowById.get(here.flow), edge.to, {edge: edge.id, text: edge.condition, input: edge.test_input, result: edge.expected_result});
  }
  function renderWalk() {
    const actions = byId("walk-actions"), list = byId("walk-trail"); actions.replaceChildren(); list.replaceChildren();
    if(!trail.length) { byId("walk-status").textContent = "选择一个分支，逐步查看它需要的前置条件。推演不会执行项目或测试。"; return; }
    trail.forEach((step, i) => {
      const flow = flowById.get(step.flow), node = flow.nodes.find(n => n.id === step.node);
      const button = el("button", `${i+1}. ${flow.title} / ${node.title}`, list);
      button.onclick = () => { trail = trail.slice(0,i+1); planned = []; chooseFlow(flow,true); inspectNode(node.id); renderWalk(); };
    });
    const here = trail[trail.length-1], flow = flowById.get(here.flow), node = flow.nodes.find(n => n.id === here.node);
    byId("walk-status").textContent = `第 ${trail.length} 步：${node.title} · 条件由你选择，实际能否到达尚未运行验证。`;
    if(here.via) { el("p", `刚才的条件：${here.via.text}`, actions); if(here.via.input) el("p", `输入：${here.via.input}；预期：${here.via.result}`, actions); }
    flow.edges.filter(e => e.from === node.id).forEach(edge => {
      const button = el("button", `${planned[0] === edge.id ? "沿所选场景继续：" : "如果："}${edge.condition} → ${flow.nodes.find(n=>n.id===edge.to).title}`, actions);
      button.onclick = () => followEdge(edge);
    });
    links.filter(c => c.from_flow === flow.id && c.from_node === node.id).forEach(c => {
      const button = el("button", `${connectionKind(c)}：${c.condition} → ${flowById.get(c.to_flow).title}`, actions);
      button.onclick = () => { planned = []; arrive(flowById.get(c.to_flow), c.to_node, {text: `${connectionKind(c)} · ${c.condition}`}); };
    });
    if(!flow.edges.some(e=>e.from===node.id) && !links.some(c=>c.from_flow===flow.id && c.from_node===node.id)) el("p", "已到本图的证据边界。其他后续行为尚未建立连接。", actions);
    const back = el("button", "退回一步", actions); back.disabled = trail.length < 2;
    back.onclick = () => { trail.pop(); planned=[]; const prev=trail[trail.length-1]; chooseFlow(flowById.get(prev.flow),true); inspectNode(prev.node); renderWalk(); };
  }
  function connectionKind(c) { return {call:"本次调用",return:"返回上层",next_request:"等待下一轮请求"}[c.kind]; }
  byId("start-scenario").onclick = () => {
    const scenario = scenarios[Number(byId("scenario").value)]; if(!scenario) return;
    trail=[]; planned=[...scenario.path]; arrive(scenario.flow,scenario.flow.entry_node,null);
  };
  function connectionDetail(c) {
    chooseFlow(flowById.get(c.from_flow)); inspectNode(c.from_node);
    const panel=byId("inspector"); el("h3", connectionKind(c), panel); el("p",c.condition,panel); el("p",c.explanation,panel); evidence(c.evidence,panel);
    const button=el("button",`进入：${flowById.get(c.to_flow).title}`,panel);
    button.onclick=()=>{chooseFlow(flowById.get(c.to_flow));inspectNode(c.to_node);};
    panel.scrollIntoView({block:"nearest"});
  }
  const overview=svgEl("svg",{viewBox:`0 0 ${Math.max(660,450+links.length*22)} ${data.flows.length*105+30}`,role:"img","aria-label":"系统模块与跨流程连接"},byId("overview-map"));
  const pos=new Map(data.flows.map((f,i)=>[f.id,{x:20,y:15+i*105}]));
  links.forEach((c,i)=>{
    const a=pos.get(c.from_flow),b=pos.get(c.to_flow), rail=390+i*22;
    svgEl("path",{d:`M ${a.x+340} ${a.y+25} H ${rail} V ${b.y+50} H ${b.x+344}`,fill:"none",stroke:c.kind==="next_request"?"#b17713":"#9aafca","stroke-dasharray":c.kind==="next_request"?"5 4":"none"},overview);
    svgEl("text",{x:b.x+339,y:b.y+55,fill:"#34527a"},overview).textContent="◀";
    const button=el("button",`${i+1}. ${flowById.get(c.from_flow).title} → ${flowById.get(c.to_flow).title} · ${connectionKind(c)} · ${c.condition}`,byId("overview-links"));
    button.onclick=()=>connectionDetail(c);
  });
  data.flows.forEach(flow=>{
    const p=pos.get(flow.id),group=svgEl("g",{transform:`translate(${p.x},${p.y})`},overview);
    svgEl("rect",{width:340,height:70,rx:10,fill:"#edf3ff",stroke:"#7893b5"},group);
    [flow.title.slice(0,21),flow.title.slice(21)].filter(Boolean).forEach((text,i)=>svgEl("text",{x:12,y:29+i*23,fill:"#182c44","font-size":15},group).textContent=text);
    accessibleClick(group,()=>{chooseFlow(flow);byId("flow-title").scrollIntoView({block:"start"});},`展开流程：${flow.title}`);
  });
  if(!links.length) el("p","这份报告尚无已建立的跨流程连接；模块排列不表示执行顺序。",byId("overview-links"));
  const gaps=el("details",undefined,byId("overview")); el("summary",`还没弄清的环节（${data.unknowns.length}）`,gaps); const gapList=el("ul",undefined,gaps); data.unknowns.forEach(u=>el("li",u,gapList));
  chooseFlow(current);
  byId("overview").open = true;
})();
