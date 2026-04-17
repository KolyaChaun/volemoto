// Number inputs: block value-change on scroll, pass scroll to page instead
document.querySelectorAll('input[type="number"]').forEach(function (el) {
  el.addEventListener('wheel', function (e) {
    e.preventDefault();
    window.scrollBy({ top: e.deltaY, behavior: 'auto' });
  }, { passive: false });
});

(function () {
  var burger = document.getElementById('admin-burger');
  var sidebar = document.querySelector('.sidebar');
  var overlay = document.getElementById('sidebar-overlay');

  if (!burger || !sidebar || !overlay) return;

  function openMenu() {
    sidebar.classList.add('open');
    overlay.classList.add('open');
    burger.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
    burger.classList.remove('open');
    document.body.style.overflow = '';
  }

  burger.addEventListener('click', function () {
    sidebar.classList.contains('open') ? closeMenu() : openMenu();
  });

  overlay.addEventListener('click', closeMenu);
})();
