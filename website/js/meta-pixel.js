/* Meta Pixel for Illinois Valley Counseling (pixel 1128636546211662).
 * Privacy-minimal setup for a counseling practice:
 *   - autoConfig disabled (no automatic event/button scraping, no automatic advanced matching)
 *   - no user data / advanced matching passed to init
 *   - events: PageView (all public pages), Lead (thank-you page after callback form success),
 *     Contact (click on the practice phone number only; crisis lines never tracked)
 *   - only on illinoisvalleycounseling.com / www (never preview or pages.dev hosts)
 *   - never loads on /admin/; on thank-you, skipped if the URL carries a query string
 */
(function () {
  'use strict';
  var ID = '1128636546211662';
  var host = window.location.hostname;
  if (host !== 'illinoisvalleycounseling.com' && host !== 'www.illinoisvalleycounseling.com') return;
  var path = window.location.pathname || '/';
  if (/^\/admin(\/|$)/.test(path)) return;
  var isThankYou = /^\/thank-you(\.html)?\/?$/.test(path);
  if (isThankYou && window.location.search) return;

  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');

  window.fbq('set', 'autoConfig', false, ID);
  window.fbq('init', ID);
  window.fbq('track', 'PageView');
  if (isThankYou) window.fbq('track', 'Lead');

  document.addEventListener('click', function (e) {
    var link = e.target && e.target.closest && e.target.closest('a[href^="tel:"]');
    if (!link) return;
    var digits = (link.getAttribute('href') || '').replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
    if (digits === '8159931614') window.fbq('track', 'Contact');
  }, true);
})();
