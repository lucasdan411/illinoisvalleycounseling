/* Google Ads conversion tracking for Illinois Valley Counseling (AW-18513555206).
 * Reuses the GA4 gtag.js already loaded in <head>.
 *   Website phone tap (7859547037)    tap on the practice number (815) 993-1614 only; crisis lines never
 *   Callback form submit (7859547040) thank-you page load after callback form success (skipped with a query string)
 * Privacy: user_data forced empty (blocks automatic enhanced-conversion page scraping), enhanced conversions off, ad personalization signals off.
 * Runs only on illinoisvalleycounseling.com / www, never on /admin/.
 */
(function () {
  'use strict';
  var AW = 'AW-18513555206';
  var PHONE_LABEL = AW + '/YEwCCJ3X3KMdEIbe-ftE';
  var FORM_LABEL = AW + '/neEhCKDX3KMdEIbe-ftE';
  var host = window.location.hostname;
  if (host !== 'illinoisvalleycounseling.com' && host !== 'www.illinoisvalleycounseling.com') return;
  var path = window.location.pathname || '/';
  if (/^\/admin(\/|$)/.test(path)) return;

  window.dataLayer = window.dataLayer || [];
  var gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag = gtag;

  gtag('set', 'user_data', {});
  gtag('config', AW, {
    allow_ad_personalization_signals: false,
    allow_enhanced_conversions: false
  });

  if (/^\/thank-you(\.html)?\/?$/.test(path) && !window.location.search) {
    gtag('event', 'conversion', { send_to: FORM_LABEL, user_data: {} });
  }

  document.addEventListener('click', function (e) {
    var link = e.target && e.target.closest && e.target.closest('a[href^="tel:"]');
    if (!link) return;
    var digits = (link.getAttribute('href') || '').replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
    if (digits === '8159931614') {
      gtag('event', 'conversion', { send_to: PHONE_LABEL, user_data: {}, transport_type: 'beacon' });
    }
  }, true);
})();
