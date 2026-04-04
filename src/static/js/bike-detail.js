// ── GALLERY ──────────────────────────────
let cur = 0;
const gImgs   = [...document.querySelectorAll('#gMain img')];
const gThumbs = [...document.querySelectorAll('.g-thumb')];
const gCount  = document.getElementById('gCounter');

function gTo(n) {
  if (!gImgs.length) return;
  gImgs[cur].classList.remove('active');
  if (gThumbs[cur]) gThumbs[cur].classList.remove('active');
  cur = (n + gImgs.length) % gImgs.length;
  gImgs[cur].classList.add('active');
  if (gThumbs[cur]) { gThumbs[cur].classList.add('active'); gThumbs[cur].scrollIntoView({block:'nearest',inline:'center'}); }
  if (gCount) gCount.textContent = (cur + 1) + ' / ' + gImgs.length;
}
function gMove(d) { gTo(cur + d); }

document.addEventListener('keydown', e => {
  if (document.getElementById('lightbox').classList.contains('open')) return;
  if (e.key === 'ArrowLeft')  gMove(-1);
  if (e.key === 'ArrowRight') gMove(1);
});

// ── LIGHTBOX ─────────────────────────────
const lbEl  = document.getElementById('lightbox');
const lbImg = document.getElementById('lbImg');
const srcs  = gImgs.map(i => i.src);

function lbOpen(n) {
  if (!srcs.length) return;
  cur = n;
  lbImg.src = srcs[cur];
  lbEl.classList.add('open');
}
function lbClose(e) {
  if (!e || e.target === lbEl || e.currentTarget === lbEl) {
    lbEl.classList.remove('open');
  }
}
function lbMove(d) {
  if (!srcs.length) return;
  cur = (cur + d + srcs.length) % srcs.length;
  lbImg.src = srcs[cur];
  gTo(cur);
}
document.addEventListener('keydown', e => {
  if (!lbEl.classList.contains('open')) return;
  if (e.key === 'Escape')     lbClose({target: lbEl});
  if (e.key === 'ArrowLeft')  lbMove(-1);
  if (e.key === 'ArrowRight') lbMove(1);
});
