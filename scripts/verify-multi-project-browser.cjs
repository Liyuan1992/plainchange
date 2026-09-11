const path = require('node:path');
const fs = require('node:fs');

const playwrightPath = process.env.PLAINCHANGE_PLAYWRIGHT_PATH;
if (!playwrightPath) throw new Error('PLAINCHANGE_PLAYWRIGHT_PATH is required');
const {chromium} = require(playwrightPath);
const reports = process.argv.slice(2);
if (!reports.length) throw new Error('provide report.html paths');

async function visibleHanLines(page) {
  return page.evaluate(() => {
    const allowedNativeLanguageLabels = new Set(['中文']);
    const lines = document.body.innerText
      .split(/\r?\n/)
      .map(value => value.trim())
      .filter(Boolean)
      .filter(value => /[\u3400-\u9fff]/.test(value))
      .filter(value => !allowedNativeLanguageLabels.has(value));
    return [...new Set(lines)];
  });
}

function mergeUnique(target, values) {
  values.forEach(value => { if (!target.includes(value)) target.push(value); });
}

(async () => {
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.PLAINCHANGE_BROWSER_PATH ? {executablePath: process.env.PLAINCHANGE_BROWSER_PATH} : {}),
  });
  const results = [];
  for (const report of reports) {
    const absolute = path.resolve(report);
    const record = {report: absolute, errors: [], states: []};
    const page = await browser.newPage({viewport: {width: 1280, height: 900}, locale: 'zh-CN'});
    page.on('console', message => { if (message.type() === 'error') record.errors.push(message.text()); });
    page.on('pageerror', error => record.errors.push(error.message));
    await page.goto(`file:///${absolute.replaceAll('\\', '/')}`);
    await page.waitForFunction(() => document.documentElement.dataset.i18nReady === 'true');
    for (const width of [1280, 390]) {
      await page.setViewportSize({width, height: 900});
      await page.locator('#change-tab').click();
      record.states.push({width, page: 'change', overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)});
      await page.locator('#architecture-tab').click();
      const capabilityMap = await page.locator('#owner-map-canvas').getAttribute('data-owner-map-kind') === 'capability';
      const overview = page.locator('[data-owner-node-id]');
      const overviewCount = await overview.count();
      const expansionCounts = [];
      for (let index = 0; index < overviewCount; index += 1) {
        const expandable = await overview.nth(index).getAttribute('aria-expanded') !== null;
        await overview.nth(index).click();
        const detail = page.locator('[data-owner-detail-id]');
        const detailCount = await detail.count();
        expansionCounts.push({index, expandable, detailCount});
        if (capabilityMap && expandable && detailCount < 2) throw new Error(`expandable capability has fewer than two details: ${absolute}`);
        if (capabilityMap && !expandable && detailCount !== 0) throw new Error(`leaf capability rendered duplicate details: ${absolute}`);
        for (let detailIndex = 0; detailIndex < detailCount; detailIndex += 1) await detail.nth(detailIndex).click();
        if (expandable) await overview.nth(index).click();
      }
      let technicalScroll = null;
      if (width > 720) {
        const disclosure = page.locator('.owner-implementation-disclosure');
        if (!await disclosure.evaluate(element => element.open)) {
          await disclosure.locator(':scope > summary').click();
        }
        await page.waitForFunction(() => document.querySelector('#architecture-concept-canvas')?.clientWidth > 0);
        const conceptCanvas = page.locator('#architecture-concept-canvas');
        const before = await conceptCanvas.evaluate(element => ({
          clientWidth: element.clientWidth,
          scrollWidth: element.scrollWidth,
          scrollLeft: element.scrollLeft,
          overflowX: getComputedStyle(element).overflowX,
        }));
        let afterScrollLeft = before.scrollLeft;
        if (before.scrollWidth > before.clientWidth) {
          if (!['auto', 'scroll'].includes(before.overflowX)) {
            throw new Error(`technical architecture canvas is not user-scrollable: ${absolute}`);
          }
          await conceptCanvas.evaluate(element => { element.scrollLeft = 0; });
          await conceptCanvas.scrollIntoViewIfNeeded();
          const box = await conceptCanvas.boundingBox();
          if (!box) throw new Error(`technical architecture canvas has no visible box: ${absolute}`);
          await page.mouse.move(box.x + box.width / 2, box.y + Math.min(50, box.height / 2));
          await page.mouse.wheel(280, 0);
          await page.waitForTimeout(80);
          afterScrollLeft = await conceptCanvas.evaluate(element => element.scrollLeft);
          if (afterScrollLeft <= 0) {
            throw new Error(`technical architecture canvas did not move after horizontal wheel input: ${absolute}`);
          }
        }
        technicalScroll = {...before, afterScrollLeft};
      }
      record.states.push({width, page: 'software', overviewCount,
        expansionCounts,
        technicalScroll,
        overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
        overflowElements: await page.evaluate(() => [...document.querySelectorAll('body *')]
          .filter(element => element.getBoundingClientRect().right > innerWidth + 1)
          .slice(0, 12)
          .map(element => ({tag: element.tagName, className: element.className, right: Math.round(element.getBoundingClientRect().right), text: (element.textContent || '').trim().slice(0, 80)}))),
      });
    }
    await page.setViewportSize({width: 1280, height: 900});
    await page.locator('#change-tab').click();
    record.headline = await page.locator('#owner-change-headline').textContent();
    await page.locator('#architecture-tab').click();
    await page.evaluate(() => window.scrollTo(0, 0));
    record.softwareHeadline = await page.locator('#owner-map-headline').textContent();
    record.mapKind = await page.locator('#owner-map-canvas').getAttribute('data-owner-map-kind');
    record.visibleConnectors = await page.locator('#owner-map-links .owner-map-link').count();
    record.steps = await page.locator('[data-owner-node-id] .owner-map-node-copy strong').allTextContents();
    const firstExpandable = page.locator('[data-owner-node-id][aria-expanded]').first();
    if (await firstExpandable.count()) {
      await firstExpandable.click();
      record.expandedDetailCount = await page.locator('[data-owner-detail-id]').count();
      const expandedScreenshot = path.join(path.dirname(absolute), 'browser-software-expanded.png');
      await page.screenshot({path: expandedScreenshot, fullPage: false});
      record.expandedScreenshot = expandedScreenshot;
      await firstExpandable.click();
    } else {
      record.expandedDetailCount = 0;
    }
    const screenshot = path.join(path.dirname(absolute), 'browser-software.png');
    await page.screenshot({path: screenshot, fullPage: false});
    record.screenshot = screenshot;
    await page.close();
    const englishPage = await browser.newPage({viewport: {width: 1280, height: 900}, locale: 'en-US'});
    await englishPage.goto(`file:///${absolute.replaceAll('\\', '/')}#plainchange-lang=en`);
    await englishPage.waitForFunction(() => document.documentElement.dataset.i18nReady === 'true');
    record.englishFallbackNotice = await englishPage.locator('.language-boundary').textContent();
    record.englishHasTranslatedBody = !/[\u3400-\u9fff]/.test(await englishPage.locator('#owner-change-headline').textContent());
    const englishChangeDisclosure = englishPage.locator('.owner-technical-disclosure').first();
    if (!await englishChangeDisclosure.evaluate(element => element.open)) {
      await englishChangeDisclosure.locator(':scope > summary').click();
    }
    record.englishVisibleHan = {
      change: await visibleHanLines(englishPage),
      software: [],
    };
    const contextButton = englishPage.locator('[data-summary-context="summary.why"]');
    if (await contextButton.count()) {
      await contextButton.click();
      mergeUnique(record.englishVisibleHan.change, await visibleHanLines(englishPage));
      await contextButton.click();
    }
    for (const viewButton of await englishPage.locator('[data-view]').all()) {
      await viewButton.click();
      const nodeIds = await englishPage.locator('[data-node-id]').evaluateAll(elements => [...new Set(elements.map(element => element.dataset.nodeId))]);
      for (const nodeId of nodeIds) {
        await englishPage.locator(`[data-node-id="${nodeId}"]`).first().click();
        mergeUnique(record.englishVisibleHan.change, await visibleHanLines(englishPage));
      }
    }
    const technicalToggle = englishPage.locator('#technical-toggle');
    if (await technicalToggle.count()) {
      await technicalToggle.click();
      mergeUnique(record.englishVisibleHan.change, await visibleHanLines(englishPage));
    }
    await englishPage.locator('#architecture-tab').click();
    const englishDisclosure = englishPage.locator('.owner-implementation-disclosure');
    if (!await englishDisclosure.evaluate(element => element.open)) {
      await englishDisclosure.locator(':scope > summary').click();
    }
    await englishPage.waitForFunction(() => document.querySelector('#architecture-concept-title')?.textContent?.trim());
    await englishPage.waitForFunction(() => document.querySelector('#architecture-scope')?.textContent?.trim());
    record.englishGeneratedArchitecture = {
      title: await englishPage.locator('#architecture-concept-title').textContent(),
      boundary: await englishPage.locator('#architecture-concept-boundary').textContent(),
      status: await englishPage.locator('#architecture-scope').textContent(),
      implementation: await englishPage.locator('.concept-implementation').first().textContent(),
    };
    record.englishVisibleHan.software = await visibleHanLines(englishPage);
    const untranslatedGeneratedArchitecture = Object.entries(record.englishGeneratedArchitecture)
      .filter(([, value]) => /[\u3400-\u9fff]/.test(value || ''));
    await englishPage.close();
    if (!record.englishHasTranslatedBody && !record.englishFallbackNotice.startsWith('English report text is not available')) {
      throw new Error(`missing honest translation fallback: ${absolute}`);
    }
    if (untranslatedGeneratedArchitecture.length) {
      throw new Error(`generated architecture text remains Chinese: ${JSON.stringify(untranslatedGeneratedArchitecture)}`);
    }
    if (process.env.PLAINCHANGE_REQUIRE_ENGLISH_VISIBLE === '1') {
      const visibleHan = [...record.englishVisibleHan.change, ...record.englishVisibleHan.software];
      if (visibleHan.length) throw new Error(`visible English-mode text remains Chinese: ${JSON.stringify(record.englishVisibleHan)}`);
    }
    if (record.errors.length || record.states.some(state => state.overflow)) throw new Error(JSON.stringify(record, null, 2));
    results.push(record);
  }
  await browser.close();
  console.log(JSON.stringify({ok: true, reports: results}, null, 2));
})().catch(error => { console.error(error.stack || String(error)); process.exitCode = 1; });
