/* ═══════════════════════════════════════════════════════════════
   BZSF — main.js  |  Hamburger, Alerts, Active Nav
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── DOM refs ─────────────────────────────────────────────────
  const hamburger = document.querySelector('.hamburger');
  const navLinks  = document.querySelector('.nav-links');
  const navbar    = document.querySelector('.navbar');

  // ── Create overlay ───────────────────────────────────────────
  const overlay = document.createElement('div');
  overlay.className = 'nav-overlay';
  document.body.appendChild(overlay);

  // ── State ────────────────────────────────────────────────────
  let menuOpen = false;

  function openMenu() {
    menuOpen = true;
    hamburger.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    navLinks.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    menuOpen = false;
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    navLinks.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function toggleMenu() {
    menuOpen ? closeMenu() : openMenu();
  }

  // ── Hamburger click ──────────────────────────────────────────
  if (hamburger) {
    hamburger.setAttribute('aria-label', 'Toggle navigation');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleMenu();
    });
  }

  // ── Overlay click closes menu ─────────────────────────────────
  overlay.addEventListener('click', closeMenu);

  // ── Close on nav link tap (mobile) ──────────────────────────
  if (navLinks) {
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth <= 860) closeMenu();
      });
    });
  }

  // ── Close on resize past breakpoint ──────────────────────────
  window.addEventListener('resize', function () {
    if (window.innerWidth > 860 && menuOpen) closeMenu();
  });

  // ── Escape key ───────────────────────────────────────────────
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menuOpen) closeMenu();
  });

  // ── Active nav link ──────────────────────────────────────────
  if (navLinks) {
    const currentPath = window.location.pathname;
    navLinks.querySelectorAll('a').forEach(function (link) {
      const href = link.getAttribute('href');
      if (!href) return;
      if (
        href === currentPath ||
        (href !== '/' && currentPath.startsWith(href))
      ) {
        link.classList.add('active');
      }
    });
  }

  // ── Auto-dismiss flash messages ───────────────────────────────
  document.querySelectorAll('.alert').forEach(function (alert) {
    function dismiss() {
      alert.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(function () {
        if (alert.parentNode) alert.parentNode.removeChild(alert);
      }, 370);
    }

    // Click to dismiss
    alert.addEventListener('click', dismiss);

    // Auto-dismiss after 5 s
    setTimeout(dismiss, 5000);
  });

  // ── Lightbox (shared across pages) ───────────────────────────
  window.openLightbox = function (src, caption) {
    const lb  = document.getElementById('lightbox');
    const img = document.getElementById('lightbox-img');
    const cap = document.getElementById('lightbox-caption');
    if (!lb || !img) return;
    img.src = src;
    if (cap) cap.textContent = caption || '';
    lb.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  };

  window.closeLightbox = function () {
    const lb = document.getElementById('lightbox');
    if (!lb) return;
    lb.style.display = 'none';
    document.body.style.overflow = '';
  };

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') window.closeLightbox();
  });

  // ── Navbar scroll shadow ─────────────────────────────────────
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 8) {
        navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
      } else {
        navbar.style.boxShadow = '';
      }
    }, { passive: true });
  }

  // ── Image preview for file inputs ────────────────────────────
  document.querySelectorAll('input[type="file"][data-preview]').forEach(function (input) {
    const gridId = input.getAttribute('data-preview');
    const grid   = document.getElementById(gridId);
    if (!grid) return;
    input.addEventListener('change', function () {
      grid.innerHTML = '';
      Array.from(this.files).slice(0, 5).forEach(function (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const wrap = document.createElement('div');
          wrap.style.cssText = 'border-radius:8px;overflow:hidden;aspect-ratio:1;border:1px solid var(--card-border)';
          const img = document.createElement('img');
          img.src = e.target.result;
          img.style.cssText = 'width:100%;height:100%;object-fit:cover';
          wrap.appendChild(img);
          grid.appendChild(wrap);
        };
        reader.readAsDataURL(file);
      });
    });
  });

})();
