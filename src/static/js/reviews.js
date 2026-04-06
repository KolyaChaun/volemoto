function toggleReply(id) {
  const form = document.getElementById('reply-form-' + id);
  if (!form) return;
  form.classList.toggle('open');
  if (form.classList.contains('open')) {
    setTimeout(() => form.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const cta = document.querySelector('.mobile-write-cta a');
  if (cta) {
    cta.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.getElementById('new-review');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => {
          const inp = target.querySelector('input[name="name"]');
          if (inp) inp.focus();
        }, 400);
      }
    });
  }

  const form = document.getElementById('new-review');
  const fixedBtn = document.querySelector('.mobile-write-cta');
  if (form && fixedBtn && window.innerWidth <= 768) {
    const observer = new IntersectionObserver(entries => {
      fixedBtn.style.display = entries[0].isIntersecting ? 'none' : 'flex';
    }, { threshold: 0.1 });
    observer.observe(form);
  }
});