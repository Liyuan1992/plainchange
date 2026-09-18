const fs = require('node:fs');
const path = require('node:path');

const [endpoint, pageUrl, changeOutput, softwareOutput, locale = 'zh-CN'] = process.argv.slice(2);
if (!endpoint || !pageUrl || !changeOutput || !softwareOutput) {
  throw new Error('usage: node scripts/capture-readme-demo.cjs <endpoint> <page-url> <change.png> <software.png> [zh-CN|en]');
}
if (!['zh-CN', 'en'].includes(locale)) throw new Error(`unsupported locale: ${locale}`);

const delay = milliseconds => new Promise(resolve => setTimeout(resolve, milliseconds));

async function targetPage() {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const targets = await fetch(`${endpoint}/json`).then(response => response.json());
      const target = targets.find(item => item.type === 'page');
      if (target) return target;
    } catch (_) {}
    await delay(100);
  }
  throw new Error('browser page did not become available');
}

async function connect(target) {
  const socket = new WebSocket(target.webSocketDebuggerUrl);
  const pending = new Map();
  let nextId = 0;
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, {once: true});
    socket.addEventListener('error', reject, {once: true});
  });
  socket.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (!message.id || !pending.has(message.id)) return;
    const callbacks = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) callbacks.reject(new Error(message.error.message));
    else callbacks.resolve(message.result);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, {resolve, reject});
    socket.send(JSON.stringify({id, method, params}));
  });
  return {socket, send};
}

async function evaluate(send, expression) {
  const result = await send('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}

async function waitForReady(send) {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (await evaluate(send, "document.documentElement?.dataset?.i18nReady === 'true'")) return;
    await delay(100);
  }
  throw new Error('report did not become ready');
}

async function capture(send, output) {
  const screenshot = await send('Page.captureScreenshot', {format: 'png'});
  fs.mkdirSync(path.dirname(path.resolve(output)), {recursive: true});
  fs.writeFileSync(output, Buffer.from(screenshot.data, 'base64'));
}

(async () => {
  const target = await targetPage();
  const {socket, send} = await connect(target);
  try {
    await send('Runtime.enable');
    await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride', {width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false});
    await send('Page.navigate', {url: pageUrl});
    await waitForReady(send);
    await evaluate(send, `localStorage.setItem('plainchange.review.language', ${JSON.stringify(locale)}); location.reload()`);
    await waitForReady(send);
    await evaluate(send, "document.querySelector('#change-tab').click(); window.scrollTo(0, 0)");
    await delay(150);
    await capture(send, changeOutput);
    await evaluate(send, "document.querySelector('#architecture-tab').click(); window.scrollTo(0, 0)");
    await delay(150);
    await capture(send, softwareOutput);
  } finally {
    socket.close();
  }
})().catch(error => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
