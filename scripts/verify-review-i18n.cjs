const endpoint = process.argv[2];
const pageUrl = process.argv[3];

if (!endpoint || !pageUrl) {
  throw new Error("usage: node scripts/verify-review-i18n.cjs <devtools-endpoint> <page-url>");
}

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));

async function pageTarget() {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const targets = await fetch(`${endpoint}/json`).then(response => response.json());
      const target = targets.find(item => item.type === "page");
      if (target) return target;
    } catch (_) {}
    await delay(200);
  }
  throw new Error("review page did not appear");
}

async function connection(target) {
  const socket = new WebSocket(target.webSocketDebuggerUrl);
  const pending = new Map();
  const problems = [];
  let nextId = 0;
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, {once: true});
    socket.addEventListener("error", reject, {once: true});
  });
  socket.addEventListener("message", event => {
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
    pending.set(id, {resolve, reject});
    socket.send(JSON.stringify({id, method, params}));
  });
  return {socket, send, problems};
}

async function evaluate(send, expression) {
  const result = await send("Runtime.evaluate", {expression, returnByValue: true, awaitPromise: true});
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}

async function waitReady(send, expected) {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    let value;
    try {
      value = await evaluate(send, `(() => ({
      ready: document.documentElement?.dataset?.i18nReady || null,
      locale: document.documentElement.lang,
      title: document.title,
      changeTab: document.querySelector('#change-tab')?.textContent?.trim(),
      architectureTab: document.querySelector('#architecture-tab')?.textContent?.trim(),
      activeButtons: document.querySelectorAll('#language-switch button.active').length,
      supportedButtons: document.querySelectorAll('#language-switch button[data-locale]').length,
      stored: (() => { try { return localStorage.getItem('plainchange.review.language'); } catch (_) { return null; } })(),
      width: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      overflow: document.documentElement.scrollWidth > window.innerWidth
    }))()`);
    } catch (_) {
      await delay(100);
      continue;
    }
    if (value.ready === "true" && value.locale === expected) return value;
    await delay(100);
  }
  throw new Error(`locale ${expected} did not become ready`);
}

