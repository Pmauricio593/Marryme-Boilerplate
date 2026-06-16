(function () {
  'use strict';

  if (typeof AOS !== 'undefined') {
    AOS.init({
      once: true,
      duration: 800,
      easing: 'ease-out-cubic',
      offset: 80
    });
  }

  if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
  }
})();
