const fs = require("fs");
const path = require("path");

const endpoint = "http://127.0.0.1:9237";
const outputDir = __dirname;

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function target() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const targets = await fetch(`${endpoint}/json`).then((response) => response.json());
      const page = targets.find((item) => item.type === "page" && item.url.includes("review.html"));
      if (page) return page;
    } catch (_) {
      // The browser may still be starting.
    }
    await delay(250);
  }
  throw new Error("Edge DevTools target did not become ready");
}

async function session(url) {
  const socket = new WebSocket(url);
  const pending = new Map();
  const events = [];
  let nextId = 0;
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message)); else resolve(message.result);
      return;
    }
    if (message.method === "Runtime.exceptionThrown" || message.method === "Log.entryAdded") {
      events.push(message);
    }
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
  return { socket, send, events };
}

async function evaluate(send, expression) {
  const result = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "evaluation failed");
  return result.result.value;
}

async function screenshot(send, filename) {
  const result = await send("Page.captureScreenshot", { format: "png", fromSurface: true, captureBeyondViewport: false });
  fs.writeFileSync(path.join(outputDir, filename), Buffer.from(result.data, "base64"));
}

(async () => {
  const page = await target();
  const { socket, send, events } = await session(page.webSocketDebuggerUrl);
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Log.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  await send("Page.reload", { ignoreCache: true });
  await delay(600);

  await evaluate(send, `document.querySelector('[data-page="architecture"]').click()`);
  await delay(400);
  const overview = await evaluate(send, `(() => ({
    activeTab: document.querySelector('[data-page="architecture"]').getAttribute('aria-selected'),
    depth: document.getElementById('owner-map-canvas').dataset.ownerMapDepth,
    nodeCount: document.querySelectorAll('#owner-map-nodes .owner-map-node').length,
    changedCount: document.querySelectorAll('#owner-map-nodes .owner-map-node.changed').length,
    relationOpen: document.querySelector('.owner-relation-disclosure').open,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
  }))()`);
  await screenshot(send, "architecture-overview-after.png");

  await evaluate(send, `document.querySelector('#owner-map-nodes .owner-map-node.changed').click()`);
  await delay(400);
  const detail = await evaluate(send, `(() => {
    const selected = document.querySelector('#owner-map-nodes .owner-map-node[aria-pressed="true"]');
    const inspector = document.getElementById('owner-map-inspector');
    return {
      depth: document.getElementById('owner-map-canvas').dataset.ownerMapDepth,
      nodeCount: document.querySelectorAll('#owner-map-nodes .owner-map-node').length,
      selectedChangeState: selected?.dataset.changeState,
      selectedHasChangedStyle: selected?.classList.contains('changed'),
      inspectorChangeState: inspector.dataset.changeState,
      inspectorHeading: inspector.querySelector('.eyebrow')?.textContent,
      inspectorChangeQuestion: [...inspector.querySelectorAll('.detail-row h3')].map((item) => item.textContent).find((text) => text.includes('改了')),
      canvasHorizontalOverflow: document.getElementById('owner-map-canvas').scrollWidth > document.getElementById('owner-map-canvas').clientWidth,
      canvasClientWidth: document.getElementById('owner-map-canvas').clientWidth,
      canvasScrollWidth: document.getElementById('owner-map-canvas').scrollWidth,
      svgWidth: document.getElementById('owner-map-links').getAttribute('width'),
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
    };
  })()`);
  await screenshot(send, "architecture-detail-after.png");

  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await send("Page.reload", { ignoreCache: true });
  await delay(600);
  const mobile = await evaluate(send, `(() => ({
    width: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    decisionCards: document.querySelectorAll('.owner-status-row').length,
    fullExplanationOpen: document.querySelector('.owner-full-explanation').open
  }))()`);
  await screenshot(send, "mobile-change-after.png");
  await evaluate(send, `document.querySelector('[data-page="architecture"]').click()`);
  await delay(350);
  const mobileArchitecture = await evaluate(send, `(() => ({
    width: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    depth: document.getElementById('owner-map-canvas').dataset.ownerMapDepth,
    nodeCount: document.querySelectorAll('#owner-map-nodes .owner-map-node').length,
    linksDisplay: getComputedStyle(document.getElementById('owner-map-links')).display
  }))()`);
  await screenshot(send, "mobile-architecture-after.png");

  console.log(JSON.stringify({ overview, detail, mobile, mobileArchitecture, consoleProblemCount: events.length }));
  socket.close();
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
