/* Toggle the responsive navigation menu on smaller screens. */
function myFunction() {
  var nav = document.getElementById("mynavbar");
  if (!nav) return;

  if (nav.className === "navbar") {
    nav.className += " responsive";
  } else {
    nav.className = "navbar";
  }
}