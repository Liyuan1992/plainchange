"""Bounded offline Archify adapter. Does not analyze or execute target code.

Usage: python scripts/archify_pilot.py --report ... --profile ... --archify ... --output ...
The explicit profile authors presentation only; full source claims remain in evidence.json.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path


PIN = "9e35d2b0b39b155553ba9fcfe0b4f2a5198dd993"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def convert(report, profile):
    if report.get("schema_version") != "plainchange.system-flow.v2":
        raise ValueError("Unsupported report schema")
    flow = next(f for f in report["flows"] if f["id"] == profile["flow_id"])
    for kind in ("nodes", "edges"):
        ids = [x["id"] for x in flow[kind]]
        if len(ids) != len(set(ids)) or set(ids) != set(profile[kind]):
            raise ValueError(f"Profile must cover every {kind} ID exactly once")
        if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", x) for x in ids):
            raise ValueError("Unsafe ID")
    sources = {s["id"]: s for s in report["sources"]}
    def check_refs(value):
        if isinstance(value, dict):
            for ref in value.get("evidence", []):
                s = sources[ref["source_id"]]
                if not s["start_line"] <= ref["start_line"] <= ref["end_line"] <= s["end_line"]:
                    raise ValueError("Out-of-range citation")
            for v in value.values():
                check_refs(v)
        elif isinstance(value, list):
            for v in value:
                check_refs(v)
    check_refs(flow)
    node_ids = set(profile["nodes"])
    if any(e["from"] not in node_ids or e["to"] not in node_ids for e in flow["edges"]):
        raise ValueError("Dangling edge")
    connections = [c for c in report.get("connections", [])
                   if flow["id"] in (c["from_flow"], c["to_flow"])]
    review = report.get("product_review", {})
    check_refs(review)
    check_refs(connections)
    used = set()
    def collect(value):
        if isinstance(value, dict):
            if "source_id" in value:
                used.add(value["source_id"])
            for v in value.values():
                collect(v)
        elif isinstance(value, list):
            for v in value:
                collect(v)
    collect([flow, review, connections])
    evidence = {"commit": report["commit"], "report_title": report.get("title", flow["title"]), "flow": flow, "connections": connections,
                "coverage": report["coverage"], "unknowns": report["unknowns"],
                "product_review": review, "sources": [sources[k] for k in sorted(used)],
                "working_tree_excluded": report.get("working_tree_excluded"),
                "scope": "One full authored flow; cross-flow boundaries are listed separately. "
                         "Findings and unknowns are from the whole historical report, not new verification."}
    nodes = []
    for n in flow["nodes"]:
        p = profile["nodes"][n["id"]]
        allowed = {"lane", "col", "type", "width", "height", "yOffset"}
        if set(p) - allowed:
            raise ValueError("Node profile may only change presentation")
        nodes.append({**p, "id": n["id"], "label": n["title"]})
    edges = []
    for e in flow["edges"]:
        p = profile["edges"][e["id"]]
        allowed = {"label", "role", "variant", "route", "fromSide", "toSide", "channelX",
                   "channelY", "labelAt", "via", "bias", "labelDx", "labelDy"}
        if set(p) - allowed:
            raise ValueError("Edge profile cannot change IDs or topology")
        edges.append({**p, "id": e["id"], "from": e["from"], "to": e["to"]})
    graph = {"schema_version": 2, "diagram_type": "workflow",
             "meta": {"title": flow["title"], "locale": "zh-CN",
                      "quality_profile": "showcase", "legend": {"entries": {"backend": {"label": "索引处理步骤"}}}},
             "lanes": profile["lanes"], "mainPath": profile["mainPath"],
             "nodes": nodes, "edges": edges,
             "cards": [{"dot": "amber", "title": "固定版本 · 静态解释",
                        "items": [report["commit"][:12] + " · 不代表当前版本或运行结果",
                                  "连线为条件摘要；完整条件与源码见配套证据页"]}]}
    return graph, evidence


def render_evidence(evidence):
    esc = lambda v: html.escape(str(v))
    sources = {s["id"]: s for s in evidence["sources"]}
    def refs(item):
        parts = []
        for r in item.get("evidence", []):
            s = sources[r["source_id"]]
            lines = s.get("text", s.get("content", "")).splitlines()
            excerpt = "\n".join(f"{i}: {lines[i-s['start_line']]}" for i in
                                range(r["start_line"], r["end_line"]+1))
            parts.append(f'<details><summary>{esc(s["path"])}:{r["start_line"]}–{r["end_line"]}</summary>'
                         f'<pre>{esc(excerpt)}</pre></details>')
        return "".join(parts)
    labels = {"description": "说明", "inputs": "输入", "outputs": "输出", "state_changes": "状态变化",
              "condition": "完整条件", "explanation": "解释", "test_input": "候选测试输入",
              "expected_result": "预期结果（未执行）", "observation": "观察", "trigger": "触发条件",
              "impact": "可能影响", "uncertainty": "不确定性", "verification": "核查方法",
              "recommendation": "建议", "reason": "反证审阅理由"}
    flow = evidence["flow"]
    sections = []
    for kind in ("nodes", "edges"):
        for item in flow[kind]:
            key = item["id"]
            title = item.get("title", f'{item.get("from")} → {item.get("to")}')
            fragment = "focus" if kind == "nodes" else "relation"
            body = "".join(f'<dt>{label}</dt><dd>{esc(item[k])}</dd>' for k, label in labels.items() if k in item)
            sections.append(f'<article id="{key}"><h2>{esc(key)} · {esc(title)}</h2>'
                            f'<a target="diagram" href="diagram.html#{fragment}={key}">在图中定位</a>'
                            f'<p class="status">源码关联的模型解释 · 运行未验证 · 候选测试未执行</p>'
                            f'<dl>{body}</dl>{refs(item)}</article>')
    sections.append('<article id="boundaries"><h2>跨流程边界</h2><p>只显示原报告已有的连接；未把返回画成重新执行。</p>')
    for c in evidence["connections"]:
        sections.append(f'<h3>{esc(c["from_flow"])} / {esc(c["from_node"])} → '
                        f'{esc(c["to_flow"])} / {esc(c["to_node"])}</h3><p>{esc(c["kind"])} · '
                        f'{esc(c["condition"])}</p><p>{esc(c["explanation"])}</p>{refs(c)}')
    sections.append('</article><article id="findings"><h2>原报告疑点与反证</h2>'
                    '<p>以下来自整份历史报告，不都属于当前流程；未导入外层复现实验，不代表本轮已验证。</p>')
    for f in evidence["product_review"].get("findings", []):
        sections.append(f'<h3>{esc(f["id"])} · {esc(f["title"])}</h3><dl>' +
                        "".join(f'<dt>{label}</dt><dd>{esc(f[k])}</dd>' for k, label in labels.items() if k in f) +
                        f'</dl>{refs(f)}')
    for d in evidence["product_review"].get("challenge", {}).get("dispositions", []):
        sections.append(f'<h3>{esc(d["candidate_id"])} · {esc(d["decision"])}</h3><p>{esc(d["reason"])}</p>{refs(d)}')
    sections.append('</article><article id="unknowns"><h2>覆盖与未知</h2>')
    coverage = evidence["coverage"]
    sections.append(f'<p>原报告读取 {coverage["read_files"]}/{coverage["eligible_files"]} 个范围内文件；'
                    '不是业务覆盖率。本页仅转换一条已有流程，没有重新分析当前代码。</p><ul>')
    for u in evidence["unknowns"] + evidence["product_review"].get("not_covered", []):
        sections.append(f'<li>{esc(u)}</li>')
    sections.append('</ul></article>')
    nav = ''.join(f'<a href="#{x["id"]}">{esc(x["id"])} · {esc(x.get("title", x.get("condition", "")))}</a>'
                  for x in flow["nodes"] + flow["edges"])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>在线索引 · 条件与证据</title><style>
body{{margin:0;background:#f5f4ef;color:#242d3b;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}}
header{{padding:22px 32px;background:#173b48;color:white}}a{{color:#116778}}header a{{color:#bdeef0;margin-right:24px}}
main{{display:grid;grid-template-columns:250px minmax(0,900px);gap:28px;max-width:1220px;margin:28px auto;padding:0 24px}}
nav{{align-self:start;position:sticky;top:16px;max-height:92vh;overflow:auto}}nav a{{display:block;margin:8px 0;font-size:14px}}
article{{padding:24px;margin-bottom:20px;background:white;border:1px solid #dbe1e2;border-radius:12px;scroll-margin-top:20px}}
h2{{font-size:23px;margin:0 0 10px}}h3{{margin-top:28px}}dt{{font-weight:650}}dd{{margin:0 0 14px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.7 Consolas,monospace;background:#f3f5f7;padding:16px}}
summary{{cursor:pointer;overflow-wrap:anywhere}}.status{{color:#875a17;font-size:14px}}li{{margin-bottom:12px}}
@media(max-width:800px){{main{{display:block}}nav{{position:static;max-height:180px;margin-bottom:20px}}}}
</style><header><h1>{esc(flow['title'])}：完整条件与证据</h1><p>{esc(evidence['report_title'])} · {esc(evidence['commit'][:12])} · 输入报告静态解释</p>
<a target="diagram" href="diagram.html">打开交互图 ↗</a><a href="#findings">疑点与反证</a><a href="#unknowns">未知与覆盖</a><a href="evidence.json">完整数据</a></header>
<main><nav>{nav}<a href="#boundaries">跨流程边界</a></nav><div>{''.join(sections)}</div></main></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("report", "profile", "archify", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    for name in ("report", "profile", "archify", "output"):
        setattr(args, name, getattr(args, name).resolve())
    report_bytes = args.report.read_bytes()
    profile_bytes = args.profile.read_bytes()
    upstream = subprocess.check_output(["git", "-C", str(args.archify), "rev-parse", "HEAD"], text=True).strip()
    if upstream != PIN:
        raise SystemExit(f"Archify pin mismatch: expected {PIN}, got {upstream}")
    dirty = subprocess.check_output(["git", "-C", str(args.archify), "status", "--porcelain", "--untracked-files=no"], text=True)
    if dirty.strip():
        raise SystemExit("Pinned Archify checkout has tracked modifications")
    graph, evidence = convert(json.loads(report_bytes), json.loads(profile_bytes))
    args.output.mkdir(parents=True, exist_ok=True)
    spec = args.output / "diagram.workflow.json"
    write_json(spec, graph)
    cli = args.archify / "archify/bin/archify.mjs"
    for command in ("validate", "deliver"):
        cmd = ["node", str(cli), command, "workflow", str(spec)]
        if command == "deliver":
            cmd.append(str(args.output / "diagram.html"))
        result = subprocess.run(cmd + ["--quality", "showcase", "--json"], capture_output=True, text=True, encoding="utf-8")
        (args.output / f"{command}.json").write_text(result.stdout, encoding="utf-8")
        if result.returncode:
            print(result.stdout or result.stderr)
            raise SystemExit(result.returncode)
    write_json(args.output / "evidence.json", evidence)
    (args.output / "evidence.html").write_text(render_evidence(evidence), encoding="utf-8")
    links = ''.join(f'<li><a target="diagram" href="diagram.html#relation={e["id"]}">{html.escape(e["id"])} · '
                    f'{html.escape(e["condition"])}</a> · <a href="evidence.html#{e["id"]}">源码与候选测试</a></li>' for e in evidence["flow"]["edges"])
    (args.output / "index.html").write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>PlainChange × Archify · 在线索引维护</title><style>body{{margin:0;background:#f5f4ef;color:#243744;font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1000px;margin:50px auto;padding:0 24px}}h1{{font-size:36px}}a{{color:#086e7e}}.actions{{display:flex;gap:20px;margin:28px 0}}.actions a{{padding:14px 22px;border:1px solid #a6bfc5;border-radius:10px;background:white}}li{{margin:16px 0}}aside{{border-left:4px solid #b08033;padding:12px 20px;background:#fff9eb}}small{{color:#65727c}}</style>
<main><small>PLAINCHANGE × ARCHIFY · 本地接入试验</small><h1>{html.escape(evidence['flow']['title'])}</h1>
<p>{html.escape(evidence['report_title'])} · 共 {len(graph['nodes'])} 个步骤。</p>
<aside>输入报告版本：{html.escape(str(evidence['commit']))}。本轮只转换展示，没有运行目标项目，也没有重新判断疑点。</aside>
<div class="actions"><a target="diagram" href="diagram.html">打开交互流程图 ↗</a><a href="evidence.html">查看源码、疑点与未知</a></div>
<p>图上使用短条件；下面保留全部 {len(graph['edges'])} 条原始条件。点击条件可在图中定位，点击证据可查看源码和未执行的测试候选。</p>
<ol>{links}</ol><p>图由 Archify 生成，分析内容来自 PlainChange 的已有报告。<a href="receipt.json">接入回执</a> · <a href="ARCHIFY-LICENSE.txt">Archify MIT 许可</a></p></main></html>''', encoding="utf-8")
    (args.output / "ARCHIFY-LICENSE.txt").write_bytes((args.archify / "LICENSE").read_bytes())
    receipt = {"upstream_commit": upstream, "source_report_sha256": digest(report_bytes),
               "profile_sha256": digest(profile_bytes), "source_commit": evidence["commit"],
               "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
               "boundary_connections": len(evidence["connections"]),
               "full_conditions_preserved": True, "source_analysis_repeated": False,
               "target_code_executed": False, "human_acceptance": "pending",
               "diagram_sha256": digest((args.output / "diagram.html").read_bytes()),
               "evidence_sha256": digest((args.output / "evidence.json").read_bytes())}
    write_json(args.output / "receipt.json", receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
