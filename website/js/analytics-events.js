/* GA4 conversion events for Illinois Valley Counseling (G-RQVFPHMK1H).
 * Requires the gtag.js snippet in <head>. Events:
 *   phone_call_click      any click on an a[href^="tel:"] link (event delegation)
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

  // Phone calls: one delegated listener covers every tel: link, including ones added later.
  document.addEventListener('click', function (e) {
    var target = e.target;
    if (!target || !target.closest) return;
    var link = target.closest('a[href^="tel:"]');
    if (link) {
      send('phone_call_click', {
        link_url: link.getAttribute('href'),
        link_text: cleanText(link),
        page_location: window.location.href,
        button_location: locate(link),
        transport_type: 'beacon'
      });
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
