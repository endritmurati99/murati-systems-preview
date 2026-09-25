// Usage: node shot.cjs <outdir> <css-file|-> <page[@W[xH]][#full][!selector]>...
// Screenshots of the VPS preview (tunnelled to 127.0.0.1:8766). "!selector" scrolls that element to the top first.
const { chromium } = require(process.env.APPDATA + "/npm/node_modules/@playwright/cli/node_modules/playwright");
const fs = require("fs");
(async () => {
  const [outdir, cssFile, ...specs] = process.argv.slice(2);
  fs.mkdirSync(outdir, { recursive: true });
  const css = cssFile && cssFile !== "-" ? fs.readFileSync(cssFile, "utf8") : "";
  const browser = await chromium.launch({ executablePath: process.env.LOCALAPPDATA + "/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64/chrome-headless-shell.exe" });
  for (const spec of specs) {
    const [main, selector] = spec.split("!");
    const full = main.endsWith("#full");
    const [page_, size = "390"] = main.replace("#full", "").split("@");
    const [w, h] = size.split("x").map(Number);
    const ctx = await browser.newContext({ viewport: { width: w, height: h || (w < 700 ? 844 : 900) }, deviceScaleFactor: w < 700 ? 2 : 1, reducedMotion: "reduce" });
    const p = await ctx.newPage();
    const errors = [];
    p.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
    p.on("pageerror", e => errors.push(e.message));
    await p.goto((/^https?:/.test(page_) ? "" : "http://127.0.0.1:8766/") + page_, { waitUntil: "networkidle" });
    if (css) await p.addStyleTag({ content: css });
    if (selector) await p.evaluate(s => { const el = document.querySelector(s); if (el) window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 70); }, selector);
    await p.waitForTimeout(400);
    const tag = (selector ? "_" + selector.replace(/[^a-z0-9]+/gi, "") : "") + (full ? "_full" : "");
    const name = `${outdir}/${page_.replace(/[^a-z0-9]+/gi, "_")}_${size}${tag}.png`;
    await p.screenshot({ path: name, fullPage: full });
    const overflow = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    console.log(name.split("/").pop(), "overflow:", overflow, errors.length ? "ERR " + errors.join(" | ") : "");
    await ctx.close();
  }
  await browser.close();
})();
