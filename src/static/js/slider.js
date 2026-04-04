let current = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');

function slideTo(n) {
  slides[current].classList.remove('active');
  dots[current].classList.remove('active');
  current = (n + slides.length) % slides.length;
  slides[current].classList.add('active');
  dots[current].classList.add('active');
}

function slideMove(dir) { slideTo(current + dir); }

setInterval(() => slideMove(1), 5000);
