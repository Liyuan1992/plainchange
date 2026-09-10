const path = require("path");
const { chromium } = require("playwright");

const reviewUrl = "http://127.0.0.1:8767/review.html";
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
    const cards = [...document.querySelectorAll(".concept-component")];
    const blockers = [...document.querySelectorAll(".architecture-concept-link")].filter((line) => {
      const box = line.getBoundingClientRect();
      return cards.some((card) => {
        const cardBox = card.getBoundingClientRect();
        return box.left < cardBox.right && box.right > cardBox.left && box.top < cardBox.bottom && box.bottom > cardBox.top;
      });
    }).length;
    return {
      conceptVisible: Boolean(concept && !concept.hidden),
      componentCount: cards.length,
      flowCount: document.querySelectorAll(".architecture-concept-link").length,
      floatingLabelCount: document.querySelectorAll(".architecture-concept-label").length,
      relationCount: document.querySelectorAll(".architecture-concept-relation").length,
      bandCount: document.querySelectorAll(".architecture-story-band").length,
      conceptBeforeImplementation: concept.getBoundingClientRect().top < implementation.getBoundingClientRect().top,
      blockers,
      componentLabels: cards.map((card) => card.querySelector("h4")?.textContent),
    };
  });
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
    conceptLinksDisplay: getComputedStyle(document.getElementById("architecture-concept-links")).display,
    bandDisplay: getComputedStyle(document.querySelector(".architecture-story-band")).display,
  }));
  await browser.close();
  console.log(JSON.stringify({ desktopEvidence, mobileEvidence, consoleProblems, outputPath, mobileOutputPath }));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
