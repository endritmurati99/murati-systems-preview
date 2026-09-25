// Anfrageformulare (Website-Check, Kontakt): geführte Abschnitte mit Fortschrittsbalken,
// Prüfung direkt am Feld und Versand ohne Neuladen. Ohne JavaScript bleibt jedes Formular
// ein normales POST an /api/anfrage. Speichert nichts im Browser.
(() => {
  "use strict";

  const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  const PHONE = /^\+?[0-9 ()/.-]{6,40}$/;
  const ANTWORTZEIT = "in der Regel innerhalb von zwei Werktagen";
  const MESSAGES = {
    ziel: "Bitte wählen Sie aus, was sich zuerst verbessern soll.",
    anliegen: "Bitte wählen Sie aus, worum es geht.",
    nachricht: "Bitte schreiben Sie kurz Ihr Anliegen.",
    name: "Bitte geben Sie Ihren Namen an.",
    email: "Bitte geben Sie eine gültige E-Mail-Adresse an.",
    telefon: "Für eine Antwort per WhatsApp benötigen wir Ihre Nummer.",
  };
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const waLink = document.querySelector('a[href^="https://wa.me/"]');
  const waNumber = waLink ? new URL(waLink.href).pathname.replace(/\D/g, "") : "";
  let uid = 0;

  // Danke-Seite (Versand ohne fetch): Vorgangsnummer zeigen, Hinweise passend zu Anfrageart und Bestätigung.
  const params = new URLSearchParams(location.search);
  const vorgang = document.querySelector("[data-vorgang]");
  const nr = params.get("nr");
  if (vorgang && nr && /^MS-\d{6}-[A-Z0-9]{4}$/.test(nr)) {
    vorgang.querySelector("strong").textContent = nr;
    vorgang.hidden = false;
  }
  document.querySelectorAll("[data-typ]").forEach(item => {
    if (params.get("typ") && item.dataset.typ !== params.get("typ")) item.hidden = true;
  });
  if (params.get("b") === "0") document.querySelectorAll("[data-bestaetigung]").forEach(item => { item.hidden = true; });

  document.querySelectorAll("form[data-anfrage]").forEach(setup);

  function setup(form) {
    form.noValidate = true; // eigene Prüfung je Abschnitt; ohne JS greift die Browserprüfung
    const nonce = el("input");
    nonce.type = "hidden";
    nonce.name = "nonce";
    nonce.value = randomId();
    form.append(nonce);
    const live = el("p", "sr-only");
    live.setAttribute("aria-live", "polite");
    form.prepend(live);

    const steps = form.hasAttribute("data-schritte") ? [...form.querySelectorAll(":scope > fieldset")] : [];
    const flow = steps.length > 1 ? stepper(form, steps, live) : null;

    const phone = form.elements.telefon;
    const hint = phone && phone.closest("label").querySelector("small");
    const syncChannel = () => {
      if (!phone) return;
      const whatsapp = (form.querySelector('input[name="kanal"]:checked') || {}).value === "WhatsApp";
      phone.required = whatsapp;
      if (hint) hint.textContent = whatsapp ? "(für WhatsApp nötig)" : "(optional)";
      if (!whatsapp && !problem(phone)) clearError(phone);
    };
    syncChannel();

    form.addEventListener("change", event => {
      if (event.target.name === "kanal") syncChannel();
      revalidate(event.target);
    });
    form.addEventListener("input", event => revalidate(event.target));
    form.addEventListener("focusout", event => {
      const field = event.target;
      if (field.matches && field.matches('input[type="email"], input[name="telefon"]') && field.value.trim()) {
        const message = problem(field);
        if (message) showError(field, message);
      }
    });
    form.addEventListener("submit", event => {
      event.preventDefault();
      if (flow && !flow.isLast()) return flow.next();
      if (flow ? !flow.checkAll() : !checkGroup(form, live)) return;
      send(form, live, flow);
    });
  }

  function stepper(form, steps, live) {
    form.classList.add("is-stepped");
    let current = 0;
    const bar = el("div", "form-progress");
    bar.setAttribute("aria-hidden", "true");
    const items = steps.map(step => {
      step.tabIndex = -1;
      const item = el("span", "form-progress-item", title(step));
      bar.append(item);
      return item;
    });
    form.prepend(bar);

    const submit = form.querySelector('[type="submit"]');
    const back = button("Zurück", "button subtle form-back");
    const next = button("Weiter", "button primary form-next");
    next.append(arrow());
    const nav = el("div", "form-nav");
    nav.append(back, next, submit);
    form.append(nav);

    back.addEventListener("click", () => show(current - 1));
    next.addEventListener("click", () => api.next());
    form.addEventListener("click", event => {
      const jump = event.target.closest("[data-springe]");
      if (jump) show(Number(jump.dataset.springe));
    });

    function show(index, focus = true) {
      current = Math.max(0, Math.min(index, steps.length - 1));
      const last = current === steps.length - 1;
      steps.forEach((step, i) => step.classList.toggle("is-current", i === current));
      items.forEach((item, i) => {
        item.classList.toggle("is-done", i < current);
        item.classList.toggle("is-current", i === current);
      });
      form.classList.toggle("is-last", last);
      back.hidden = current === 0;
      next.hidden = last;
      submit.hidden = !last;
      if (last) summary(form, steps);
      if (!focus) return;
      live.textContent = "Abschnitt " + title(steps[current]);
      steps[current].focus({ preventScroll: true });
      if (form.getBoundingClientRect().top < 0) {
        form.scrollIntoView({ block: "start", behavior: reduceMotion ? "auto" : "smooth" });
      }
    }
    show(0, false);

    const api = {
      isLast: () => current === steps.length - 1,
      next: () => { if (checkGroup(steps[current], live)) show(current + 1); },
      checkAll: () => {
        const bad = steps.findIndex(step => !checkGroup(step, live, false));
        if (bad < 0) return true;
        show(bad);
        checkGroup(steps[bad], live);
        return false;
      },
      showField: name => {
        const index = steps.findIndex(step => step.querySelector(`[name="${name}"]`));
        if (index >= 0) show(index, false);
      },
    };
    return api;
  }

  function summary(form, steps) {
    let box = form.querySelector(".form-summary");
    if (!box) {
      box = el("div", "form-summary");
      steps[steps.length - 1].querySelector("legend").after(box);
    }
    box.replaceChildren();
    steps.slice(0, -1).forEach((step, index) => {
      const chosen = [...step.querySelectorAll("input:checked")].map(input => input.value);
      const typed = [...step.querySelectorAll('input[type="text"], input[type="url"], textarea')]
        .map(field => field.value.trim()).filter(Boolean)
        .map(text => (text.length > 70 ? text.slice(0, 69) + "…" : text));
      const values = chosen.concat(typed);
      const row = el("p", "form-summary-row");
      const change = button("Ändern", "form-summary-edit");
      change.dataset.springe = index;
      change.setAttribute("aria-label", title(step) + " ändern");
      row.append(el("span", "form-summary-label", title(step)),
        el("span", "form-summary-value", values.length ? values.join(" · ") : "Keine Angabe"), change);
      box.append(row);
    });
  }

  function checkGroup(scope, live, focus = true) {
    let first = null;
    const fail = (field, message) => { showError(field, message); first = first || field; };
    const radios = new Set([...scope.querySelectorAll('input[type="radio"][required]')].map(input => input.name));
    radios.forEach(name => {
      const group = [...scope.querySelectorAll(`input[name="${name}"]`)];
      if (group.some(input => input.checked)) clearError(group[0]);
      else fail(group[0], MESSAGES[name] || "Bitte wählen Sie eine Antwort.");
    });
    scope.querySelectorAll('input:not([type="radio"]):not([type="checkbox"]):not([type="hidden"]), textarea').forEach(field => {
      if (field.closest(".hp")) return;
      const message = problem(field);
      if (message) fail(field, message);
      else clearError(field);
    });
    if (first && focus) {
      focusField(first);
      live.textContent = "Bitte prüfen Sie die markierten Angaben.";
    }
    return !first;
  }

  function problem(field) {
    const value = field.value.trim();
    if (field.required && !value) return MESSAGES[field.name] || "Bitte füllen Sie dieses Feld aus.";
    if (value && field.type === "email" && !EMAIL.test(value)) return MESSAGES.email;
    if (value && field.name === "telefon" && !(PHONE.test(value) && value.replace(/\D/g, "").length >= 6)) {
      return "Bitte prüfen Sie die Telefonnummer.";
    }
    return "";
  }

  function revalidate(field) {
    if (!field.name || field.getAttribute("aria-invalid") !== "true") return;
    if (field.type === "radio" || !problem(field)) clearError(field);
  }

  function focusField(field) {
    // Mittig scrollen, damit die feste Kontaktleiste am Handy das Feld nicht verdeckt.
    field.focus({ preventScroll: true });
    field.scrollIntoView({ block: "center", behavior: reduceMotion ? "auto" : "smooth" });
  }

  function group(field) {
    return field.type === "radio" ? [...field.form.querySelectorAll(`input[name="${field.name}"]`)] : [field];
  }

  function showError(field, message) {
    const inputs = group(field);
    let note = document.getElementById(inputs[0].dataset.fehler || "");
    if (!note) {
      note = el("p", "field-error");
      note.id = "fehler-" + ++uid;
      inputs[0].dataset.fehler = note.id;
      (field.type === "radio" ? field.closest(".choices, .channel") : field.closest("label")).after(note);
    }
    if (field.type === "radio") field.closest(".choices, .channel").classList.add("is-invalid");
    note.textContent = message;
    inputs.forEach(input => {
      input.setAttribute("aria-invalid", "true");
      input.setAttribute("aria-describedby", note.id);
    });
  }

  function clearError(field) {
    const inputs = group(field);
    const note = document.getElementById(inputs[0].dataset.fehler || "");
    if (note) note.remove();
    delete inputs[0].dataset.fehler;
    if (field.type === "radio") field.closest(".choices, .channel").classList.remove("is-invalid");
    inputs.forEach(input => {
      input.removeAttribute("aria-invalid");
      input.removeAttribute("aria-describedby");
    });
  }

  async function send(form, live, flow) {
    if (form.classList.contains("is-sending")) return;
    const alert = form.querySelector(".form-alert");
    if (alert) alert.remove();
    if (navigator.onLine === false) {
      return formError(form, "Keine Internetverbindung. Bitte senden Sie noch einmal, sobald Sie wieder online sind.");
    }
    const submit = form.querySelector('[type="submit"]');
    const label = [...submit.childNodes].map(node => node.cloneNode(true));
    const busy = on => {
      form.classList.toggle("is-sending", on);
      form.setAttribute("aria-busy", String(on));
      submit.disabled = on;
      if (on) submit.replaceChildren(el("span", "form-spinner"), "Wird gesendet …");
      else submit.replaceChildren(...label);
    };
    busy(true);
    live.textContent = "Wird gesendet.";
    let response;
    try {
      response = await fetch(form.action, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new URLSearchParams(new FormData(form)),
      });
    } catch {
      form.submit(); // gesperrt oder Netz weg: normaler Versand, die Nonce verhindert Doppelungen
      return;
    }
    let result = null;
    try { result = await response.json(); } catch { result = null; }
    busy(false);
    if (result && result.ok) return success(form, result);
    const field = result && result.feld && form.elements[result.feld];
    if (field) {
      const target = field.length && !field.tagName ? field[0] : field;
      if (flow) flow.showField(result.feld);
      showError(target, result.fehler);
      focusField(target);
      live.textContent = result.fehler;
      return;
    }
    formError(form, (result && result.fehler) ||
      "Das hat gerade nicht geklappt. Bitte versuchen Sie es gleich noch einmal oder schreiben Sie uns per WhatsApp oder E-Mail.");
  }

  function formError(form, message) {
    const box = el("p", "form-alert", message);
    box.setAttribute("role", "alert");
    form.querySelector(".form-nav, [type='submit']").before(box);
  }

  function success(form, result) {
    const check = result.typ === "check";
    const weg = result.kanal === "WhatsApp" ? "per WhatsApp" : "per E-Mail";
    const panel = el("div", "form-success");
    panel.tabIndex = -1;
    const mark = el("span", "form-success-mark");
    mark.setAttribute("aria-hidden", "true");
    const heading = el("h2", "", check ? "Danke. Ihr Website-Check ist angefragt." : "Danke. Ihre Nachricht ist angekommen.");
    const number = el("p", "form-success-nr", "Vorgangsnummer ");
    number.append(el("strong", "", result.nr));
    const path = el("ul", "form-success-path");
    (check
      ? ["Wir sehen uns Ihre Website und Ihre Angaben persönlich an.",
         `Sie hören ${weg} von uns, ${ANTWORTZEIT}.`,
         "Sie bekommen drei Schwachstellen, drei schnelle Verbesserungen und eine Empfehlung. Kostenlos."]
      : ["Wir lesen Ihre Nachricht persönlich.", `Sie hören ${weg} von uns, ${ANTWORTZEIT}.`]
    ).forEach(text => path.append(el("li", "", text)));
    panel.append(mark, heading, number, path);
    if (result.bestaetigung) {
      panel.append(el("p", "form-success-note", "Eine Bestätigung mit der Vorgangsnummer ist an Ihre E-Mail-Adresse unterwegs."));
    }
    if (waNumber) {
      const wa = el("a", "button wa");
      wa.href = `https://wa.me/${waNumber}?text=${encodeURIComponent(`Hallo Murati Systems, zu meiner Anfrage ${result.nr}: `)}`;
      wa.target = "_blank";
      wa.rel = "noopener noreferrer";
      const icon = el("span", "wa-i");
      icon.setAttribute("aria-hidden", "true");
      wa.append(icon, "Per WhatsApp ergänzen");
      panel.append(wa);
    }
    form.hidden = true;
    form.after(panel);
    panel.focus({ preventScroll: true });
    panel.scrollIntoView({ block: "start", behavior: reduceMotion ? "auto" : "smooth" });
  }

  function title(step) {
    return step.dataset.titel || step.querySelector("legend").textContent.trim();
  }

  function arrow() {
    const span = el("span", "", "→");
    span.setAttribute("aria-hidden", "true");
    return span;
  }

  function button(text, className) {
    const node = el("button", className, text);
    node.type = "button";
    return node;
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function randomId() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return [...crypto.getRandomValues(new Uint8Array(16))].map(b => b.toString(16).padStart(2, "0")).join("");
  }
})();
