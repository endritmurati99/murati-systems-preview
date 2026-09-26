// Run with: node tests/check_privacy.cjs
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, "..");
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
const ALL_PAGES = ["index.html","leistungen.html","ki-automatisierung.html","arbeitsweise.html","kontakt.html",
 "website-check.html","impressum.html","datenschutz.html","faq.html","website-handwerk-dortmund.html",
 "website-praxis-dortmund.html","website-dienstleister-dortmund.html","danke.html","404.html","design/index.html"];
for (const name of ALL_PAGES) {
 const file = path.join(root, name);
 if (!fs.existsSync(file)) continue; // design/ is a separate gallery, not always built into dist/
 const html = fs.readFileSync(file, "utf8");
 assert.match(html, /data-cookie-info/); assert.match(html, /datenschutz\.html#cookies/);
 assert.match(html, /<dialog[^>]+aria-labelledby="cookie-title"/);
 assert.match(html, /assets\/privacy\.js/);
}
const form = fs.readFileSync(path.join(root,"website-check.html"),"utf8");
assert.match(form, /<form[^>]+method="post"[^>]+action="\/api\/anfrage"/); // first-party, works without JS
assert.match(form, /name="homepage"/); assert.match(form, /datenschutz\.html#anfragen/);
// B87: BreadcrumbList-JSON-LD hat keinen src, ist aber reine Daten ohne Ausfuehrung - zulassen.
const NO_UNEXPECTED_SCRIPT = /<script(?![^>]*src="assets\/(privacy|main|anfrage)\.js(\?v=[0-9a-f]+)?")(?![^>]*type="application\/ld\+json")/;
assert.doesNotMatch(form, NO_UNEXPECTED_SCRIPT);
const contact = fs.readFileSync(path.join(root,"kontakt.html"),"utf8");
assert.match(contact, /<form[^>]+method="post"[^>]+action="\/api\/anfrage"/); // Kontaktformular, auch ohne JS
assert.match(contact, /name="typ" value="kontakt"/); assert.match(contact, /name="homepage"/);
assert.match(contact, /datenschutz\.html#anfragen/);
assert.doesNotMatch(contact, NO_UNEXPECTED_SCRIPT); // B81: main.js schliesst das Mobil-Menue per Escape/Klick aussen
const enhance = fs.readFileSync(path.join(root, "assets/anfrage.js"), "utf8");
assert.doesNotMatch(enhance, /localStorage|sessionStorage|indexedDB|document\.cookie|innerHTML/); // kein Speicher, kein HTML aus Eingaben
vm.runInNewContext(enhance, {window: {matchMedia: () => ({matches: false})}, document: {querySelector: () => null, querySelectorAll: () => []},
 location: {search: "?nr=MS-260925-AB12"}, URLSearchParams, URL, crypto: globalThis.crypto}); // lädt ohne Formular fehlerfrei
console.log("PASS: privacy open/close/fallback, all-page integration, first-party forms without JS, anfrage.js without storage");
