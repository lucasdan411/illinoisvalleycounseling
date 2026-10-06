/* Floating action buttons: show while scrolling back up; always hide near the footer
 * so they never cover Privacy/Terms (or other) footer links.
 */
(function () {
  'use strict';

  var fabs = [
    document.getElementById('fabTop'),
    document.getElementById('fabCall'),
    document.getElementById('fabCallback')
  ].filter(Boolean);

  if (!fabs.length) return;

  var footerNear = false;
  var lastScroll = window.pageYOffset || document.documentElement.scrollTop;
  var hideTimer = null;

  function setHidden(hidden) {
    fabs.forEach(function (f) {
      f.classList.toggle('fab-hidden', hidden);
    });
  }

  function showFabs() {
    if (footerNear) return;
    fabs.forEach(function (f) {
      f.classList.add('show');
      f.classList.remove('fab-hidden');
    });
  }

  function hideFabs() {
    fabs.forEach(function (f) {
      f.classList.remove('show');
    });
  }

  function footerIsNear() {
    var footer = document.querySelector('footer');
    if (!footer) {
      // Fallback: near document bottom (footer height + FAB stack ~ 220px)
      var doc = document.documentElement;
      var remaining = doc.scrollHeight - (window.pageYOffset + window.innerHeight);
      return remaining < 220;
    }
    var rect = footer.getBoundingClientRect();
    // Hide once the footer top enters (or is within ~24px of) the viewport bottom
    return rect.top < window.innerHeight - 24;
  }

  function syncFooter() {
    var near = footerIsNear();
    if (near === footerNear) return;
    footerNear = near;
    if (footerNear) {
      clearTimeout(hideTimer);
      setHidden(true);
      hideFabs();
    } else {
      setHidden(false);
    }
  }

  var footer = document.querySelector('footer');
  if (footer && 'IntersectionObserver' in window) {
    try {
      new IntersectionObserver(
        function (entries) {
          footerNear = entries.some(function (e) {
            return e.isIntersecting;
          });
          if (footerNear) {
            clearTimeout(hideTimer);
            setHidden(true);
            hideFabs();
          } else {
            setHidden(false);
          }
        },
        // Expand the root downward so we hide slightly before the footer hits the FABs
        { root: null, rootMargin: '0px 0px -24px 0px', threshold: 0 }
      ).observe(footer);
    } catch (err) {
      // Fall through to scroll-based footer check below
      footer = null;
    }
  }

  window.addEventListener(
    'scroll',
    function () {
      var y = window.pageYOffset || document.documentElement.scrollTop;
      var scrollingUp = y < lastScroll;

      // Keep footer check current when IntersectionObserver is unavailable
      if (!('IntersectionObserver' in window) || !document.querySelector('footer')) {
        syncFooter();
      } else {
        // Also re-check on scroll: rootMargin alone can miss edge cases on short pages
        var near = footerIsNear();
        if (near !== footerNear) {
          footerNear = near;
          if (footerNear) {
            clearTimeout(hideTimer);
            setHidden(true);
            hideFabs();
          } else {
            setHidden(false);
          }
        }
      }

      if (footerNear) {
        lastScroll = y;
        return;
      }

      if (scrollingUp && y > 300) {
        showFabs();
        clearTimeout(hideTimer);
        hideTimer = setTimeout(hideFabs, 2000);
      } else if (!scrollingUp && y > 300) {
        hideFabs();
      } else if (y <= 300) {
        hideFabs();
      }
      lastScroll = y;
    },
    { passive: true }
  );

  // Initial state (e.g. deep-linked near bottom)
  syncFooter();
})();
