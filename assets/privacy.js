// No consent or preference is stored: there are no optional services.
const privacyDialog = document.getElementById("cookie-dialog");
if (privacyDialog && typeof privacyDialog.showModal === "function") {
  document.querySelectorAll("[data-cookie-info]").forEach(link => {
    link.addEventListener("click", event => {
      event.preventDefault();
      privacyDialog.showModal();
    });
  });
  privacyDialog.querySelector("[data-cookie-close]").addEventListener("click", () => privacyDialog.close());
}
