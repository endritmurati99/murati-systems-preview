// Theme-Umschalter: Wahl nur als Komfort im Browser merken.
document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("theme", next); } catch (e) {}
  });
});

// Mobiles Menü nach Klick auf einen Link schließen.
document.querySelectorAll(".menu-panel a").forEach(function (a) {
  a.addEventListener("click", function () { a.closest("details").removeAttribute("open"); });
});

// Check-Formular. ponytail: öffnet vorerst eine vorausgefüllte E-Mail (kein Server, kein Drittanbieter).
// Upgrade: data-endpoint auf n8n-Webhook am VPS setzen, dann wird per fetch gesendet.
var form = document.getElementById("check-form");
if (form) {
  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var status = form.querySelector(".form-status");
    var d = new FormData(form);
    var name = (d.get("name") || "").trim();
    var email = (d.get("email") || "").trim();
    if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      status.className = "form-status err";
      status.textContent = "Bitte geben Sie Ihren Namen und eine gültige E-Mail-Adresse an.";
      (name ? form.elements.email : form.elements.name).focus();
      return;
    }
    var body =
      "Website: " + (d.get("website") || "-") + "\n" +
      "Name: " + name + "\n" +
      "E-Mail: " + email + "\n" +
      "Telefon/WhatsApp: " + (d.get("telefon") || "-") + "\n\n" +
      "Was möchte ich verbessern?\n" + (d.get("nachricht") || "-");
    var endpoint = form.getAttribute("data-endpoint");
    if (endpoint) {
      fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.fromEntries(d)) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); })
        .then(function () {
          form.reset();
          status.className = "form-status ok";
          status.textContent = "Danke! Ihre Anfrage ist angekommen. Sie hören innerhalb von 48 Stunden von uns.";
        })
        .catch(function () {
          status.className = "form-status err";
          status.textContent = "Senden hat nicht geklappt. Schreiben Sie uns bitte per WhatsApp oder E-Mail.";
        });
      return;
    }
    location.href = "mailto:" + form.getAttribute("data-to") +
      "?subject=" + encodeURIComponent("Website-Check: " + name) +
      "&body=" + encodeURIComponent(body);
    status.className = "form-status ok";
    status.textContent = "Ihr E-Mail-Programm öffnet sich mit Ihrer Anfrage. Bitte dort auf Senden tippen.";
  });
}
