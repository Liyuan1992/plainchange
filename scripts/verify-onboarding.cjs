const endpoint = process.argv[2];
const expectedUrl = process.argv[3];

if (!endpoint || !expectedUrl) {
  throw new Error("usage: node scripts/verify-onboarding.cjs <devtools-endpoint> <page-url>");
}

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function findPage() {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const targets = await fetch(`${endpoint}/json`).then((response) => response.json());
      const page = targets.find((item) => item.type === "page" && item.url === expectedUrl);
      if (page) return page;
    } catch (_) {
      // The browser may still be starting.
    }
    await delay(250);
  }
  throw new Error("onboarding page did not appear in the browser");
}

async function connect(webSocketDebuggerUrl) {
  const socket = new WebSocket(webSocketDebuggerUrl);
  const pending = new Map();
  const problems = [];
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
      if (message.error) callbacks.reject(new Error(message.error.message));
      else callbacks.resolve(message.result);
      return;
    }
    if (message.method === "Runtime.exceptionThrown" || message.method === "Log.entryAdded") {
      problems.push(message);
    }
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
  return { socket, send, problems };
}

async function evaluate(send) {
  const expression = `(() => ({
    title: document.title,
    brand: document.querySelector('.brand')?.textContent?.trim() || '',
    heading: document.querySelector('h1')?.textContent?.trim() || '',
    width: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    overflow: document.documentElement.scrollWidth > window.innerWidth,
    hasProjectInput: Boolean(document.querySelector('#repository-path')),
    hasAnalyzeAction: Boolean(document.querySelector('#analyze-button')),
    hasDirectApiKey: Boolean(document.querySelector('#model-api-key[type="password"]')),
    hasEnvironmentVariableField: Boolean(document.querySelector('#api-key-env'))
  }))()`;
  const result = await send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  if (result.exceptionDetails) throw new Error("browser evaluation failed");
  return result.result.value;
}

(async () => {
  const page = await findPage();
  const { socket, send, problems } = await connect(page.webSocketDebuggerUrl);
  await send("Runtime.enable");
  await send("Log.enable");
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", {
    width: 1280,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false,
  });
  const desktop = await evaluate(send);
  await send("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 1,
    mobile: true,
  });
  const narrow = await evaluate(send);
  socket.close();

  const checks = {
    title: desktop.title === "开始使用 · PlainChange",
    brand: desktop.brand.includes("PlainChange"),
    controls: desktop.hasProjectInput && desktop.hasAnalyzeAction && desktop.hasDirectApiKey && !desktop.hasEnvironmentVariableField,
    desktopOverflow: desktop.overflow,
    narrowOverflow: narrow.overflow,
    browserProblems: problems.length,
  };
  if (!checks.title || !checks.brand || !checks.controls || checks.desktopOverflow || checks.narrowOverflow || checks.browserProblems) {
    throw new Error(JSON.stringify({ checks, desktop, narrow, problems }, null, 2));
  }
  console.log(JSON.stringify({ ok: true, checks, desktop, narrow }, null, 2));
})().catch((error) => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
