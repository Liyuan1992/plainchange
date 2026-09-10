const path = require("path");
const { chromium } = require("playwright");

const reviewUrl = "http://127.0.0.1:8766/review.html";
const outputPath = path.join(__dirname, "current-after.png");
const mobileOutputPath = path.join(__dirname, "mobile-after.png");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const consoleProblems = [];
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  desktop.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) consoleProblems.push(message.text());
  });
  await desktop.goto(reviewUrl, { waitUntil: "load" });
  await desktop.getByRole("tab", { name: "整体架构" }).click();
  await desktop.screenshot({ path: outputPath, fullPage: false });
  const desktopEvidence = await desktop.evaluate(() => {
    const concept = document.getElementById("architecture-concept");
    const implementation = document.getElementById("architecture-implementation");
    const componentLabels = [...document.querySelectorAll(".concept-component h4")]
      .map((node) => node.textContent);
    return {
      conceptVisible: Boolean(concept && !concept.hidden),
      componentCount: document.querySelectorAll(".concept-component").length,
      flowCount: document.querySelectorAll(".architecture-concept-link").length,
      relationCount: document.querySelectorAll(".architecture-concept-relation").length,
      conceptBeforeImplementation: concept.getBoundingClientRect().top < implementation.getBoundingClientRect().top,
      componentLabels,
      boundary: document.getElementById("architecture-concept-boundary")?.textContent,
      implementationHeading: implementation.querySelector("h3")?.textContent,
    };
  });
  await desktop.locator(".concept-implementation-button").first().click();
  const drillEvidence = await desktop.evaluate(() => ({
    selectedStaticGroup: document.querySelector(".system-group[aria-selected='true'] .system-group-title")?.textContent,
    staticInspector: document.querySelector("#architecture-inspector h3")?.textContent,
  }));

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) consoleProblems.push(message.text());
  });
  await mobile.goto(reviewUrl, { waitUntil: "load" });
  await mobile.getByRole("tab", { name: "整体架构" }).click();
  await mobile.screenshot({ path: mobileOutputPath, fullPage: false });
  const mobileEvidence = await mobile.evaluate(() => ({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    conceptColumns: getComputedStyle(document.getElementById("architecture-concept-components")).gridTemplateColumns,
    conceptLinksDisplay: getComputedStyle(document.getElementById("architecture-concept-links")).display,
  }));
  await browser.close();
  console.log(JSON.stringify({ desktopEvidence, drillEvidence, mobileEvidence, consoleProblems, outputPath, mobileOutputPath }));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
