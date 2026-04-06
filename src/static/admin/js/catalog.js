let currentCat = 'all';

function setCat(btn, cat) {
  currentCat = cat;
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function applyFilters() {
  const q = document.getElementById('search-input').value.toLowerCase().trim();

  // Desktop table rows
  const rows = document.querySelectorAll('#bikes-tbody tr[data-cat]');
  let count = 0;
  rows.forEach(row => {
    const catOk    = currentCat === 'all' || row.dataset.cat === currentCat;
    const searchOk = !q || row.dataset.search.includes(q);
    const show = catOk && searchOk;
    row.style.display = show ? '' : 'none';
    if (show) count++;
  });
  document.getElementById('no-results').style.display = count === 0 && rows.length > 0 ? 'block' : 'none';

  // Mobile cards
  const cards = document.querySelectorAll('#mobile-bike-list .m-bike-card');
  let mCount = 0;
  cards.forEach(card => {
    const catOk    = currentCat === 'all' || card.dataset.cat === currentCat;
    const searchOk = !q || card.dataset.search.includes(q);
    const show = catOk && searchOk;
    card.style.display = show ? '' : 'none';
    if (show) mCount++;
  });
  const mNoResults = document.getElementById('mobile-no-results');
  if (mNoResults) mNoResults.style.display = mCount === 0 && cards.length > 0 ? 'block' : 'none';

  document.getElementById('table-title').textContent = 'Оголошення (' + (count || mCount) + ')';
}
