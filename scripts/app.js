function updateBackground() {
  if (window.scrollY > window.innerHeight / 2) {
    document.body.classList.add("background_active");
  } else {
    document.body.classList.remove("background_active");
  }
}

function updateCopyrightYear() {
  var yearElements = document.getElementsByClassName("current-year");
  var currentYear = new Date().getFullYear();
  for (var i = 0; i < yearElements.length; i++) {
    yearElements[i].textContent = currentYear;
  }
}

window.addEventListener("scroll", updateBackground);
document.addEventListener("DOMContentLoaded", updateCopyrightYear);