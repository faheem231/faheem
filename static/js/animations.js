/**
 * animations.js
 * ─────────────
 * GSAP-powered animation helpers.
 *
 * Functions exposed (global):
 *   - initPageAnimations()        → Hero + scroll animations
 *   - animateScoreRing(val)       → Animate ATS score ring
 *   - animateSkillBars()          → Animate skill progress bars
 *   - animateMatchBar(val)        → Animate JD match bar
 *   - animateFileDropped(name)    → Upload drop animation
 *   - animateProgressBar(sel, w)  → Generic progress bar
 *   - animateResultCards()        → Result cards stagger in
 *   - animateCounter(sel, n, sfx) → Animate any number counter
 *   - showToast(msg, type)        → Toast notification
 */

// ── Page Entry Animations ─────────────────────────────────────────────────────
function initPageAnimations() {
  if (typeof gsap === 'undefined') return;

  // Hero stagger
  ['.hero-eyebrow', '.hero h1', '.hero p', '.hero-cta'].forEach((sel, i) => {
    const els = document.querySelectorAll(sel);
    if (els.length) {
      gsap.fromTo(els,
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 0.8, delay: i * 0.15, ease: 'power3.out' }
      );
    }
  });

  // Feature cards
  gsap.fromTo('.feature-card',
    { opacity: 0, y: 40, scale: 0.95 },
    { opacity: 1, y: 0, scale: 1, duration: 0.7, stagger: 0.1, delay: 0.4, ease: 'back.out(1.4)' }
  );

  // Navbar slide down
  gsap.fromTo('.navbar',
    { opacity: 0, y: -20 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out' }
  );

  // Scroll fade-ups
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        gsap.to(entry.target, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' });
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.fade-up').forEach(el => {
    gsap.set(el, { opacity: 0, y: 30 });
    observer.observe(el);
  });

  // Data counters
  document.querySelectorAll('[data-count]').forEach((el) => {
    const target = parseFloat(el.dataset.count);
    gsap.fromTo({ val: 0 }, { val: target }, {
      duration: 2,
      delay: 0.5,
      ease: 'power2.out',
      onUpdate() {
        el.textContent = Math.round(this.targets()[0].val) + (el.dataset.suffix || '');
      }
    });
  });

  // Animate skill bars if present on page load
  animateSkillBars();
}


// ── ATS Score Ring ────────────────────────────────────────────────────────────
function animateScoreRing(score, maxScore = 100) {
  const ring     = document.querySelector('.score-ring-fill');
  const numberEl = document.querySelector('.score-number');
  const labelEl  = document.querySelector('.score-label');
  if (!ring) return;

  const radius       = parseFloat(ring.getAttribute('r'));
  const circumference = 2 * Math.PI * radius;

  ring.style.strokeDasharray  = circumference;
  ring.style.strokeDashoffset = circumference;
  ring.style.transition       = 'stroke-dashoffset 1.5s cubic-bezier(0.4,0,0.2,1), stroke 0.6s ease';

  let color, label;
  if (score >= 75)      { color = '#34D399'; label = 'Great';       }
  else if (score >= 55) { color = '#94A3B8'; label = 'Good';        }
  else if (score >= 35) { color = '#64748B'; label = 'Fair';        }
  else                  { color = '#F87171'; label = 'Needs Work';  }

  ring.style.stroke = color;

  setTimeout(() => {
    ring.style.strokeDashoffset = circumference * (1 - score / maxScore);
  }, 300);

  if (numberEl && typeof gsap !== 'undefined') {
    gsap.fromTo({ val: 0 }, { val: score }, {
      duration: 1.6,
      ease: 'power2.out',
      delay: 0.4,
      onUpdate() {
        numberEl.textContent = Math.round(this.targets()[0].val);
      }
    });
    numberEl.style.color = color;
  } else if (numberEl) {
    numberEl.textContent = score;
    numberEl.style.color = color;
  }

  if (labelEl) {
    labelEl.textContent = label;
    labelEl.style.color = color;
    if (typeof gsap !== 'undefined') {
      gsap.fromTo(labelEl, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.5, delay: 1.2, ease: 'back.out(1.4)' });
    }
  }
}


// ── Skill Bars ────────────────────────────────────────────────────────────────
function animateSkillBars() {
  const bars = document.querySelectorAll('.skill-bar-fill');
  if (!bars.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar   = entry.target;
        const width = bar.dataset.width || '0';
        if (typeof gsap !== 'undefined') {
          gsap.fromTo(bar,
            { width: '0%' },
            { width: `${width}%`, duration: 1.1, ease: 'power3.out', delay: 0.1 }
          );
        } else {
          bar.style.transition = 'width 1s ease';
          bar.style.width      = `${width}%`;
        }
        observer.unobserve(bar);
      }
    });
  }, { threshold: 0.2 });

  bars.forEach(bar => {
    bar.style.width = '0%';
    observer.observe(bar);
  });
}


