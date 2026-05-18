document.addEventListener('DOMContentLoaded', () => {
  // Toggle password (icône œil)
  const toggle = document.querySelector('.js-toggle-password');
  const passwordInput = document.getElementById('password');

  if (toggle && passwordInput) {
    toggle.addEventListener('click', () => {
      const svg = toggle.querySelector('svg');
      const isPassword = passwordInput.type === 'password';

      if (isPassword) {
        passwordInput.type = 'text';
        if (svg) {
          svg.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
        }
      } else {
        passwordInput.type = 'password';
        if (svg) {
          svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" x2="23" y1="1" y2="23"/>';
        }
      }
    });
  }

  // Auto-hide alerts
  document.querySelectorAll('.alert-auto-hide').forEach((alert) => {
    window.setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      window.setTimeout(() => {
        if (alert) alert.style.display = 'none';
      }, 500);
    }, 5000);
  });
});

