let currentCat = 'all';

function setCat(btn, cat) {
  currentCat = cat;
  document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function applyFilters() {
  const q = document.getElementById('search-input').value.toLowerCase().trim();
  const rows = document.querySelectorAll('#bikes-tbody tr[data-cat]');
  let count = 0;
  rows.forEach(row => {
    const catOk    = currentCat === 'all' || row.dataset.cat === currentCat;
    const searchOk = !q || row.dataset.search.includes(q);
    const show = catOk && searchOk;
    row.style.display = show ? '' : 'none';
    if (show) count++;
  });
  document.getElementById('table-title').textContent = 'Оголошення (' + count + ')';
  document.getElementById('no-results').style.display = count === 0 ? 'block' : 'none';
}
