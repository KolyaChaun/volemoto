function applySort(val) {
  const url = new URL(window.location.href);
  url.searchParams.set('sort', val);
  window.location.href = url.toString();
}

function toggleFilters() {
  document.querySelector('.filters-sidebar').classList.toggle('open');
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
