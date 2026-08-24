var slideIndex = 1;

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  var slides = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("dot");
  if (slides.length === 0) return;

  if (n > slides.length) slideIndex = 1;
  if (n < 1) slideIndex = slides.length;

  for (var i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (var j = 0; j < dots.length; j++) {
    dots[j].className = dots[j].className.replace(" activehover", "");
  }

  slides[slideIndex - 1].style.display = "block";
  if (dots.length >= slideIndex) {
    dots[slideIndex - 1].className += " activehover";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  showSlides(slideIndex);
});