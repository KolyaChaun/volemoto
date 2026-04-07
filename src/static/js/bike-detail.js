// ── GALLERY ──────────────────────────────
let cur = 0;
const gImgs   = [...document.querySelectorAll('#gMain img')];
const gYt     = document.querySelector('#gMain .g-yt-slide');
const gThumbs = [...document.querySelectorAll('.g-thumb')];
const gCount  = document.getElementById('gCounter');
const totalSlides = gImgs.length + (gYt ? 1 : 0);

function gTo(n) {
  if (!totalSlides) return;
  // deactivate current
  if (cur < gImgs.length) gImgs[cur].classList.remove('active');
  else if (gYt) { gYt.classList.remove('active'); stopYt(); }
  if (gThumbs[cur]) gThumbs[cur].classList.remove('active');

  cur = (n + totalSlides) % totalSlides;

  // activate new
  if (cur < gImgs.length) {
    gImgs[cur].classList.add('active');
  } else if (gYt) {
    gYt.classList.add('active');
    playYt();
  }
  if (gThumbs[cur]) { gThumbs[cur].classList.add('active'); gThumbs[cur].scrollIntoView({block:'nearest',inline:'center'}); }
  if (gCount) gCount.textContent = (cur + 1) + ' / ' + totalSlides;
}
function gMove(d) { gTo(cur + d); }

function playYt() {
  if (!gYt) return;
  const iframe = gYt.querySelector('iframe');
  const id = gYt.dataset.ytId;
  if (iframe && id) iframe.src = 'https://www.youtube.com/embed/' + id + '?autoplay=1';
}
function stopYt() {
  if (!gYt) return;
  const iframe = gYt.querySelector('iframe');
  if (iframe) iframe.src = '';
}

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
