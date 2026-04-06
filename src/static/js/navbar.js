(function () {
  var overlay, burger;

  function openMenu() {
    overlay.classList.add('open');
    burger.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    overlay.classList.remove('open');
    burger.classList.remove('open');
    document.body.style.overflow = '';
  }

  document.addEventListener('DOMContentLoaded', function () {
    overlay = document.getElementById('mobile-overlay');
    burger  = document.getElementById('burger');

    if (!overlay || !burger) return;

    burger.addEventListener('click', function () {
      overlay.classList.contains('open') ? closeMenu() : openMenu();
    });

    document.getElementById('mobile-menu-close').addEventListener('click', closeMenu);

    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeMenu();
    });

    var catalogToggle = document.querySelector('.mobile-catalog-toggle');
    if (catalogToggle) {
      catalogToggle.addEventListener('click', function (e) {
        e.preventDefault();
        this.closest('.mobile-dropdown').classList.toggle('open');
      });
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
  });
})();
