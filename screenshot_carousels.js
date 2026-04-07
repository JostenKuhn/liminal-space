
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1350 });
  await page.goto('file:///Users/tarynlee/Desktop/liminal-space/instagram/generate_carousels.html');
  await page.waitForTimeout(2000); // wait for fonts

  const carousels = [
    { prefix: 'carousel-1-cia', ids: ['c1s1','c1s2','c1s3','c1s4','c1s5','c1s6','c1s7','c1s8','c1s9'] },
    { prefix: 'carousel-2-states', ids: ['c2s1','c2s2','c2s3','c2s4','c2s5','c2s6','c2s7','c2s8','c2s9'] },
    { prefix: 'carousel-3-threshold', ids: ['c3s1','c3s2','c3s3','c3s4','c3s5','c3s6','c3s7','c3s8','c3s9'] },
  ];

  for (const c of carousels) {
    for (let i = 0; i < c.ids.length; i++) {
      const el = await page.$('#' + c.ids[i]);
      const path = `instagram/${c.prefix}/slide-${i+1}.jpg`;
      await el.screenshot({ path, type: 'jpeg', quality: 95 });
      console.log('Saved: ' + path);
    }
  }

  await browser.close();
  console.log('Done!');
})();
