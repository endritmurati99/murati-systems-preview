// node compose.cjs <html-file> <out.png> <width>  – rendert eine lokale Vergleichsseite als PNG
const { chromium } = require(process.env.APPDATA + "/npm/node_modules/@playwright/cli/node_modules/playwright");
const { pathToFileURL } = require("url");
(async () => {
  const [html, out, width = "1500"] = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: process.env.LOCALAPPDATA + "/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe" });
  const p = await browser.newPage({ viewport: { width: +width, height: 800 }, deviceScaleFactor: 1 });
  await p.goto(pathToFileURL(html).href, { waitUntil: "load" });
  await p.screenshot({ path: out, fullPage: true });
  await browser.close();
})();