// ── JD Match Bar ──────────────────────────────────────────────────────────────
function animateMatchBar(score) {
  const bar   = document.querySelector('.match-bar-fill');
  const label = document.querySelector('.match-score-label');
  if (!bar) return;

  let color;
  if (score >= 75)      color = '#34D399';
  else if (score >= 50) color = '#94A3B8';
  else                  color = '#64748B';

  bar.style.background  = color;
  bar.style.transition  = 'width 1.5s cubic-bezier(0.4,0,0.2,1)';
  bar.style.width       = '0%';

  setTimeout(() => { bar.style.width = `${score}%`; }, 300);

  if (label && typeof gsap !== 'undefined') {
    gsap.fromTo({ val: 0 }, { val: score }, {
      duration: 1.6,
      ease: 'power2.out',
      delay: 0.3,
      onUpdate() {
        label.textContent = Math.round(this.targets()[0].val) + '%';
      }
    });
    label.style.color = color;
  }
}


// ── Upload File Dropped ────────────────────────────────────────────────────────
function animateFileDropped(filename) {
  if (typeof gsap === 'undefined') return;

  const icon  = document.querySelector('.upload-icon');
  const label = document.querySelector('.upload-label');
  const zone  = document.querySelector('.upload-zone');

  if (zone) {
    gsap.to(zone, {
      borderColor: 'rgba(255, 255, 255, 0.25)',
      duration: 0.4,
      ease: 'power2.out'
    });
  }

  if (icon) {
    gsap.to(icon, {
      scale: 1.3,
      duration: 0.25,
      yoyo: true,
      repeat: 1,
      ease: 'back.out(2)'
    });
  }

  if (label) {
    gsap.to(label, {
      opacity: 0, y: -10, duration: 0.2,
      onComplete: () => {
        label.textContent = `${filename}`;
        label.style.color = '#E2E8F0';
        gsap.to(label, { opacity: 1, y: 0, duration: 0.3 });
      }
    });
  }
}


// ── Generic Progress Bar ──────────────────────────────────────────────────────
function animateProgressBar(selector, width) {
  const bar = document.querySelector(selector);
  if (!bar) return;

  if (typeof gsap !== 'undefined') {
    gsap.fromTo(bar,
      { width: '0%' },
      { width: `${width}%`, duration: 1.2, ease: 'power3.out', delay: 0.2 }
    );
  } else {
    bar.style.transition = 'width 1.2s ease';
    bar.style.width      = `${width}%`;
  }
}


// ── Result Cards Stagger ──────────────────────────────────────────────────────
function animateResultCards() {
  if (typeof gsap === 'undefined') return;
  gsap.fromTo('.result-card',
    { opacity: 0, y: 30, scale: 0.96 },
    { opacity: 1, y: 0, scale: 1, duration: 0.65, stagger: 0.12, ease: 'back.out(1.2)', delay: 0.3 }
  );
}


// ── Number Counter ────────────────────────────────────────────────────────────
function animateCounter(selector, target, suffix = '', duration = 1.5) {
  const el = document.querySelector(selector);
  if (!el || typeof gsap === 'undefined') return;
  gsap.fromTo({ val: 0 }, { val: target }, {
    duration,
    ease: 'power2.out',
    onUpdate() {
      el.textContent = Math.round(this.targets()[0].val) + suffix;
    }
  });
}


// ── Page Transition Out ───────────────────────────────────────────────────────
function pageTransitionOut(href) {
  if (typeof gsap === 'undefined') {
    window.location.href = href;
    return;
  }
  gsap.to('body', {
    opacity: 0,
    duration: 0.3,
    ease: 'power2.in',
    onComplete: () => { window.location.href = href; }
  });
}


// ── Toast Notifications ────────────────────────────────────────────────────────
const TOAST_ICONS = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };

function showToast(message, type = 'info', duration = 4000) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${TOAST_ICONS[type] || 'ℹ️'}</span><span>${message}</span>`;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => { toast.classList.add('show'); });
  });

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 500);
  }, duration);
}


// ── Typing Effect ─────────────────────────────────────────────────────────────
function typeText(selector, text, speed = 40) {
  const el = document.querySelector(selector);
  if (!el) return;
  el.textContent = '';
  let i = 0;
  const interval = setInterval(() => {
    el.textContent += text[i];
    i++;
    if (i >= text.length) clearInterval(interval);
  }, speed);
}


// ── Ripple Effect on Buttons ──────────────────────────────────────────────────
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn');
  if (!btn) return;

  const ripple = document.createElement('span');
  ripple.style.cssText = `
    position:absolute;border-radius:50%;
    width:6px;height:6px;
    background:rgba(255,255,255,0.4);
    transform:scale(0);
    animation:ripple-anim 0.6s linear;
    pointer-events:none;
    left:${e.offsetX - 3}px;
    top:${e.offsetY - 3}px;
  `;

  if (!document.querySelector('#ripple-style')) {
    const style = document.createElement('style');
    style.id = 'ripple-style';
    style.textContent = `
      @keyframes ripple-anim {
        to { transform: scale(40); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  const prev = btn.style.position;
  btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(ripple);
  setTimeout(() => {
    ripple.remove();
    if (!prev) btn.style.position = '';
  }, 700);
});


// ── Run on DOMContentLoaded ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Fade in body
  if (typeof gsap !== 'undefined') {
    gsap.fromTo('body', { opacity: 0 }, { opacity: 1, duration: 0.5, ease: 'power2.out' });
  }
  initPageAnimations();

  // Global navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar');
    if (nav) {
      if (window.scrollY > 50) nav.classList.add('scrolled');
      else nav.classList.remove('scrolled');
    }
  });
});