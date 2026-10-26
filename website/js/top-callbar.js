/* Slim fixed top call bar. Tracking is handled by /js/analytics-events.js:
 * tel: link -> phone_call_click (button_location "top-callbar-call"); callback link -> cta_click. */
(function () {
  'use strict';
  var form = document.getElementById('callback-top');
  var bar = document.createElement('div');
  bar.className = 'top-callbar';
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', 'Contact');
  bar.innerHTML = '<a href="tel:8159931614" class="tcb-call" data-track="top-callbar-call">Call (815) 993-1614</a>' +
    '<a href="' + (form ? '#callback-top' : '/#callback-top') + '" class="tcb-callback" data-track="top-callbar-callback">Request a Call Back</a>';
  document.body.insertBefore(bar, document.body.firstChild);
  if (form) bar.querySelector('.tcb-callback').addEventListener('click', function (e) {
    e.preventDefault();
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    var f = form.querySelector('input[name="name"]');
    if (f) setTimeout(function () { try { f.focus({ preventScroll: true }); } catch (x) {} }, 600);
  });
})();
