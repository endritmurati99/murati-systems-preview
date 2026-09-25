// Übernimmt die Website-Adresse aus dem Feld der Startseite (?website=...) in den Website-Check.
const websiteField = document.querySelector('#formular input[name="website"]');
const givenWebsite = new URLSearchParams(location.search).get("website");
if (websiteField && givenWebsite) websiteField.value = givenWebsite.trim().slice(0, 250);
