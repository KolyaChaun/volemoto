(function () {
  var timer = null;

  var CAT_LABELS = {
    helmets:    'Мотошолом',
    gloves:     'Рукавиці',
    gear:       'Екіпіровка',
    parts_new:  'Запчастини нові',
    parts_used: 'Запчастини б/у',
  };

  var EQUIPMENT_CATS = ['helmets', 'gloves', 'gear'];

  function fmt(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0');
  }

  function productUrl(item) {
    return (EQUIPMENT_CATS.indexOf(item.category) >= 0 ? '/equipment/' : '/parts/') + item.slug;
  }

  function makeThumb(photo, name, fallbackEmoji) {
    var thumb;
    if (photo) {
      thumb = document.createElement('div');
      thumb.className = 'search-dropdown-thumb-wrap';
      var img = document.createElement('img');
      img.src = photo;
      img.alt = name;
      thumb.appendChild(img);
    } else {
      thumb = document.createElement('div');
      thumb.className = 'search-dropdown-thumb-empty';
      thumb.textContent = fallbackEmoji;
    }
    return thumb;
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

    function show(results, q) {
      dropdown.innerHTML = '';
      if (!results.length) { hide(); return; }

      results.forEach(function (item) {
        var a = document.createElement('a');
        a.className = 'search-dropdown-item';

        if (item.type === 'bike') {
          a.href = '/catalog/' + (item.category || 'moto') + '/' + item.slug;

          a.appendChild(makeThumb(item.photo, item.name, '🏍'));

          var info = document.createElement('div');
          info.className = 'search-dropdown-info';

          var name = document.createElement('div');
          name.className = 'search-dropdown-name';
          name.textContent = item.name;

          var meta = document.createElement('div');
          meta.className = 'search-dropdown-meta';
          meta.textContent = item.year + (item.article ? ' · Арт. ' + item.article : '');

          info.appendChild(name);
          info.appendChild(meta);

          var price = document.createElement('div');
          price.className = 'search-dropdown-price';
          if (item.price_uah) {
            price.textContent = item.price_uah + ' ₴';
          } else if (item.price) {
            price.textContent = fmt(item.price) + ' $';
          }

          a.appendChild(info);
          a.appendChild(price);

        } else {
          a.href = productUrl(item);

          a.appendChild(makeThumb(item.photo, item.name, '🛡'));

          var info = document.createElement('div');
          info.className = 'search-dropdown-info';

          var name = document.createElement('div');
          name.className = 'search-dropdown-name';
          name.textContent = item.name;

          var meta = document.createElement('div');
          meta.className = 'search-dropdown-meta';
          meta.textContent = (CAT_LABELS[item.category] || item.category) +
            (item.article ? ' · Арт. ' + item.article : '');

          info.appendChild(name);
          info.appendChild(meta);

          var price = document.createElement('div');
          price.className = 'search-dropdown-price';
          price.textContent = fmt(item.price) + ' ₴';

          a.appendChild(info);
          a.appendChild(price);
        }

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