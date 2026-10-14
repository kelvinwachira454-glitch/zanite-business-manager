document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  document.querySelectorAll('.modal').forEach(function (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) modal.classList.remove('open');
    });
  });

  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  const overlay = document.getElementById('sidebarOverlay');

  if (sidebar && toggle && overlay) {
    function openSidebar() {
      sidebar.classList.add('mobile-open');
      overlay.classList.add('visible');
    }
    function closeSidebar() {
      sidebar.classList.remove('mobile-open');
      overlay.classList.remove('visible');
    }
    toggle.addEventListener('click', function () {
      sidebar.classList.contains('mobile-open') ? closeSidebar() : openSidebar();
    });
    overlay.addEventListener('click', closeSidebar);
    sidebar.querySelectorAll('.sidebar-nav a').forEach(function (link) {
      link.addEventListener('click', closeSidebar);
    });
  }

  const timeoutUrl = document.body.getAttribute('data-session-timeout-url');
  if (timeoutUrl) {
    const INACTIVITY_LIMIT_MS = 5 * 60 * 1000;
    let inactivityTimer;

    function logoutForInactivity() {
      window.location.href = timeoutUrl;
    }

    function resetInactivityTimer() {
      clearTimeout(inactivityTimer);
      inactivityTimer = setTimeout(logoutForInactivity, INACTIVITY_LIMIT_MS);
    }

    ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'click'].forEach(function (evt) {
      document.addEventListener(evt, resetInactivityTimer, { passive: true });
    });

    resetInactivityTimer();
  }
});
