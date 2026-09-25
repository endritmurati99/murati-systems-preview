// Run with: node tests/check_privacy.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = path.join(__dirname, "..");
const source = fs.readFileSync(path.join(root, "assets/privacy.js"), "utf8");
let opened = 0, closed = 0, prevented = 0;
const link = { addEventListener(type, listener) { this[type] = listener; } };
const close = { addEventListener(type, listener) { this[type] = listener; } };
const dialog = {
  showModal() { opened++; }, close() { closed++; }, querySelector() { return close; }
};
const document = {getElementById() {return dialog;}, querySelectorAll() {return [link];}};
vm.runInNewContext(source, {document}); // No cookie, storage, fetch or network APIs provided.
link.click({preventDefault() {prevented++;}});
assert.equal(opened, 1); assert.equal(prevented, 1);
close.click(); assert.equal(closed, 1);
const fallback = {addEventListener() {throw new Error("Do not intercept fallback navigation");}};
vm.runInNewContext(source, {document:{getElementById() {return {};},querySelectorAll(){return [fallback];}}});
vm.runInNewContext(source, {document:{getElementById() {return null;}}});
for (const name of ["index.html","leistungen.html","ki-automatisierung.html","arbeitsweise.html","kontakt.html","website-check.html","impressum.html","datenschutz.html","design/index.html"]) {
 const html = fs.readFileSync(path.join(root,name), "utf8");
 assert.match(html, /data-cookie-info/); assert.match(html, /datenschutz\.html#cookies/);
 assert.match(html, /<dialog[^>]+aria-labelledby="cookie-title"/);
 assert.match(html, /assets\/privacy\.js/);
}
const form = fs.readFileSync(path.join(root,"website-check.html"),"utf8");
assert.match(form, /<form[^>]+method="post"[^>]+action="\/api\/anfrage"/); // first-party, works without JS
assert.match(form, /name="homepage"/); assert.match(form, /datenschutz\.html#anfragen/);
assert.doesNotMatch(form, /<script(?![^>]+src="assets\/privacy\.js")/);
console.log("PASS: privacy open/close/fallback, all-page integration, first-party form without JS");
