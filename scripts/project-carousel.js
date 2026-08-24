(function () {
  'use strict';

  function initializeProjectCarousel(carousel) {
    var viewport = carousel.querySelector('.focus-carousel-viewport');
    var track = carousel.querySelector('.focus-card-track');
    var cards = Array.prototype.slice.call(carousel.querySelectorAll('.focus-card'));
    var previousButton = carousel.querySelector('.focus-carousel-prev');
    var nextButton = carousel.querySelector('.focus-carousel-next');
    var currentIndex = 0;

    if (!viewport || !track || !cards.length || !previousButton || !nextButton) {
      return;
    }

    function getVisibleCardCount() {
      if (window.matchMedia('(max-width: 650px)').matches) {
        return 1;
      }

      if (window.matchMedia('(max-width: 1000px)').matches) {
        return 2;
      }

      return 3;
    }

    function getGap() {
      var styles = window.getComputedStyle(track);
      return parseFloat(styles.columnGap || styles.gap) || 0;
    }

    function updateCarousel() {
      var visibleCards = getVisibleCardCount();
      var maximumIndex = Math.max(0, cards.length - visibleCards);
      var cardWidth = cards[0].getBoundingClientRect().width;
      var moveAmount;
      var controlsNeeded = cards.length > visibleCards;

      currentIndex = Math.min(currentIndex, maximumIndex);
      moveAmount = currentIndex * (cardWidth + getGap());

      track.style.transform = 'translateX(-' + moveAmount + 'px)';

      previousButton.disabled = currentIndex === 0;
      nextButton.disabled = currentIndex >= maximumIndex;

      previousButton.classList.toggle('is-hidden', !controlsNeeded);
      nextButton.classList.toggle('is-hidden', !controlsNeeded);
    }

    previousButton.addEventListener('click', function () {
      if (currentIndex > 0) {
        currentIndex -= 1;
        updateCarousel();
      }
    });

    nextButton.addEventListener('click', function () {
      var maximumIndex = Math.max(0, cards.length - getVisibleCardCount());

      if (currentIndex < maximumIndex) {
        currentIndex += 1;
        updateCarousel();
      }
    });

    carousel.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowLeft' && !previousButton.disabled) {
        currentIndex -= 1;
        updateCarousel();
      } else if (event.key === 'ArrowRight' && !nextButton.disabled) {
        currentIndex += 1;
        updateCarousel();
      }
    });

    var resizeTimer;
    window.addEventListener('resize', function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(updateCarousel, 100);
    });

    updateCarousel();
  }

  function initializeAllProjectCarousels() {
    var carousels = document.querySelectorAll('[data-project-carousel]');
    Array.prototype.forEach.call(carousels, initializeProjectCarousel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAllProjectCarousels);
  } else {
    initializeAllProjectCarousels();
  }
}());