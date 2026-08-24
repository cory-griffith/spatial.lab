document.addEventListener("DOMContentLoaded", function() {
  var images = document.querySelectorAll("img[data-src]");

  if (!("IntersectionObserver" in window)) {
    for (var i = 0; i < images.length; i++) {
      images[i].src = images[i].dataset.src;
    }
    return;
  }

  var observer = new IntersectionObserver(function(entries, imageObserver) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var image = entry.target;
        image.src = image.dataset.src;
        image.removeAttribute("data-src");
        imageObserver.unobserve(image);
      }
    });
  });

  images.forEach(function(image) {
    observer.observe(image);
  });
});