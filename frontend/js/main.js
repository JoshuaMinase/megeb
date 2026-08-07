// ===== STICKY HEADER =====
(function () {
  const header = document.querySelector('header');
  if (!header) return;

  const logoImg = header.querySelector('img');
  const logoWhite = logoImg ? logoImg.getAttribute('data-logo-white') : null;
  const logoDark  = logoImg ? logoImg.getAttribute('data-logo-dark')  : null;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 200) {
      if (!header.classList.contains('sticky')) {
        header.classList.add('sticky');
        if (logoImg && logoDark) logoImg.src = logoDark;
      }
    } else {
      header.classList.remove('sticky');
      if (logoImg && logoWhite) logoImg.src = logoWhite;
    }
  }, { passive: true });
})();

// ===== HERO ZOOM + PARALLAX (index only) =====
(function () {
  const zoom     = document.querySelector('.zoom-wrapper');
  const heroText = document.querySelector('.hero-text');
  const zjBg     = document.querySelector('.zj-hero-bg');

  if (!zoom && !heroText && !zjBg) return;

  window.addEventListener('scroll', () => {
    const s = window.scrollY;

    if (zoom) {
      let scale = 1 + s / 1200;
      if (scale > 1.4) scale = 1.4;
      zoom.style.transform = `scale(${scale})`;
    }

    if (heroText) {
      const opacity = Math.max(0, 1 - (s - 100) / 400);
      heroText.style.opacity  = opacity;
      heroText.style.transform = `translate(-50%, calc(-50% + ${s / 7}px))`;
    }

    if (zjBg) {
      const scale = 1.05 + s / 3000;
      zjBg.style.transform = `scale(${Math.min(scale, 1.4)})`;
    }
  }, { passive: true });
})();

// ===== INNER PAGE HERO PARALLAX (foods / recipe pages) =====
(function () {
  const heroImg  = document.querySelector('.hero.static .hero-img');
  const heroTitle = document.querySelector('.hero-title');
  if (!heroImg && !heroTitle) return;

  window.addEventListener('scroll', () => {
    const s = window.scrollY;
    if (heroImg) heroImg.style.transform = `scale(${1 + s / 2000})`;
    if (heroTitle) {
      heroTitle.style.transform = `translate(-50%, calc(-50% + ${s / 3}px))`;
      heroTitle.style.opacity   = Math.max(0, 1 - s / 600);
    }
  }, { passive: true });
})();

// ===== INTERSECTION OBSERVER (scroll-reveal) =====
(function () {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('active'); });
  }, { threshold: 0.3 });

  document.querySelectorAll('.rotate-img, .bimg, .image21 img')
    .forEach(el => observer.observe(el));
})();

// ===== HORIZONTAL SCROLL (foods page) =====
(function () {
  const section  = document.querySelector('.horizontal-scroll-container');
  const foodGrid = document.querySelector('.food-grid');
  if (!section || !foodGrid) return;

  window.addEventListener('scroll', () => {
    const s          = window.scrollY;
    const offsetTop  = section.offsetTop;
    const maxScroll  = section.offsetHeight - window.innerHeight;
    const moveAmount = foodGrid.scrollWidth - window.innerWidth;

    if (s < offsetTop) {
      foodGrid.style.transform = 'translateX(0px)';
    } else if (s > offsetTop + maxScroll) {
      foodGrid.style.transform = `translateX(-${moveAmount}px)`;
    } else {
      const pct = (s - offsetTop) / maxScroll;
      foodGrid.style.transform = `translateX(-${pct * moveAmount}px)`;
    }
  }, { passive: true });
})();


// ===== SCROLL REVEAL (fade + slide up) =====
(function () {
  const els = document.querySelectorAll(
    '.recipe-card, .section-title, .trending-card, .feature-item, .auth-card, .page-title, h2, h3, .sub, p, .btn, .food-card'
  );

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        const delay = (Array.from(els).indexOf(e.target) % 6) * 80;
        e.target.style.transitionDelay = delay + 'ms';
        e.target.classList.add('sr-visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });

  els.forEach(el => { el.classList.add('sr-hidden'); io.observe(el); });
})();

// ===== ZJ REVEAL (scroll-triggered for new zetta-joule sections) =====
(function () {
  const revealEls = document.querySelectorAll('.zj-reveal, .zj-reveal-delay');
  if (!revealEls.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('zj-visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => io.observe(el));
})();

// ===== SMOOTH CURSOR GLOW =====
(function () {
  const glow = document.createElement('div');
  glow.id = 'cursor-glow';
  document.body.appendChild(glow);

  let mx = -200, my = -200, cx = -200, cy = -200;

  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

  function loop() {
    cx += (mx - cx) * 0.1;
    cy += (my - cy) * 0.1;
    glow.style.transform = `translate(${cx - 200}px, ${cy - 200}px)`;
    requestAnimationFrame(loop);
  }
  loop();
})();

// ===== CARD TILT ON HOVER =====
(function () {
  document.addEventListener('mousemove', e => {
    document.querySelectorAll('.recipe-card, .trending-card, .food-card').forEach(card => {
      const r   = card.getBoundingClientRect();
      const cx  = r.left + r.width / 2;
      const cy  = r.top  + r.height / 2;
      const dx  = (e.clientX - cx) / (r.width / 2);
      const dy  = (e.clientY - cy) / (r.height / 2);
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 1.4) {
        card.style.transform = `perspective(600px) rotateY(${dx * 4}deg) rotateX(${-dy * 4}deg) translateY(-6px)`;
      } else {
        card.style.transform = '';
      }
    });
  });

  document.addEventListener('mouseleave', () => {
    document.querySelectorAll('.recipe-card, .trending-card, .food-card').forEach(c => c.style.transform = '');
  });
})();


// ===== SCROLL-TO-TOP BUTTON =====
(function () {
  const btn = document.createElement('button');
  btn.id = 'scroll-top-btn';
  btn.title = 'Back to top';
  btn.setAttribute('aria-label', 'Scroll to top');
  btn.innerHTML = '↑';
  document.body.appendChild(btn);

  // Show after scrolling 400px
  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();
