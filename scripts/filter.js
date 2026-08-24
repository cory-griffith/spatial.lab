filterSelection("all");

function filterSelection(category) {
  var columns = document.getElementsByClassName("portcolumn");
  var filter = category === "all" ? "" : category;

  for (var i = 0; i < columns.length; i++) {
    removeClass(columns[i], "portshow");
    if (columns[i].className.indexOf(filter) > -1) {
      addClass(columns[i], "portshow");
    }
  }
}

function addClass(element, name) {
  var classes = element.className.split(" ");
  if (classes.indexOf(name) === -1) {
    element.className += " " + name;
  }
}

function removeClass(element, name) {
  var classes = element.className.split(" ");
  while (classes.indexOf(name) > -1) {
    classes.splice(classes.indexOf(name), 1);
  }
  element.className = classes.join(" ");
}

var btnContainer = document.getElementById("myBtnContainer");
if (btnContainer) {
  var buttons = btnContainer.getElementsByClassName("portbtn");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
      var current = btnContainer.getElementsByClassName("portactive");
      if (current.length > 0) {
        current[0].className = current[0].className.replace(" portactive", "");
      }
      this.className += " portactive";
    });
  }
}