const check = document.getElementById("guided-check");
if (check) {
  let step = 1;
  const panels = [...check.querySelectorAll("[data-step]")];
  const next = document.getElementById("next-step");
  const back = document.getElementById("back-step");
  const send = document.getElementById("send-check");
  const status = document.getElementById("wizard-status");
  const stepLabel = document.getElementById("step-label");
  const progress = document.getElementById("progress-fill");

  function showStep(number) {
    step = number;
    panels.forEach(panel => { panel.hidden = Number(panel.dataset.step) !== step; });
    stepLabel.textContent = "SCHRITT " + step + " VON 3";
    progress.style.width = (step * 100 / 3) + "%";
    back.hidden = step === 1;
    next.hidden = step === 3;
    send.hidden = step !== 3;
    status.textContent = "";
    check.querySelector("[data-step='" + step + "'] legend").focus();
  }

  function validCurrentStep() {
    if (step === 2 && !check.querySelector("input[name='ziel']:checked")) {
      status.textContent = "Bitte wählen Sie ein Ziel aus.";
      return false;
    }
    if (step === 3) {
      const name = check.elements.name.value.trim();
      const email = check.elements.email.value.trim();
      if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
        status.textContent = "Bitte geben Sie Namen und eine gültige E-Mail-Adresse an.";
        (name ? check.elements.email : check.elements.name).focus();
        return false;
      }
      if (check.querySelector("input[name='kanal']:checked").value === "WhatsApp" && !check.elements.telefon.value.trim()) {
        status.textContent = "Für eine Antwort per WhatsApp benötigen wir Ihre Nummer.";
        check.elements.telefon.focus();
        return false;
      }
    }
    status.textContent = "";
    return true;
  }

  next.addEventListener("click", () => { if (validCurrentStep()) showStep(step + 1); });
  back.addEventListener("click", () => showStep(step - 1));
  check.addEventListener("keydown", event => {
    if (event.key === "Enter" && event.target.tagName !== "TEXTAREA" && step < 3) {
      event.preventDefault();
      next.click();
    }
  });
  check.addEventListener("submit", event => {
    event.preventDefault();
    if (!validCurrentStep()) return;
    const data = new FormData(check);
    const problems = data.getAll("problem").join("; ") || "Keine Auswahl";
    const body = [
      "Website-Check",
      "",
      "Website: " + (data.get("website") || "-"),
      "Aktuelle Probleme: " + problems,
      "Ziel: " + data.get("ziel"),
      "Zusätzlicher Hinweis: " + (data.get("hinweis") || "-"),
      "",
      "Name: " + data.get("name"),
      "E-Mail: " + data.get("email"),
      "Telefon/WhatsApp: " + (data.get("telefon") || "-"),
      "Bevorzugte Antwort: " + data.get("kanal")
    ].join("\n");
    window.location.href = "mailto:" + check.dataset.to + "?subject=" + encodeURIComponent("Website-Check: " + data.get("name")) + "&body=" + encodeURIComponent(body);
    status.textContent = "Ihr E-Mail-Programm öffnet sich. Bitte senden Sie die vorbereitete Nachricht dort ab.";
  });
  // Reveal only after submit interception is installed; no-JS fallback is mailto.
  check.hidden = false;
}
