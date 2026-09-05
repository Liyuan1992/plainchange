const path = require("path");
const { chromium } = require("playwright");

const reviewUrl = "http://127.0.0.1:8765/review.html";
const outputPath = path.join(__dirname, "current-after.png");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const consoleProblems = [];
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  desktop.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) consoleProblems.push(message.text());
  });
  await desktop.goto(reviewUrl, { waitUntil: "load" });
  await desktop.getByRole("tab", { name: "整体架构" }).click();
  await desktop.getByRole("button", { name: /用户入口与交互/ }).click();
  await desktop.waitForTimeout(2300);
  await desktop.screenshot({ path: outputPath, fullPage: false });

  const desktopEvidence = await desktop.evaluate(() => ({
    focusRelationCards: document.querySelectorAll(".architecture-focus-relation").length,
    visibleLines: document.querySelectorAll(".architecture-link.incoming, .architecture-link.outgoing").length,
    selectedHeading: document.querySelector(".architecture-focus-center h3")?.textContent,
  }));

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mobile.goto(reviewUrl, { waitUntil: "load" });
  await mobile.getByRole("tab", { name: "整体架构" }).click();
  await mobile.getByRole("button", { name: /用户入口与交互/ }).click();
  const mobileEvidence = await mobile.evaluate(() => ({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    linkLayerDisplay: getComputedStyle(document.getElementById("architecture-links")).display,
    focusColumns: getComputedStyle(document.querySelector(".architecture-focus-map")).gridTemplateColumns,
  }));

  await browser.close();
  console.log(JSON.stringify({ desktopEvidence, mobileEvidence, consoleProblems, outputPath }));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
