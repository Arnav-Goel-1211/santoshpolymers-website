document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.getElementById('stickyCtaToggle');
  var body = document.getElementById('stickyCtaBody');
  if (toggle && body) {
    toggle.addEventListener('click', function () {
      body.classList.toggle('hidden');
    });
  }
});
