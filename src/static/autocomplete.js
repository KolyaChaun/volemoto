(function () {
  var timer = null;

  function fmt(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0');
  }

  function initSearch(input) {
    var wrap = input.closest('.nav-search');
    if (!wrap) return;

    var dropdown = document.createElement('div');
    dropdown.className = 'search-dropdown';
    wrap.appendChild(dropdown);

    function hide() {
      dropdown.classList.remove('open');
      dropdown.innerHTML = '';
    }

    function show(bikes, q) {
      dropdown.innerHTML = '';
      if (!bikes.length) { hide(); return; }

      bikes.forEach(function (b) {
        var a = document.createElement('a');
        a.className = 'search-dropdown-item';
        a.href = '/bike/' + b.id;

        var thumb;
        if (b.photo) {
          thumb = document.createElement('div');
          thumb.className = 'search-dropdown-thumb-wrap';
          var img = document.createElement('img');
          img.src = b.photo;
          img.alt = b.name;
          thumb.appendChild(img);
        } else {
          thumb = document.createElement('div');
          thumb.className = 'search-dropdown-thumb-empty';
          thumb.textContent = '🏍';
        }

        var info = document.createElement('div');
        info.className = 'search-dropdown-info';

        var name = document.createElement('div');
        name.className = 'search-dropdown-name';
        name.textContent = b.name;

        var meta = document.createElement('div');
        meta.className = 'search-dropdown-meta';
        meta.textContent = b.year + (b.article ? ' · Арт. ' + b.article : '');

        info.appendChild(name);
        info.appendChild(meta);

        var price = document.createElement('div');
        price.className = 'search-dropdown-price';
        price.textContent = fmt(b.price) + ' ₴';

        a.appendChild(thumb);
        a.appendChild(info);
        a.appendChild(price);
        dropdown.appendChild(a);
      });

      var all = document.createElement('a');
      all.className = 'search-dropdown-all';
      all.href = '/search?q=' + encodeURIComponent(q);
      all.textContent = 'Показати всі результати →';
      dropdown.appendChild(all);

      dropdown.classList.add('open');
    }

    input.addEventListener('input', function () {
      clearTimeout(timer);
      var q = input.value.trim();
      if (q.length < 2) { hide(); return; }
      timer = setTimeout(function () {
        fetch('/api/search?q=' + encodeURIComponent(q))
          .then(function (r) { return r.json(); })
          .then(function (data) { show(data, q); })
          .catch(hide);
      }, 200);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') hide();
    });

    document.addEventListener('click', function (e) {
      if (!wrap.contains(e.target)) hide();
    });
  }

  document.querySelectorAll('.search-input').forEach(initSearch);
})();
