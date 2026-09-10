from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from change_passport.html_renderer import render_review_html
from change_passport.models import canonical_json_bytes, sha256_bytes


ROOT = Path(__file__).parent
ARTIFACT = ROOT.parents[3] / "artifacts" / "change-passport-self-688fc5f"
URL = "http://127.0.0.1:8767/review.html"


def write_fixture(name: str, flows: list[dict[str, str]], cycle: bool = False) -> str:
    model = json.loads((ARTIFACT / "beginner-review.json").read_text(encoding="utf-8"))
    conceptual = model["conceptual_architecture"]
    conceptual.update(
        {
            "title": "多分支项目的可读架构",
            "description": "用多个输入、分支、汇合和人工决定检验通用布局。",
            "boundary_note": "这是测试配置声明的概念关系，不是运行时调用图。",
            "components": [
                {"id": "code", "type": "input", "label": "代码变化", "description": "范围输入。", "grid_column": 1, "grid_row": 1, "implementation_groups": []},
                {"id": "task", "type": "input", "label": "任务说明", "description": "意图输入。", "grid_column": 1, "grid_row": 2, "implementation_groups": []},
                {"id": "collect", "type": "process", "label": "证据采集", "description": "固定事实。", "grid_column": 2, "grid_row": 1, "implementation_groups": []},
                {"id": "structure", "type": "process", "label": "结构提取", "description": "分析结构。", "grid_column": 3, "grid_row": 1, "implementation_groups": []},
                {"id": "quality", "type": "process", "label": "质量校验", "description": "分析边界。", "grid_column": 3, "grid_row": 2, "implementation_groups": []},
                {"id": "merge", "type": "process", "label": "合并说明", "description": "汇合结论。", "grid_column": 4, "grid_row": 1, "implementation_groups": []},
                {"id": "report", "type": "output", "label": "可读报告", "description": "输出解释。", "grid_column": 5, "grid_row": 1, "implementation_groups": []},
                {"id": "review", "type": "human_gate", "label": "人工复核", "description": "人工决定。", "grid_column": 6, "grid_row": 1, "implementation_groups": []},
                {"id": "approve", "type": "human_gate", "label": "人工批准", "description": "人工决定。", "grid_column": 6, "grid_row": 2, "implementation_groups": []},
                {"id": "baseline", "type": "state", "label": "可复用基线", "description": "持久状态。", "grid_column": 7, "grid_row": 1, "implementation_groups": []},
            ],
            "flows": flows,
        }
    )
    destination = ARTIFACT / name
    identity_source = dict(model)
    identity_source.pop("review_identity", None)
    model["review_identity"] = sha256_bytes(canonical_json_bytes(identity_source))
    destination.write_text(render_review_html(model), encoding="utf-8")
    return f"http://127.0.0.1:8767/{name}"


def desktop_evidence(page: object) -> dict[str, object]:
    return page.evaluate(
        """() => {
          const concept = document.getElementById("architecture-concept");
          const implementation = document.getElementById("architecture-implementation");
          const cards = [...document.querySelectorAll(".concept-component")];
          const cardRects = cards.map((card) => {
            const rect = card.getBoundingClientRect();
            return {left: rect.left + 5, right: rect.right - 5, top: rect.top + 5, bottom: rect.bottom - 5};
          });
          const blockedConnectorCount = [...document.querySelectorAll(".architecture-concept-link")].filter((path) => {
            const svgRect = path.ownerSVGElement.getBoundingClientRect();
            const length = path.getTotalLength();
            for (let index = 1; index < 80; index += 1) {
              const point = path.getPointAtLength((length * index) / 80);
              const x = svgRect.left + point.x * svgRect.width / path.ownerSVGElement.viewBox.baseVal.width;
              const y = svgRect.top + point.y * svgRect.height / path.ownerSVGElement.viewBox.baseVal.height;
              if (cardRects.some((rect) => x > rect.left && x < rect.right && y > rect.top && y < rect.bottom)) return true;
            }
            return false;
          }).length;
          const canvas = document.getElementById("architecture-concept-canvas");
          const bandHeaderBottom = Math.max(...[...document.querySelectorAll(".architecture-story-band small")]
            .map((node) => node.getBoundingClientRect().bottom));
          const firstCardTop = Math.min(...cards.map((card) => card.getBoundingClientRect().top));
          return {
            conceptVisible: Boolean(concept && !concept.hidden),
            componentCount: cards.length,
            flowCount: document.querySelectorAll(".architecture-concept-link").length,
            floatingLabelCount: document.querySelectorAll(".architecture-concept-label").length,
            relationCount: document.querySelectorAll(".architecture-concept-relation").length,
            bandCount: document.querySelectorAll(".architecture-story-band").length,
            layoutMode: canvas.dataset.conceptLayout,
            layoutStatus: document.getElementById("architecture-concept-layout-status").textContent,
            layoutStatusHidden: document.getElementById("architecture-concept-layout-status").hidden,
            blockedConnectorCount,
            canvasClientWidth: canvas.clientWidth,
            canvasScrollWidth: canvas.scrollWidth,
            bandHeadersClearCards: bandHeaderBottom <= firstCardTop,
            pageSwitchToastHidden: document.getElementById("toast").hidden,
            conceptBeforeImplementation: concept.getBoundingClientRect().top < implementation.getBoundingClientRect().top,
          };
        }"""
    )


