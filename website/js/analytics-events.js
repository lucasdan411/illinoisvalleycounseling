/* GA4 conversion events for Illinois Valley Counseling (G-RQVFPHMK1H).
 * Requires the gtag.js snippet in <head>. Events:
 *   phone_call_click      click on a tel: link to the practice line (815) 993-1614
 *   crisis_line_click     click on a crisis line tel: link (988, 911, etc.), never a conversion
 *   callback_form_submit  submit of the callback form (#callbackForm), beacon transport
 *   generate_lead         thank-you page load after a FormSubmit redirect (canonical lead)
 *   cta_click             clicks on non-phone [data-track] elements (e.g. "Request a Call Back")
 */
(function () {
  'use strict';

  function send(name, params) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, params || {});
    }
  }

  function cleanText(el) {
    return (el.textContent || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 100);
  }

  // Best-effort description of where on the page a link lives.
  function locate(el) {
    var tracked = el.closest('[data-track]');
    if (tracked) return tracked.getAttribute('data-track');
    if (el.closest('.topbar')) return 'topbar';
    if (el.classList.contains('fab-call') || el.closest('.fab')) return 'fab-call';
    if (el.closest('.hero')) return 'hero';
    if (el.closest('nav, header, .mobile-menu')) return 'nav';
    if (el.closest('footer')) return 'footer';
    var section = el.closest('section[id], section[class], article, main');
    if (section) {
      if (section.id) return section.id;
      if (section.tagName === 'ARTICLE') return 'article';
      if (section.className) return String(section.className).split(/\s+/)[0];
      return section.tagName.toLowerCase();
    }
    return 'body';
  }

  // Practice line (815) 993-1614 is the only number that counts as phone_call_click.
  // Crisis lines (988, 911, legacy Lifeline 1-800-273-8255, Crisis Text Line 741741)
  // get their own crisis_line_click event so they never count as conversions.
  var PRACTICE_NUMBER = '8159931614';
  var CRISIS_NUMBERS = ['988', '911', '8002738255', '741741'];

  // Phone calls: one delegated listener covers every tel: link, including ones added later.
  document.addEventListener('click', function (e) {
    var target = e.target;
    if (!target || !target.closest) return;
    var link = target.closest('a[href^="tel:"]');
    if (link) {
      var href = link.getAttribute('href') || '';
      var digits = href.replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
      var eventName = null;
      if (digits === PRACTICE_NUMBER) eventName = 'phone_call_click';
      else if (CRISIS_NUMBERS.indexOf(digits) !== -1) eventName = 'crisis_line_click';
      if (eventName) {
        send(eventName, {
          link_url: href,
          link_text: cleanText(link),
          page_location: window.location.href,
          button_location: locate(link),
          transport_type: 'beacon'
        });
      }
      return;
    }
    var cta = target.closest('[data-track]');
    if (cta) {
      send('cta_click', {
        cta_name: cta.getAttribute('data-track'),
        link_url: cta.getAttribute('href') || '',
        link_text: cleanText(cta),
        page_location: window.location.href
      });
    }
  }, true);

  // Callback form submit (secondary signal; generate_lead fires on the thank-you page).
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (form && form.id === 'callbackForm') {
      send('callback_form_submit', {
        form_name: 'callback',
        page_location: window.location.href,
        transport_type: 'beacon'
      });
    }
  }, true);

  // Canonical lead conversion: FormSubmit redirects to /thank-you/#callback-success.
  var path = window.location.pathname.replace(/\/+$/, '');
  if (/\/thank-you(\.html)?$/.test(path)) {
    var isReload = false;
    try {
      var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
      isReload = !!(nav && nav.type === 'reload');
    } catch (err) {}
    if (!isReload) {
      send('generate_lead', { form_name: 'callback', page_location: window.location.href });
    }
  }
})();
