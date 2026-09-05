const path = require("path");
const { chromium } = require("playwright");

const reviewUrl = "http://127.0.0.1:8765/review.html";
const defaultPath = path.join(__dirname, "why-default.png");
const expandedPath = path.join(__dirname, "current-after.png");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const consoleProblems = [];
  const watchConsole = (page) => page.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) consoleProblems.push(message.text());
  });

  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  watchConsole(desktop);
  await desktop.goto(reviewUrl, { waitUntil: "load" });
  const detailsBefore = await desktop.locator("#summary-why-context").isVisible();
  await desktop.locator("#summary-grid").screenshot({ path: defaultPath });

  const toggle = desktop.getByRole("button", { name: "查看已有任务线索", exact: true });
  await toggle.click();
  const desktopEvidence = await desktop.evaluate(() => ({
    truthLabel: [...document.querySelectorAll(".summary-card")]
      .find((card) => card.querySelector("h2")?.textContent === "为什么这样改")
      ?.querySelector(".truth")?.textContent,
    actionCost: document.querySelector(".summary-context-cost")?.textContent,
    roles: [...document.querySelectorAll(".summary-context-entry strong")].map((node) => node.textContent),
    sources: [...document.querySelectorAll(".summary-context-entry-head span")].map((node) => node.textContent),
    warning: document.querySelector(".summary-context-warning")?.textContent,
    rule: document.querySelector(".summary-context-rule")?.textContent,
    expanded: document.querySelector(".summary-context-button")?.getAttribute("aria-expanded"),
  }));
  await desktop.locator("#summary-grid").screenshot({ path: expandedPath });
  await desktop.keyboard.press("Escape");
  const desktopEscape = await desktop.evaluate(() => ({
    expanded: document.querySelector(".summary-context-button")?.getAttribute("aria-expanded"),
    focusedLabel: document.activeElement?.textContent?.trim(),
  }));

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  watchConsole(mobile);
  await mobile.goto(reviewUrl, { waitUntil: "load" });
  await mobile.getByRole("button", { name: "查看已有任务线索", exact: true }).click();
  const mobileEvidence = await mobile.evaluate(() => ({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    panelColumns: getComputedStyle(document.querySelector(".summary-context-panel")).gridTemplateColumns,
    visibleEntries: [...document.querySelectorAll(".summary-context-entry")].filter((node) => {
      const style = getComputedStyle(node);
      return style.display !== "none" && style.visibility !== "hidden";
    }).length,
  }));

  await browser.close();
  console.log(JSON.stringify({
    detailsBefore,
    desktopEvidence,
    desktopEscape,
    mobileEvidence,
    consoleProblems,
    defaultPath,
    expandedPath,
  }));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

