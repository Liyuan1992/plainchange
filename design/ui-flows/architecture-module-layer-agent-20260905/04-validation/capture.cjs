const path = require("path");
const { chromium } = require("playwright");

const reviewUrl = "http://127.0.0.1:8765/review.html";
const outputPath = path.join(__dirname, "current-after.png");

async function openModuleLayer(page, groupLabel) {
  const groupButton = page.locator(".system-group").filter({ hasText: groupLabel }).first();
  await groupButton.click();
  await page.getByRole("button", { name: "查看这个分区的内部结构", exact: true }).click();
  await page.locator("#architecture-modules").scrollIntoViewIfNeeded();
}

async function closeModuleLayer(page) {
  await page.getByRole("button", { name: "返回分区关系图", exact: true }).click();
  await page.getByRole("button", { name: "返回全部分区关系", exact: true }).click();
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const consoleProblems = [];
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  desktop.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) consoleProblems.push(message.text());
  });
  await desktop.goto(reviewUrl, { waitUntil: "load" });
  await desktop.getByRole("tab", { name: "整体架构", exact: true }).click();
  await openModuleLayer(desktop, "用户入口与交互");
  await desktop.waitForTimeout(2300);
  await desktop.locator("#architecture-modules").screenshot({ path: outputPath });

  const desktopDefault = await desktop.evaluate(() => {
    const host = document.querySelector("#architecture-modules");
    return {
      areaCount: host.querySelectorAll(".module-area-card").length,
      areaModuleSum: Array.from(host.querySelectorAll(".module-area-card"))
        .reduce((total, item) => total + Number(item.dataset.areaCount || 0), 0),
      rawModuleCount: host.querySelectorAll(".module-card").length,
      sourcePathsVisible: host.innerText.includes("src/digital_self"),
      stepLabels: Array.from(host.querySelectorAll(".module-layer-step strong"))
        .map((item) => item.textContent.trim()),
    };
  });

  await desktop.getByRole("button", { name: /网页功能界面/ }).click();
  const desktopSelectedArea = await desktop.evaluate(() => ({
    selectedArea: document.querySelector(".module-area-card[aria-pressed='true'] strong")?.textContent.trim(),
    rawModuleCount: document.querySelectorAll("#architecture-modules .module-card").length,
    toggleText: document.querySelector(".module-detail-toggle")?.textContent.trim(),
    summaryFacts: Array.from(document.querySelectorAll(".module-area-facts .fact"))
      .map((item) => item.innerText.trim().replace(/\n+/g, ": ")),
  }));
  await desktop.getByRole("button", { name: "展开技术模块（可选）", exact: true }).click();
  const desktopTechnical = await desktop.evaluate(() => ({
    rawModuleCount: document.querySelectorAll("#architecture-modules .module-card").length,
    moreText: document.querySelector("#architecture-modules .module-more")?.textContent.trim(),
  }));
  await desktop.keyboard.press("Escape");
  const afterFirstEscape = await desktop.evaluate(() => ({
    rawModuleCount: document.querySelectorAll("#architecture-modules .module-card").length,
    selectedArea: document.querySelector(".module-area-card[aria-pressed='true'] strong")?.textContent.trim(),
  }));
  await desktop.keyboard.press("Escape");
  const afterSecondEscape = await desktop.evaluate(() => ({
    selectedAreaCount: document.querySelectorAll(".module-area-card[aria-pressed='true']").length,
    moduleLayerVisible: !document.querySelector("#architecture-modules").hidden,
  }));

  await closeModuleLayer(desktop);
  const groupLabels = [
    "用户入口与交互",
    "Agent 与执行核心",
    "记忆与知识系统",
    "能力与工具",
    "上下文与自主控制",
    "工作与项目协作",
    "数据与基础设施",
    "测试与质量保障",
    "工程、评测与交付",
  ];
  const groupCensus = [];
  for (const label of groupLabels) {
    await openModuleLayer(desktop, label);
    groupCensus.push(await desktop.evaluate((groupLabel) => {
      const host = document.querySelector("#architecture-modules");
      return {
        group: groupLabel,
        areas: host.querySelectorAll(".module-area-card").length,
        moduleSum: Array.from(host.querySelectorAll(".module-area-card"))
          .reduce((total, item) => total + Number(item.dataset.areaCount || 0), 0),
        rawModules: host.querySelectorAll(".module-card").length,
      };
    }, label));
    await closeModuleLayer(desktop);
  }

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) consoleProblems.push(`mobile: ${message.text()}`);
  });
  await mobile.goto(reviewUrl, { waitUntil: "load" });
  await mobile.getByRole("tab", { name: "整体架构", exact: true }).click();
  await openModuleLayer(mobile, "用户入口与交互");
  const mobileEvidence = await mobile.evaluate(() => ({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    areaColumns: getComputedStyle(document.querySelector(".module-area-grid")).gridTemplateColumns,
    stepColumns: getComputedStyle(document.querySelector(".module-layer-steps")).gridTemplateColumns,
    areas: document.querySelectorAll(".module-area-card").length,
    rawModules: document.querySelectorAll("#architecture-modules .module-card").length,
  }));

  await browser.close();
  console.log(JSON.stringify({
    desktopDefault,
    desktopSelectedArea,
    desktopTechnical,
    afterFirstEscape,
    afterSecondEscape,
    groupCensus,
    mobileEvidence,
    consoleProblems,
    outputPath,
  }, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
