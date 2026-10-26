/* GA4 conversion events for Illinois Valley Counseling (G-RQVFPHMK1H).
 * Requires the gtag.js snippet in <head>. Events:
 *   phone_call_click      click on a tel: link to the practice line (815) 993-1614
 *   crisis_line_click     click on a crisis line tel: link (988, 911, etc.), never a conversion
 *   callback_form_submit  submit of the callback form (#callbackForm), beacon transport
 *   generate_lead         thank-you page load after a FormSubmit redirect (canonical lead)
 *   cta_click             clicks on non-phone [data-track] elements (e.g. "Request a Call Back")
 * Lead attribution: the landing source (utm_*, gclid, fbclid, referrer, first page) is stored
 * in sessionStorage (this visit) and localStorage (30 day backup) and sent with generate_lead,
 * so leads keep their true source even though the FormSubmit hop looks like Direct.
 */
(function () {
  'use strict';

  // ---- Lead attribution capture ----
  var ATTR_KEY = 'ivcs_attr';
  var ATTR_TTL = 30 * 24 * 3600 * 1000;
  var path = window.location.pathname.replace(/\/+$/, '');
  var isThankYou = /\/thank-you(\.html)?$/.test(path);

  function readStore(store) {
    try { var v = JSON.parse(store.getItem(ATTR_KEY) || 'null'); return v && typeof v === 'object' ? v : null; } catch (e) { return null; }
  }
  function writeStore(store, v) { try { store.setItem(ATTR_KEY, JSON.stringify(v)); } catch (e) {} }

  function refHost(ref) {
    try { return ref ? new URL(ref).hostname.replace(/^www\./, '') : ''; } catch (e) { return ''; }
  }
  function classify(a) {
    if (a.utm_source || a.utm_medium) return { source: a.utm_source || '(not set)', medium: a.utm_medium || '(not set)' };
    if (a.gclid) return { source: 'google', medium: 'cpc' };
    if (a.fbclid) return { source: 'facebook', medium: 'paid_or_social' };
    var h = a.referrer_host;
    if (!h) return { source: '(direct)', medium: '(none)' };
    if (/(^|\.)google\.|bing\.com|yahoo\.|duckduckgo\.com|ecosia\.org/.test(h)) return { source: h.split('.').slice(-2, -1)[0] || h, medium: 'organic' };
    if (/facebook\.com|instagram\.com|fb\.me|t\.co|x\.com|linkedin\.com/.test(h)) return { source: h, medium: 'social' };
    return { source: h, medium: 'referral' };
  }

  function captureAttribution() {
    var q = new URLSearchParams(window.location.search);
    var ref = document.referrer || '';
    var rh = refHost(ref);
    var internal = rh === 'illinoisvalleycounseling.com' || rh === 'formsubmit.co';
    var a = {
      utm_source: q.get('utm_source') || '', utm_medium: q.get('utm_medium') || '',
      utm_campaign: q.get('utm_campaign') || '', utm_term: q.get('utm_term') || '', utm_content: q.get('utm_content') || '',
      gclid: q.get('gclid') || q.get('gbraid') || q.get('wbraid') || '', fbclid: q.get('fbclid') || '',
      referrer_host: internal ? '' : rh,
      landing_page: window.location.pathname,
      ts: Date.now()
    };
    var hasSignal = a.utm_source || a.utm_medium || a.gclid || a.fbclid || a.referrer_host;
    // This visit: keep the first touch unless a new campaign signal arrives.
    var sess = readStore(window.sessionStorage);
    if (!sess || (hasSignal && !internal)) writeStore(window.sessionStorage, a);
    // 30 day backup: only overwrite with a real (non-direct) touch.
    var loc = readStore(window.localStorage);
    if (hasSignal || !loc || (Date.now() - (loc.ts || 0)) > ATTR_TTL) writeStore(window.localStorage, a);
  }

  function leadParams() {
    var s = readStore(window.sessionStorage);
    var l = readStore(window.localStorage);
    if (l && (Date.now() - (l.ts || 0)) > ATTR_TTL) l = null;
    var sDirect = !s || !(s.utm_source || s.utm_medium || s.gclid || s.fbclid || s.referrer_host);
    var a = (sDirect && l) ? l : (s || l || {});
    var c = classify(a);
    return {
      lead_source: c.source, lead_medium: c.medium,
      lead_campaign: a.utm_campaign || '', lead_term: a.utm_term || '', lead_content: a.utm_content || '',
      lead_gclid_present: a.gclid ? 'yes' : 'no', lead_fbclid_present: a.fbclid ? 'yes' : 'no',
      lead_referrer: a.referrer_host || '', lead_landing_page: a.landing_page || '',
      lead_attr_scope: (sDirect && l) ? 'returning' : 'session'
    };
  }

  if (!isThankYou) captureAttribution();

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
        transport_type: 'beacon',
        event_callback: function () {},
        event_timeout: 1000
      });
    }
  }, true);

  // Canonical lead conversion: FormSubmit redirects to /thank-you/#callback-success.
  if (isThankYou) {
    var isReload = false;
    try {
      var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
      isReload = !!(nav && nav.type === 'reload');
    } catch (err) {}
    if (!isReload) {
      var lp = leadParams();
      lp.form_name = 'callback';
      lp.page_location = window.location.href;
      send('generate_lead', lp);
    }
  }
})();
