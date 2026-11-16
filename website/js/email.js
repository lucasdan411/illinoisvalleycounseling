/* Assemble contact mailto links at runtime so the address is not in the HTML source. */
(function () {
  function apply() {
    var nodes = document.querySelectorAll('a.js-email');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var user = el.getAttribute('data-u') || '';
      var domain = el.getAttribute('data-d') || '';
      if (!user || !domain) continue;
      var addr = user + '@' + domain;
      el.setAttribute('href', 'mailto:' + addr);
      el.textContent = addr;
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
})();
