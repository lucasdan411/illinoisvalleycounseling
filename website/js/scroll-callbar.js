/* Slim Call / Request a Call Back bar. Hidden by default; shows only after the top callback
 * block (#callback-top) has scrolled out of view AND the user scrolls back up. Hides on scroll
 * down and whenever the top block is visible. Clicks are tracked by /js/analytics-events.js:
 * tel: link -> phone_call_click (button_location "scroll-bar-call"), the callback link -> cta_click. */
(function () {
  'use strict';
  var top = document.getElementById('callback-top');
  if (!top) return;
  var bar = document.createElement('div');
  bar.className = 'scroll-callbar';
  bar.setAttribute('aria-hidden', 'true');
  bar.innerHTML = '<a href="tel:8159931614" class="scb-call" data-track="scroll-bar-call" tabindex="-1">Call</a>' +
    '<a href="#callback-top" class="scb-callback" data-track="scroll-bar-callback" tabindex="-1">Request a Call Back</a>';
  document.body.appendChild(bar);
  var links = bar.querySelectorAll('a');
  var topVisible = true, lastY = window.pageYOffset, shown = false;
  function set(v) {
    if (v === shown) return; shown = v;
    bar.classList.toggle('is-visible', v);
    document.body.classList.toggle('scb-on', v);
    bar.setAttribute('aria-hidden', v ? 'false' : 'true');
    for (var i = 0; i < links.length; i++) links[i].tabIndex = v ? 0 : -1;
  }
  function pastTop() { return top.getBoundingClientRect().bottom < 0; }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { topVisible = es[0].isIntersecting; if (topVisible) set(false); }).observe(top);
  }
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var y = window.pageYOffset, dy = y - lastY;
      if (Math.abs(dy) < 6) return;
      lastY = y;
      if (topVisible && !pastTop() || y < 50) { set(false); return; }
      if (!('IntersectionObserver' in window) && !pastTop()) { set(false); return; }
      set(dy < 0);
    });
  }, { passive: true });
  bar.querySelector('.scb-callback').addEventListener('click', function (e) {
    e.preventDefault(); set(false);
    top.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var f = top.querySelector('input[name="name"]');
    if (f) setTimeout(function () { try { f.focus({ preventScroll: true }); } catch (x) {} }, 600);
  });
})();
