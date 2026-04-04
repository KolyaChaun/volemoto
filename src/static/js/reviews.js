function toggleReply(id) {
  const form = document.getElementById('reply-form-' + id);
  form.classList.toggle('open');
  if (form.classList.contains('open')) {
    form.querySelector('textarea').focus();
  }
}
