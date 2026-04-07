// ── Custom select (all .filter-select and .sort-select) ─────
function initCustomSelect(nativeSel) {
  if (!nativeSel || nativeSel.dataset.csInit) return;
  nativeSel.dataset.csInit = '1';

  var wrap = document.createElement('div');
  wrap.className = 'cs-wrap';

  var trigger = document.createElement('div');
  trigger.className = 'cs-trigger';

  var triggerText = document.createElement('span');
  triggerText.className = 'cs-text';
  triggerText.textContent = nativeSel.options[nativeSel.selectedIndex]
    ? nativeSel.options[nativeSel.selectedIndex].text : '';

  var arrow = document.createElement('span');
  arrow.className = 'cs-arrow';
  arrow.textContent = '▾';

  trigger.appendChild(triggerText);
  trigger.appendChild(arrow);

  var list = document.createElement('div');
  list.className = 'cs-list';

  Array.from(nativeSel.options).forEach(function (opt) {
    var item = document.createElement('div');
    item.className = 'cs-item' + (opt.selected ? ' selected' : '');
    item.textContent = opt.text;
    item.dataset.value = opt.value;
    item.addEventListener('click', function () {
      nativeSel.value = opt.value;
      triggerText.textContent = opt.text;
      list.querySelectorAll('.cs-item').forEach(function (i) { i.classList.remove('selected'); });
      item.classList.add('selected');
      closeList();
      // fire change for sort select
      nativeSel.dispatchEvent(new Event('change'));
    });
    list.appendChild(item);
  });

  wrap.appendChild(trigger);
  wrap.appendChild(list);

  nativeSel.style.display = 'none';
  nativeSel.parentNode.insertBefore(wrap, nativeSel);
  wrap.appendChild(nativeSel);

  function openList() {
    // close all other open lists
    document.querySelectorAll('.cs-list.open').forEach(function (l) { l.classList.remove('open'); });
    document.querySelectorAll('.cs-trigger.open').forEach(function (t) { t.classList.remove('open'); });
    trigger.classList.add('open');
    list.classList.add('open');
  }
  function closeList() { trigger.classList.remove('open'); list.classList.remove('open'); }

  trigger.addEventListener('click', function (e) {
    e.stopPropagation();
    list.classList.contains('open') ? closeList() : openList();
  });
  list.addEventListener('click', function (e) { e.stopPropagation(); });
  document.addEventListener('click', closeList);
}

document.querySelectorAll('.filter-select').forEach(initCustomSelect);

function applySort(val) {
  const url = new URL(window.location.href);
  url.searchParams.set('sort', val);
  window.location.href = url.toString();
}

function toggleFilters() {
  var sidebar = document.querySelector('.filters-sidebar');
  var overlay = document.getElementById('filter-overlay');
  var btn     = document.querySelector('.filter-toggle');
  var isOpen  = sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('open', isOpen);
  document.body.style.overflow = isOpen ? 'hidden' : '';
  if (btn) {
    btn.classList.toggle('active', isOpen);
    btn.textContent = isOpen ? '✕ Закрити' : 'Фільтри';
  }
}

document.querySelector('select.sort-select')?.addEventListener('change', function () {
  document.querySelector('input[name="sort"]').value = this.value;
});

var shownCount = 21;
function showMore() {
  var hidden = document.querySelectorAll('.hidden-card[style*="display:none"]');
  var toShow = Array.from(hidden).slice(0, 20);
  toShow.forEach(function (el) { el.style.display = ''; });
  shownCount += toShow.length;
  if (document.querySelectorAll('.hidden-card[style*="display:none"]').length === 0) {
    var wrap = document.getElementById('show-more-wrap');
    if (wrap) wrap.style.display = 'none';
  }
}
