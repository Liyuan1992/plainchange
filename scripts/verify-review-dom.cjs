// Script/DOM regression, NOT browser layout acceptance.
// npm install --prefix artifacts/dom-validation --no-save --package-lock=false linkedom
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {parseHTML} = require('../artifacts/dom-validation/node_modules/linkedom');
const {window, document} = parseHTML(fs.readFileSync(process.argv[2], 'utf8'));
const originalJSON = document.querySelector('#review-data').textContent;
window.innerWidth = 390;
window.scrollY = 0;
window.requestAnimationFrame = () => 0; // Geometry is intentionally not simulated.
window.scrollTo = () => {};
window.matchMedia = () => ({matches: false});
window.HTMLElement.prototype.scrollIntoView = () => {};
const context = vm.createContext({window, document, console, setTimeout, clearTimeout,
  Node: window.Node, NodeFilter: {SHOW_TEXT: 4, SHOW_ELEMENT: 1},
  MutationObserver: window.MutationObserver,
  navigator: {languages: ['en']}, location: {hash: '#plainchange-lang=en'},
  localStorage: {getItem: () => null, setItem: () => {}},
  crypto: require('node:crypto').webcrypto, TextDecoder, Uint8Array,
  Blob, Response, DecompressionStream, atob,
});
for (const name of ['review-i18n.js', 'review.js']) {
  vm.runInContext(fs.readFileSync(`src/plainchange/templates/${name}`, 'utf8'), context, {filename: name});
}
const delay = () => new Promise(resolve => setTimeout(resolve, 200));
const checked = [];
async function inspect(label, selector) {
  await delay();
  const leftovers = [];
  for (const root of document.querySelectorAll(selector)) {
    const walker = document.createTreeWalker(root, 4);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement.closest('[data-preserve-language="true"]')) continue;
      if (/[\u3400-\u9fff]/.test(node.nodeValue)) leftovers.push(node.nodeValue.trim());
    }
  }
  checked.push({label, leftovers: [...new Set(leftovers)]});
}
(async () => {
  await delay();
  await inspect('change explanations', '#summary-grid');
  for (const view of ['before', 'after', 'diff']) {
    document.querySelector(`[data-view="${view}"]`).click();
    await inspect(`change graph ${view}`, '#legacy-change-host');
    const nodeIds = [...document.querySelectorAll('#graph [data-node-id]')].map(n => n.dataset.nodeId);
    for (const id of [...new Set(nodeIds)]) {
      document.querySelector(`#graph [data-node-id="${id}"]`).click();
      await inspect(`change node ${view}/${id}`, '#legacy-change-host');
    }
  }
  document.querySelector('#technical-toggle').click();
  await inspect('technical claims and limitations', '#technical-content');
  document.querySelector('#architecture-tab').click();
  const disclosure = document.querySelector('.owner-implementation-disclosure');
  disclosure.open = true;
  disclosure.dispatchEvent(new window.Event('toggle'));
  await inspect('System workflow', '#architecture-concept');
  const cards = [...document.querySelectorAll('[data-concept-id]')].map(n => n.dataset.conceptId);
  assert.equal(cards.length, 8, 'workflow must actually render');
  assert.ok(document.querySelector('.concept-expanded-label'), 'expanded status must be real DOM text, not CSS content');
  assert.equal(document.querySelector('.concept-expanded-label').textContent, 'Implementation expanded');
  for (const id of cards) {
    document.querySelector(`[data-concept-id="${id}"]`).click();
    await inspect(`workflow detail ${id}`, '#legacy-architecture-host');
  }
  assert.ok(document.querySelector('.claim-original [data-preserve-language="true"]'), 'original claims must remain accessible');
  assert.equal(document.querySelector('#review-data').textContent, originalJSON, 'canonical JSON must not be translated');
  const failures = checked.filter(item => item.leftovers.length);
  if (failures.length) throw new Error(JSON.stringify(failures, null, 2));
  console.log(JSON.stringify({ok: true, states: checked.length, browserLayoutVerified: false}));
})().catch(error => { console.error(error); process.exitCode = 1; });
