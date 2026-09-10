const fs = require("fs");
const path = require("path");

const endpoint = "http://127.0.0.1:9242";
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

const measure = `(() => {
  const rows = [...document.querySelectorAll('.owner-question-affected_people .owner-audience-row')];
  const explanations = rows.map((row) => row.querySelector('.owner-audience-explanation'));
  return {
    viewport: innerWidth,
    documentOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    rowCount: rows.length,
    rowWidths: rows.map((row) => Math.round(row.getBoundingClientRect().width)),
    rowHeights: rows.map((row) => Math.round(row.getBoundingClientRect().height)),
    explanationWidths: explanations.map((item) => Math.round(item.getBoundingClientRect().width)),
    explanationHeights: explanations.map((item) => Math.round(item.getBoundingClientRect().height)),
    verticalStrip: explanations.some((item) => item.getBoundingClientRect().width < 120 && item.getBoundingClientRect().height > item.getBoundingClientRect().width * 1.5),
    affectedCardHeight: Math.round(document.querySelector('.owner-question-affected_people').getBoundingClientRect().height),
    softwareCardHeight: Math.round(document.querySelector('.owner-question-software_operation').getBoundingClientRect().height),
    primaryColumnGap: Math.round(document.querySelector('.owner-question-current_change').getBoundingClientRect().top - document.querySelector('.owner-question-software_operation').getBoundingClientRect().bottom),
    secondaryColumnGap: Math.round(document.querySelector('.owner-question-unknowns').getBoundingClientRect().top - document.querySelector('.owner-question-affected_people').getBoundingClientRect().bottom)
  };
})()`;

async function captureAt(send, width, height, filename) {
  await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width <= 720 });
  await send("Page.reload", { ignoreCache: true });
  await delay(550);
  await evaluate(send, `(() => {
    const details = document.querySelector('.owner-full-explanation');
    details.open = true;
    details.scrollIntoView({block: 'start'});
    window.scrollBy(0, -72);
  })()`);
  await delay(350);
  const result = await evaluate(send, measure);
  await screenshot(send, filename);
  return result;
}

(async () => {
  const page = await target();
  const { socket, send, events } = await session(page.webSocketDebuggerUrl);
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Log.enable");
  const desktop = await captureAt(send, 1560, 1165, "current-after.png");
  const intermediate = await captureAt(send, 1100, 900, "intermediate-after.png");
  const narrow = await captureAt(send, 390, 844, "narrow-after.png");
  console.log(JSON.stringify({ desktop, intermediate, narrow, consoleProblemCount: events.length }));
  socket.close();
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