(async () => {
  const target = await pageTarget();
  const {socket, send, problems} = await connection(target);
  await send("Runtime.enable");
  await send("Log.enable");
  await send("Page.enable");
  await send("Network.enable");
  await send("Emulation.setDeviceMetricsOverride", {width: 1280, height: 900, deviceScaleFactor: 1, mobile: false});

  await evaluate(send, `localStorage.removeItem('plainchange.review.language')`);
  await send("Network.setUserAgentOverride", {userAgent: "PlainChangeBrowserCheck", acceptLanguage: "en-US,en;q=0.9"});
  await send("Page.navigate", {url: pageUrl});
  const english = await waitReady(send, "en");

  await send("Network.setUserAgentOverride", {userAgent: "PlainChangeBrowserCheck", acceptLanguage: "fr-FR,fr;q=0.9"});
  await send("Page.navigate", {url: pageUrl});
  const unsupportedFallsBackToEnglish = await waitReady(send, "en");

  await evaluate(send, `document.querySelector('#language-switch button[data-locale="zh-CN"]').click()`);
  const switchedChinese = await waitReady(send, "zh-CN");
  await send("Page.navigate", {url: pageUrl});
  const persistedChinese = await waitReady(send, "zh-CN");

  await evaluate(send, `localStorage.removeItem('plainchange.review.language')`);
  await send("Network.setUserAgentOverride", {userAgent: "PlainChangeBrowserCheck", acceptLanguage: "zh-CN,zh;q=0.9"});
  await send("Page.navigate", {url: pageUrl});
  const systemChinese = await waitReady(send, "zh-CN");

  await evaluate(send, `document.querySelector('#language-switch button[data-locale="en"]').click()`);
  await send("Emulation.setDeviceMetricsOverride", {width: 390, height: 844, deviceScaleFactor: 1, mobile: true});
  const narrowEnglish = await waitReady(send, "en");
  const bodyChecks = [];
  if (process.argv.includes('--body')) {
    const inspect = async label => {
      await delay(120);
      const chinese = await evaluate(send, `(() => {
        const found = [];
        for (const root of document.querySelectorAll('#owner-change, #owner-architecture')) {
          const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
          let node;
          while (node = walker.nextNode()) {
            if (node.parentElement.closest('[data-preserve-language="true"]')) continue;
            const range = document.createRange(); range.selectNodeContents(node);
            if (range.getBoundingClientRect().height && /[\\u3400-\\u9fff]/.test(node.nodeValue)) found.push(node.nodeValue.trim());
          }
        }
        return found;
      })()`);
      bodyChecks.push({label, chinese});
    };
    for (const width of [1280, 390]) {
      await send('Emulation.setDeviceMetricsOverride', {width, height: 900, deviceScaleFactor: 1, mobile: width < 720});
      await evaluate(send, `document.querySelector('#change-tab').click(); document.querySelector('.owner-full-explanation').open = true`);
      await inspect(`${width}: change explanation`);
      await evaluate(send, `document.querySelector('#owner-change > .owner-technical-disclosure').open = true`);
      await inspect(`${width}: change technical explanation`);
      await evaluate(send, `document.querySelector('#technical-toggle').click(); document.querySelectorAll('.claim').forEach(n => n.open = true)`);
      await inspect(`${width}: expanded claims`);
      await evaluate(send, `document.querySelector('#architecture-tab').click()`);
      await inspect(`${width}: workflow overview`);
      const ids = await evaluate(send, `[...document.querySelectorAll('[data-owner-node-id]')].map(n => n.dataset.ownerNodeId)`);
      for (const id of ids) {
        await evaluate(send, `document.querySelector('[data-owner-node-id="${id}"]').click()`);
        await inspect(`${width}: expanded ${id}`);
        const details = await evaluate(send, `[...document.querySelectorAll('[data-owner-detail-id]')].map(n => n.dataset.ownerDetailId)`);
        for (const detail of details) {
          await evaluate(send, `document.querySelector('[data-owner-detail-id="${detail}"]').click(); document.querySelectorAll('.owner-context-secondary').forEach(n => n.open = true)`);
          await inspect(`${width}: detail ${detail}`);
        }
        await evaluate(send, `document.querySelector('[data-owner-node-id="${id}"]').click()`);
      }
      await evaluate(send, `document.querySelector('.owner-implementation-disclosure').open = true`);
      await delay(500);
      await inspect(`${width}: System workflow and implementation`);
    }
    if (bodyChecks.some(check => check.chinese.length)) {
      socket.close();
      throw new Error(JSON.stringify(bodyChecks.filter(check => check.chinese.length), null, 2));
    }
  }
  const screenshotIndex = process.argv.indexOf('--screenshot');
  if (screenshotIndex !== -1) {
    await send('Emulation.setDeviceMetricsOverride', {width: 1280, height: 1000, deviceScaleFactor: 1, mobile: false});
    await evaluate(send, `document.querySelector('#architecture-tab').click(); window.scrollTo(0, 0)`);
    await delay(150);
    const screenshot = await send('Page.captureScreenshot', {format: 'png'});
    require('node:fs').writeFileSync(process.argv[screenshotIndex + 1], Buffer.from(screenshot.data, 'base64'));
  }
  socket.close();

  const checks = {
    englishDefault: english.changeTab === "What changed" && english.architectureTab === "How this software works",
    unsupportedLocaleFallback: unsupportedFallsBackToEnglish.changeTab === "What changed",
    chineseSwitch: switchedChinese.changeTab === "这次改了什么" && switchedChinese.stored === "zh-CN",
    persistence: persistedChinese.stored === "zh-CN",
    chineseSystemDefault: systemChinese.changeTab === "这次改了什么",
    englishSwitch: narrowEnglish.changeTab === "What changed" && narrowEnglish.stored === "en",
    onlyTwoLanguages: [english, unsupportedFallsBackToEnglish, switchedChinese, systemChinese, narrowEnglish].every(item => item.supportedButtons === 2 && item.activeButtons === 1),
    noOverflow: !english.overflow && !unsupportedFallsBackToEnglish.overflow && !switchedChinese.overflow && !systemChinese.overflow && !narrowEnglish.overflow,
    browserProblems: problems.length,
    bodyStatesChecked: bodyChecks.length,
  };
  if (Object.values(checks).some(value => value === false) || checks.browserProblems) {
    throw new Error(JSON.stringify({checks, english, unsupportedFallsBackToEnglish, switchedChinese, persistedChinese, systemChinese, narrowEnglish, problems}, null, 2));
  }
  console.log(JSON.stringify({ok: true, checks, english, unsupportedFallsBackToEnglish, switchedChinese, persistedChinese, systemChinese, narrowEnglish}, null, 2));
})().catch(error => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
