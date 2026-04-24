/* DIU BZSF — main.js */

// ── Hamburger Menu ─────────────────────────────────────────
const hamburger = document.querySelector('.hamburger');
const navLinks  = document.querySelector('.nav-links');
const overlay   = document.createElement('div');

overlay.id = 'nav-overlay';
Object.assign(overlay.style, {
  position: 'fixed', inset: '0', background: 'rgba(0,0,0,0.5)',
  zIndex: '140', display: 'none', backdropFilter: 'blur(2px)',
});
document.body.appendChild(overlay);

function openMenu() {
  hamburger.classList.add('open');
  navLinks.classList.add('open');
  overlay.style.display = 'block';
  document.body.style.overflow = 'hidden';
}
function closeMenu() {
  hamburger.classList.remove('open');
  navLinks.classList.remove('open');
  overlay.style.display = 'none';
  document.body.style.overflow = '';
}

if (hamburger) {
  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    navLinks.classList.contains('open') ? closeMenu() : openMenu();
  });
}
overlay.addEventListener('click', closeMenu);

// Close on nav link tap (mobile)
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth <= 820) closeMenu();
  });
});

// Close on resize past breakpoint
window.addEventListener('resize', () => {
  if (window.innerWidth > 820) closeMenu();
});

// ── Active Nav Link ─────────────────────────────────────────
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-links a').forEach(link => {
  if (link.getAttribute('href') === currentPath ||
      (link.getAttribute('href') !== '/' && currentPath.startsWith(link.getAttribute('href')))) {
    link.classList.add('active');
  }
});

// ── Auto-dismiss Flash Messages ─────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  // click to dismiss
  alert.style.cursor = 'pointer';
  alert.addEventListener('click', () => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(-8px)';
    alert.style.transition = 'opacity 0.3s, transform 0.3s';
    setTimeout(() => alert.remove(), 320);
  });

  // auto dismiss after 5 s
  setTimeout(() => {
    if (alert.parentNode) {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      alert.style.transition = 'opacity 0.4s, transform 0.4s';
      setTimeout(() => alert && alert.parentNode && alert.remove(), 420);
    }
  }, 5000);
});
