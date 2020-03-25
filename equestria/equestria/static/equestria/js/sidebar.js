$(document).ready(function () {
  var trigger = $('.hamburger'),
      overlay = $('#overlay'),
     isClosed = false;
      //overlay.removeClass('overlay');
    overlay.show();

    trigger.click(function () {
      hamburger_cross();
    });

    function hamburger_cross() {

      if (isClosed == true) {
        overlay.removeClass('overlay');
        trigger.removeClass('is-open');
        trigger.addClass('is-closed');
        isClosed = false;
      } else {
        overlay.addClass('overlay');
        trigger.removeClass('is-closed');
        trigger.addClass('is-open');
        isClosed = true;
      }
  }

  $('[data-toggle="offcanvas"]').click(function () {
        $('#wrapper').toggleClass('toggled');
  });
});