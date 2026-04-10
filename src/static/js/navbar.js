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

    document.querySelectorAll('.mobile-catalog-toggle').forEach(function (toggle) {
      toggle.addEventListener('click', function (e) {
        e.preventDefault();
        var dropdown = this.closest('.mobile-dropdown');
        var isOpen = dropdown.classList.contains('open');
        // Close all open dropdowns
        document.querySelectorAll('.mobile-dropdown.open').forEach(function (d) {
          d.classList.remove('open');
        });
        // Toggle current (open if it was closed)
        if (!isOpen) dropdown.classList.add('open');
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
  });
})();