with sync_playwright() as runner:
    flows = [
        {"from": "code", "to": "collect", "label": "范围"},
        {"from": "task", "to": "collect", "label": "意图"},
        {"from": "collect", "to": "structure", "label": "提取"},
        {"from": "collect", "to": "quality", "label": "校验"},
        {"from": "structure", "to": "merge", "label": "结构结论"},
        {"from": "quality", "to": "merge", "label": "质量结论"},
        {"from": "merge", "to": "report", "label": "编写"},
        {"from": "report", "to": "review", "label": "提交复核"},
        {"from": "report", "to": "approve", "label": "提交批准"},
        {"from": "review", "to": "baseline", "label": "确认"},
        {"from": "approve", "to": "baseline", "label": "批准"},
    ]
    complex_url = write_fixture("complex-layout.fixture.html", flows)
    cycle_url = write_fixture("cycle-layout.fixture.html", flows + [{"from": "baseline", "to": "collect", "label": "反馈"}], cycle=True)
    browser = runner.chromium.launch(headless=True)
    console_problems: list[str] = []
    desktop = browser.new_page(viewport={"width": 1440, "height": 1050})
    desktop.on("console", lambda message: console_problems.append(message.text) if message.type in {"error", "warning"} else None)
    desktop.goto(URL, wait_until="load")
    desktop.get_by_role("tab", name="整体架构").click()
    desktop.screenshot(path=ROOT / "current-after.png", full_page=False)
    desktop_data = desktop_evidence(desktop)

    complex_page = browser.new_page(viewport={"width": 1440, "height": 1050})
    complex_page.on("console", lambda message: console_problems.append(message.text) if message.type in {"error", "warning"} else None)
    complex_page.goto(complex_url, wait_until="load")
    complex_page.get_by_role("tab", name="整体架构").click()
    complex_page.screenshot(path=ROOT / "complex-layout.png", full_page=False)
    complex_data = desktop_evidence(complex_page)

    cycle_page = browser.new_page(viewport={"width": 1440, "height": 1050})
    cycle_page.on("console", lambda message: console_problems.append(message.text) if message.type in {"error", "warning"} else None)
    cycle_page.goto(cycle_url, wait_until="load")
    cycle_page.get_by_role("tab", name="整体架构").click()
    cycle_data = desktop_evidence(cycle_page)

    mobile = browser.new_page(viewport={"width": 390, "height": 844})
    mobile.on("console", lambda message: console_problems.append(message.text) if message.type in {"error", "warning"} else None)
    mobile.goto(URL, wait_until="load")
    mobile.get_by_role("tab", name="整体架构").click()
    mobile.locator("#architecture-concept-canvas").scroll_into_view_if_needed()
    mobile.screenshot(path=ROOT / "mobile-after.png", full_page=False)
    mobile_data = mobile.evaluate(
        """() => ({
          innerWidth: window.innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          linkDisplay: getComputedStyle(document.getElementById("architecture-concept-links")).display,
          bandDisplay: getComputedStyle(document.querySelector(".architecture-story-band")).display,
          componentOrder: [...document.querySelectorAll(".concept-component h4")].map((node) => node.textContent),
        })"""
    )
    browser.close()
    print(json.dumps({"desktop": desktop_data, "complex": complex_data, "cycle": cycle_data, "mobile": mobile_data, "console_problems": console_problems}, ensure_ascii=False))
