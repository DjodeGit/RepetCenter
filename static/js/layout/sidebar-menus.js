document.addEventListener('DOMContentLoaded', () => {
  function toggleMenu(menuId, chevronId) {
    const submenu = document.getElementById(menuId);
    const chevron = document.getElementById(chevronId);
    if (!submenu || !chevron) return;

    if (submenu.classList.contains('hidden')) {
      submenu.classList.remove('hidden');
      chevron.style.transform = 'rotate(180deg)';
    } else {
      submenu.classList.add('hidden');
      chevron.style.transform = 'rotate(0deg)';
    }
  }

  // Boutons de toggle (sidebar)
  document.querySelectorAll('[data-toggle-menu]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const menuId = btn.getAttribute('data-toggle-menu');
      const chevronId = btn.getAttribute('data-chevron');
      toggleMenu(menuId, chevronId);
    });
  });

  // Ouverture automatique: on se base sur data-app (généré côté template)
  const autoApp = document.documentElement.getAttribute('data-auto-app');
  if (autoApp === 'apprenants') {
    toggleMenu('apprenants-submenu', 'apprenants-chevron');
  }
  if (autoApp === 'enseignants') {
    toggleMenu('enseignants-submenu', 'enseignants-chevron');
  }
});

