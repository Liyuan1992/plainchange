from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
REVIEW_URL = "http://127.0.0.1:8772/fastapi-0.136.2-to-0.136.3/review.html"


GEOMETRY_SCRIPT = """
() => {
  const canvas = document.querySelector('#architecture-concept-canvas');
  const canvasRect = canvas.getBoundingClientRect();
  const cards = [...document.querySelectorAll('#architecture-concept-components .concept-component')].map((node) => {
    const rect = node.getBoundingClientRect();
    return {
      id: node.dataset.conceptId,
      row: Number(getComputedStyle(node).gridRowStart),
      left: rect.left - canvasRect.left + canvas.scrollLeft,
      right: rect.right - canvasRect.left + canvas.scrollLeft,
      top: rect.top - canvasRect.top + canvas.scrollTop,
      bottom: rect.bottom - canvasRect.top + canvas.scrollTop,
    };
  });
  const paths = [...document.querySelectorAll('#architecture-concept-links .architecture-concept-link')].map((node) => ({
    from: node.dataset.from,
    to: node.dataset.to,
    points: (node.getAttribute('d').match(/-?\\d+(?:\\.\\d+)?/g) || [])
      .map(Number)
      .reduce((result, value, index, values) => {
        if (index % 2 === 0) result.push({x: value, y: values[index + 1]});
        return result;
      }, []),
  }));
  const intersections = [];
  paths.forEach((flow) => flow.points.slice(1).forEach((point, index) => {
    const previous = flow.points[index];
    cards.forEach((card) => {
      if (card.id === flow.from || card.id === flow.to) return;
      const crosses = previous.y === point.y
        ? previous.y > card.top + 1 && previous.y < card.bottom - 1
          && Math.max(previous.x, point.x) > card.left + 1 && Math.min(previous.x, point.x) < card.right - 1
        : previous.x > card.left + 1 && previous.x < card.right - 1
          && Math.max(previous.y, point.y) > card.top + 1 && Math.min(previous.y, point.y) < card.bottom - 1;
      if (crosses) intersections.push(`${flow.from}->${flow.to}:${card.id}`);
    });
  }));
  const rows = [...new Set(cards.map((card) => card.row))].sort((left, right) => left - right);
  const rowTops = rows.map((row) => Math.min(...cards.filter((card) => card.row === row).map((card) => card.top)));
  return {
    cardCount: cards.length,
    pathCount: paths.length,
    relationCount: document.querySelectorAll('.architecture-concept-relation').length,
    rows,
    rowsProgressDown: rowTops.every((top, index) => index === 0 || top > rowTops[index - 1]),
    intersections: [...new Set(intersections)],
    canvasOverflowX: canvas.scrollWidth > canvas.clientWidth,
    layoutMode: canvas.dataset.conceptLayout,
  };
}
"""


def main() -> None:
    console_problems: list[str] = []
    with sync_playwright() as runner:
        browser = runner.chromium.launch(headless=True)
        desktop = browser.new_page(viewport={"width": 1440, "height": 1050})
        desktop.on(
            "console",
            lambda message: console_problems.append(message.text)
            if message.type in {"error", "warning"}
            else None,
        )
        desktop.goto(REVIEW_URL, wait_until="load")
        desktop.get_by_role("tab", name="整体架构").click()
        desktop_evidence = desktop.evaluate(GEOMETRY_SCRIPT)
        desktop.evaluate(
            "() => { document.querySelector('.topbar').style.position = 'static'; }"
        )
        desktop.locator("#architecture-concept").screenshot(
            path=ROOT / "current-after.png"
        )
        desktop.locator('[data-concept-id="application_routing"]').click()
        expanded = desktop.evaluate(
            """() => ({
              selectedNodes: [...document.querySelectorAll('.concept-component[aria-pressed="true"]')].map((node) => node.dataset.conceptId),
              expandedNodes: [...document.querySelectorAll('.concept-component[aria-expanded="true"]')].map((node) => node.dataset.conceptId),
              implementationVisible: !document.querySelector('#architecture-implementation').hidden,
              subdomainCount: document.querySelectorAll('.architecture-inline-subdomains .implementation-subdomain-card').length,
            })"""
        )
        desktop.locator('[data-concept-id="application_routing"]').click()
        collapsed = desktop.evaluate(
            """() => ({
              selectedNodeCount: document.querySelectorAll('.concept-component[aria-pressed="true"]').length,
              implementationVisible: !document.querySelector('#architecture-implementation').hidden,
            })"""
        )

        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.on(
            "console",
            lambda message: console_problems.append(message.text)
            if message.type in {"error", "warning"}
            else None,
        )
        mobile.goto(REVIEW_URL, wait_until="load")
        mobile.get_by_role("tab", name="整体架构").click()
        mobile.locator("#architecture-concept").screenshot(
            path=ROOT / "mobile-after.png"
        )
        mobile_evidence = mobile.evaluate(
            """() => ({
              viewport: window.innerWidth,
              scrollWidth: document.documentElement.scrollWidth,
              cardCount: document.querySelectorAll('.concept-component').length,
              relationCount: document.querySelectorAll('.architecture-concept-relation').length,
              connectorDisplay: getComputedStyle(document.querySelector('#architecture-concept-links')).display,
              columns: [...new Set([...document.querySelectorAll('.concept-component')].map((node) => getComputedStyle(node).gridColumnStart))],
            })"""
        )
        browser.close()

    print(
        json.dumps(
            {
                "desktopEvidence": desktop_evidence,
                "expanded": expanded,
                "collapsed": collapsed,
                "mobileEvidence": mobile_evidence,
                "consoleProblems": console_problems,
                "outputPath": str(ROOT / "current-after.png"),
                "mobileOutputPath": str(ROOT / "mobile-after.png"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
