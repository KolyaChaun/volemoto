// Inject phone-tip animation styles once
(function () {
  var s = document.createElement('style');
  s.textContent = [
    '@keyframes phoneTipIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}',
    '.phone-tip{animation:phoneTipIn .15s ease}'
  ].join('');
  document.head.appendChild(s);
})();

var COPY_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>';
var CHECK_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';

function openPhone(e) {
  e.preventDefault();
  e.stopPropagation();
  if (/Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent)) {
    window.location.href = 'tel:+380997558803';
    return;
  }
  var btn = e.currentTarget;
  var tip = btn.nextElementSibling;
  if (!tip || !tip.classList.contains('phone-tip')) return;
  if (tip.style.display === 'flex') {
    tip.style.display = 'none';
    return;
  }
  if (tip.dataset.fixed) {
    var rect = btn.getBoundingClientRect();
    tip.style.top = (rect.bottom + 8) + 'px';
    tip.style.left = '0px';
    tip.style.right = 'auto';
    tip.style.visibility = 'hidden';
    tip.style.display = 'flex';
    var tipWidth = tip.offsetWidth;
    tip.style.display = 'none';
    tip.style.visibility = '';
    var leftPos = rect.left;
    if (leftPos + tipWidth > window.innerWidth - 8) {
      leftPos = window.innerWidth - tipWidth - 8;
    }
    if (leftPos < 8) { leftPos = 8; }
    tip.style.left = leftPos + 'px';
    tip.style.width = tipWidth + 'px';
  }
  tip.style.display = 'flex';
  setTimeout(function () {
    function hide() {
      tip.style.display = 'none';
      document.removeEventListener('click', hide);
      window.removeEventListener('scroll', hide);
    }
    document.addEventListener('click', hide);
    window.addEventListener('scroll', hide, { passive: true });
  }, 0);
}

function copyPhone(btn, e) {
  if (e) { e.stopPropagation(); }
  function onCopied() {
    btn.innerHTML = CHECK_ICON;
    btn.style.background = '#f0f7ee';
    btn.style.color = '#2d9e00';
    setTimeout(function () {
      btn.innerHTML = COPY_ICON + ' Копіювати';
    }, 2000);
  }
  var number = '+380997558803';
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(number).then(onCopied);
  } else {
    var ta = document.createElement('textarea');
    ta.value = number;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    onCopied();
  }
}

function openViber(e) {
  e.preventDefault();
  var appOpened = false;
  window.addEventListener('blur', function () { appOpened = true; }, { once: true });
  window.location.href = 'viber://chat?number=%2B380997558803';
  setTimeout(function () {
    if (!appOpened) {
      var tip = document.getElementById('viber-tip');
      if (tip) { tip.style.display = 'block'; setTimeout(function () { tip.style.display = 'none'; }, 5000); }
    }
  }, 600);
}
