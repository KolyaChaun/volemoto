document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.style.display = 'none';

    const wrapper = document.createElement('div');
    wrapper.className = 'custom-file-wrap';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'custom-file-btn';
    btn.textContent = input.multiple ? 'Обрати файли' : 'Обрати файл';

    const label = document.createElement('span');
    label.className = 'custom-file-label';
    label.textContent = 'Файл не обрано';

    wrapper.appendChild(btn);
    wrapper.appendChild(label);
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    btn.addEventListener('click', () => input.click());

    input.addEventListener('change', function () {
      if (this.files.length === 0) {
        label.textContent = 'Файл не обрано';
      } else if (this.files.length === 1) {
        label.textContent = this.files[0].name;
      } else {
        label.textContent = 'Обрано файлів: ' + this.files.length;
      }
    });
  });
});