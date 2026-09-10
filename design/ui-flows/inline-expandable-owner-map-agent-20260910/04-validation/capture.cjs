const fs = require("fs");
const path = require("path");

const endpoint = "http://127.0.0.1:9241";
const outputDir = __dirname;
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function target() {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      const targets = await fetch(`${endpoint}/json`).then((response) => response.json());
      const page = targets.find((item) => item.type === "page" && item.url.includes("review.html"));
      if (page) return page;
    } catch (_) {
      // Edge may still be starting.
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
      const callbacks = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) callbacks.reject(new Error(message.error.message)); else callbacks.resolve(message.result);
      return;
    }
    if (message.method === "Runtime.exceptionThrown" || message.method === "Log.entryAdded") events.push(message);
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

const snapshotExpression = `(() => {
  const canvas = document.getElementById('owner-map-canvas');
  const inspector = document.getElementById('owner-map-inspector');
  const selectedDetail = document.querySelector('.owner-inline-detail[aria-pressed="true"]');
  return {
    state: canvas.dataset.ownerMapState,
    overviewCount: document.querySelectorAll('#owner-map-nodes > .owner-map-overview-group').length,
    overviewButtonCount: document.querySelectorAll('#owner-map-nodes > .owner-map-overview-group > .owner-map-node').length,
    expandedCount: document.querySelectorAll('.owner-map-overview-group.expanded').length,
    inlinePanelCount: document.querySelectorAll('.owner-map-inline-details').length,
    inlineDetailCount: document.querySelectorAll('.owner-inline-detail').length,
    globalLinkCount: document.querySelectorAll('#owner-map-links .owner-map-link').length,
    collapseHidden: document.getElementById('owner-map-back').hidden,
    selectedDetailId: selectedDetail?.dataset.ownerDetailId || null,
    selectedDetailState: selectedDetail?.dataset.changeState || null,
    inspectorState: inspector.dataset.changeState || null,
    inspectorHeading: inspector.querySelector('.eyebrow')?.textContent || null,
    documentOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    canvasOverflow: canvas.scrollWidth > canvas.clientWidth
  };
})()`;

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
  await delay(450);
  const initial = await evaluate(send, snapshotExpression);
  await screenshot(send, "desktop-overview.png");

  await evaluate(send, `document.querySelector('#owner-map-nodes > .owner-map-overview-group > .owner-map-node.changed').click()`);
  await delay(450);
  const expanded = await evaluate(send, snapshotExpression);
  await screenshot(send, "desktop-inline-expanded.png");

  await evaluate(send, `document.querySelector('.owner-map-overview-group.expanded > .owner-map-node').click()`);
  await delay(350);
  const collapsed = await evaluate(send, snapshotExpression);

  await evaluate(send, `document.querySelector('#owner-map-nodes > .owner-map-overview-group:not(:has(.owner-map-node.changed)) > .owner-map-node').click()`);
  await delay(400);
  const switched = await evaluate(send, snapshotExpression);
  await screenshot(send, "desktop-inline-switched.png");

  await evaluate(send, `document.querySelector('.owner-implementation-disclosure').open = true`);
  await delay(1200);
  const technical = await evaluate(send, `(() => ({
    statusHidden: document.getElementById('technical-payload-status').hidden,
    statusText: document.getElementById('technical-payload-status').textContent,
    groupCount: document.querySelectorAll('#architecture-group-map .architecture-group-node').length
  }))()`);

  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await send("Page.reload", { ignoreCache: true });
  await delay(600);
  await evaluate(send, `document.querySelector('[data-page="architecture"]').click()`);
  await delay(300);
  await evaluate(send, `document.querySelector('#owner-map-nodes > .owner-map-overview-group > .owner-map-node.changed').click()`);
  await delay(350);
  const narrow = await evaluate(send, snapshotExpression);
  const narrowLinksDisplay = await evaluate(send, `getComputedStyle(document.getElementById('owner-map-links')).display`);
  await screenshot(send, "narrow-inline-expanded.png");

  console.log(JSON.stringify({ initial, expanded, collapsed, switched, technical, narrow: {...narrow, linksDisplay: narrowLinksDisplay}, consoleProblemCount: events.length }));
  socket.close();
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
