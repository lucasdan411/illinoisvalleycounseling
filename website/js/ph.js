/* PostHog for Illinois Valley Counseling (project 678054, site=ivcs). v1
 * Privacy: no session replay, no surveys, no heatmaps, no person profiles unless identified (never),
 * autocapture limited to clicks on <a>/<button>, forms marked ph-no-capture, query strings stripped
 * (except utm_*, gclid, fbclid). Not loaded on /thank-you or /admin. */
(function () {
  'use strict';
  var p = location.pathname;
  if (/^\/(admin)(\/|$)/i.test(p) || /^\/thank-you(\.html)?\/?$/i.test(p)) return;

  !function(t,e){var o,n,p,r;e.__SV||(window.posthog&&window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag on identify setPersonProperties reset get_distinct_id get_session_id set_config startSessionRecording stopSessionRecording opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing get_property".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

  var KEEP = /^(utm_[a-z_]+|gclid|fbclid)$/i;
  function cleanUrl(u) {
    if (typeof u !== 'string' || !u) return u;
    try {
      var x = new URL(u, location.origin), keep = [];
      x.searchParams.forEach(function (v, k) { if (KEEP.test(k)) keep.push(encodeURIComponent(k) + '=' + encodeURIComponent(v)); });
      x.search = keep.length ? '?' + keep.join('&') : '';
      x.hash = '';
      return x.toString();
    } catch (e) { return u.split(/[?#]/)[0]; }
  }
  function cleanPath(v) { return typeof v === 'string' ? v.split(/[?#]/)[0] : v; }
  var URL_KEYS = ['$current_url', '$referrer', '$initial_referrer', '$initial_current_url', '$prev_pageview_pathname', '$host'];
  var PATH_KEYS = ['$pathname', '$initial_pathname', '$prev_pageview_pathname'];

  function scrub(obj) {
    if (!obj) return;
    URL_KEYS.forEach(function (k) { if (typeof obj[k] === 'string' && /^https?:/i.test(obj[k])) obj[k] = cleanUrl(obj[k]); });
    PATH_KEYS.forEach(function (k) { if (obj[k]) obj[k] = cleanPath(obj[k]); });
  }

  posthog.init('phc_s9EPZmHkGhcqtDqJwyNLgFy7XM4HK2WLo45zUKDJe7xt', {
    api_host: 'https://us.i.posthog.com',
    ui_host: 'https://us.posthog.com',
    person_profiles: 'identified_only',
    disable_session_recording: true,
    disable_surveys: true,
    enable_heatmaps: false,
    capture_heatmaps: false,
    capture_dead_clicks: false,
    capture_performance: false,
    capture_exceptions: false,
    capture_pageview: true,
    capture_pageleave: true,
    autocapture: { dom_event_allowlist: ['click'], element_allowlist: ['a', 'button'], capture_copied_text: false },
    mask_all_element_attributes: true,
    mask_all_text: false,
    advanced_disable_feature_flags: true,
    before_send: function (e) {
      if (!e) return e;
      try {
        scrub(e.properties); scrub(e.$set); scrub(e.$set_once);
        if (e.properties && e.properties.$set) scrub(e.properties.$set);
        if (e.properties && e.properties.$set_once) scrub(e.properties.$set_once);
        // Never send element chains that originate inside a form
        if (e.event === '$autocapture' && e.properties && Array.isArray(e.properties.$elements) &&
            e.properties.$elements.some(function (el) { return el.tag_name === 'form' || el.tag_name === 'input' || el.tag_name === 'textarea' || el.tag_name === 'select'; })) return null;
      } catch (x) {}
      return e;
    },
    loaded: function (ph) { ph.register({ site: 'ivcs' }); }
  });
  posthog.register({ site: 'ivcs' });

  function cap(name, props) { try { posthog.capture(name, props, { transport: 'sendBeacon' }); } catch (x) {} }

  function phoneLocation(a) {
    var t = (a.getAttribute('data-track') || '').toLowerCase();
    if (a.closest('footer')) return 'footer';
    if (/top/.test(t) || a.closest('.top-callbar,.quick-callback-bar,#top-callbar')) return 'top-bar';
    if (/hero/.test(t) || a.closest('.hero,.hero-intro')) return 'hero';
    if (/bottom|box/.test(t)) return 'box';
    return t || 'inline';
  }

  document.addEventListener('click', function (ev) {
    try {
      var a = ev.target && ev.target.closest && ev.target.closest('a,button');
      if (!a || a.closest('form')) return;
      var href = a.getAttribute('href') || '';
      var track = a.getAttribute('data-track') || '';
      if (/^tel:/i.test(href)) {
        var num = href.replace(/[^0-9]/g, '');
        return cap('phone_click', { location: phoneLocation(a), line: /8159931614$/.test(num) ? 'practice' : 'crisis', data_track: track || null, page: location.pathname });
      }
      if (/^mailto:/i.test(href)) return cap('email_click', { location: a.closest('footer') ? 'footer' : 'inline', page: location.pathname });
      var txt = (a.innerText || a.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
      if (track || /call ?back|call me back|book|schedule|first step/i.test(txt) || /#contact$/.test(href)) {
        return cap('cta_click', { data_track: track || null, cta_text: txt, page: location.pathname });
      }
      var card = a.closest('.therapist-card') || (ev.target.closest && ev.target.closest('.therapist-card'));
      if (card) { var h = card.querySelector('h3'); cap('therapist_profile_view', { therapist: h ? h.textContent.trim() : null }); }
    } catch (x) {}
  }, true);

  // Therapist photo clicks (open lightbox) on /our-staff/
  document.addEventListener('click', function (ev) {
    try {
      var w = ev.target.closest && ev.target.closest('.therapist-photo-wrap');
      if (!w) return;
      var card = w.closest('.therapist-card'), h = card && card.querySelector('h3');
      cap('therapist_profile_view', { therapist: h ? h.textContent.trim() : null, page: location.pathname });
    } catch (x) {}
  }, true);

  function formLabel(f) {
    var d = f.getAttribute('data-callback-form');
    if (d) return d;
    if (f.id === 'callbackForm') return 'home-cta';
    return f.id || 'form';
  }
  document.addEventListener('submit', function (ev) {
    try {
      var f = ev.target;
      if (!f || f.tagName !== 'FORM') return;
      cap('ivcs_contact_submitted', { form: formLabel(f), page: location.pathname });
    } catch (x) {}
  }, true);
})();
