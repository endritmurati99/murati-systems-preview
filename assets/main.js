// Übernimmt die Website-Adresse aus dem Feld der Startseite (?website=...) in den Website-Check.
const websiteField = document.querySelector('#formular input[name="website"]');
const givenWebsite = new URLSearchParams(location.search).get("website");
if (websiteField && givenWebsite) websiteField.value = givenWebsite.trim().slice(0, 250);

// Themenleiste (Leistungen, FAQ): markiert den Abschnitt, der gerade im Bild ist.
const jumpLinks = [...document.querySelectorAll(".jump a[href^='#']")];
if (jumpLinks.length && "IntersectionObserver" in window) {
  const linkFor = new Map(jumpLinks.map(link => [decodeURIComponent(link.hash.slice(1)), link]));
  const spy = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      jumpLinks.forEach(link => link.removeAttribute("aria-current"));
      linkFor.get(entry.target.id)?.setAttribute("aria-current", "true");
    }
  }, { rootMargin: "-30% 0px -60% 0px" });
  linkFor.forEach((_, id) => { const section = document.getElementById(id); if (section) spy.observe(section); });
}

// B81: Mobil-Menü per Escape oder Klick ausserhalb schliessen (auch Klick auf den abgedunkelten
// Hintergrund), Fokus zurück auf den Menü-Knopf.
const mobileMenu = document.querySelector(".mobile-menu");
if (mobileMenu) {
  const summary = mobileMenu.querySelector("summary");
  const panel = mobileMenu.querySelector("nav");
  const closeMenu = () => mobileMenu.removeAttribute("open");
  document.addEventListener("click", event => {
    if (!mobileMenu.hasAttribute("open")) return;
    if (summary.contains(event.target) || (panel && panel.contains(event.target))) return;
    closeMenu();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && mobileMenu.hasAttribute("open")) {
      closeMenu();
      summary.focus();
    }
  });
}

// Startseite: getippte Adresse erscheint in der Beispiel-Karte; statt Beispielwerten steht dort dann "prüfen wir".
const heroField = document.getElementById("hero-url");
const scanCard = document.querySelector(".scan");
if (heroField && scanCard) {
  const scanUrl = scanCard.querySelector(".scan-url");
  const sampleUrl = scanUrl.textContent;
  heroField.addEventListener("input", () => {
    const typed = heroField.value.trim().replace(/^https?:\/\//i, "").split("/")[0].slice(0, 60);
    scanCard.classList.toggle("is-live", typed.length > 0);
    scanUrl.textContent = typed || sampleUrl;
  });
}
