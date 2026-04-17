const PAGE_SIZE = 30;
let currentCat = 'all';
let shownCount = PAGE_SIZE;

function setCat(btn, cat) {
  currentCat = cat;
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters(true);
}

function showMore() {
  shownCount += PAGE_SIZE;
  applyFilters(false);
}

function applyFilters(reset) {
  if (reset === undefined || reset === true) shownCount = PAGE_SIZE;

  const q = document.getElementById('search-input').value.toLowerCase().trim();

  // --- Desktop table rows ---
  const rows = Array.from(document.querySelectorAll('#bikes-tbody tr[data-cat]'));
  const matchingRows = rows.filter(row => {
    const catOk    = currentCat === 'all' || row.dataset.cat === currentCat;
    const searchOk = !q || row.dataset.search.includes(q);
    return catOk && searchOk;
  });

  rows.forEach(row => row.style.display = 'none');
  matchingRows.slice(0, shownCount).forEach(row => row.style.display = '');

  const noResults = document.getElementById('no-results');
  if (noResults) noResults.style.display = matchingRows.length === 0 && rows.length > 0 ? 'block' : 'none';

  // --- Mobile cards ---
  const cards = Array.from(document.querySelectorAll('#mobile-bike-list .m-bike-card'));
  const matchingCards = cards.filter(card => {
    const catOk    = currentCat === 'all' || card.dataset.cat === currentCat;
    const searchOk = !q || card.dataset.search.includes(q);
    return catOk && searchOk;
  });

  cards.forEach(card => card.style.display = 'none');
  matchingCards.slice(0, shownCount).forEach(card => card.style.display = '');

  const mNoResults = document.getElementById('mobile-no-results');
  if (mNoResults) mNoResults.style.display = matchingCards.length === 0 && cards.length > 0 ? 'block' : 'none';

  // --- Title ---
  const total = matchingRows.length || matchingCards.length;
  const titleEl = document.getElementById('table-title');
  if (titleEl) titleEl.textContent = 'Оголошення (' + total + ')';

  // --- Show More button ---
  const btn = document.getElementById('show-more-btn');
  if (btn) {
    const hasMore = total > shownCount;
    btn.style.display = hasMore ? 'block' : 'none';
    if (hasMore) {
      const left = total - shownCount;
      btn.textContent = 'Показати ще ' + Math.min(left, PAGE_SIZE) + ' із ' + left;
    }
  }
}
