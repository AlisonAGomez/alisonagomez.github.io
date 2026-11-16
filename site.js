'use strict';
(() => {
  const menu = document.getElementById('menuToggle');
  const nav = document.getElementById('mainNav');
  const closeMenu = () => {
    if (!menu || !nav) return;
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Abrir navegação');
    document.body.classList.remove('menu-open');
  };
  if (menu && nav) {
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      nav.classList.toggle('open', open);
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? 'Fechar navegação' : 'Abrir navegação');
      document.body.classList.toggle('menu-open', open);
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
    window.addEventListener('resize', () => { if (innerWidth > 950) closeMenu(); });
    document.addEventListener('click', e => {
      const dropdown = document.querySelector('.nav-dropdown[open]');
      if (dropdown && !dropdown.contains(e.target)) dropdown.open = false;
    });
  }
  const filters = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('[data-category]')];
  filters.forEach(button => button.addEventListener('click', () => {
    const value = button.dataset.filter;
    filters.forEach(filter => {
      filter.classList.toggle('active', filter === button);
      filter.setAttribute('aria-pressed', String(filter === button));
    });
    cards.forEach(card => { card.hidden = value !== 'todos' && card.dataset.category !== value; });
  }));
  const typed = document.getElementById('typedIntro');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (typed && !reduced) {
    const full = typed.textContent.trim();
    typed.textContent = '';
    let current = 0;
    const tick = () => {
      typed.textContent = full.slice(0, ++current);
      if (current < full.length) window.setTimeout(tick, 29);
    };
    window.setTimeout(tick, 450);
  }

  // Transições entre páginas internas; links externos e ações de browser continuam nativos.
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionOK = !motionQuery.matches;
  if (motionOK) {
    document.documentElement.classList.add('v4-motion');
    document.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const link = event.target.closest?.('a[href]');
      if (!link || link.hasAttribute('download') || link.target === '_blank') return;
      const href = link.getAttribute('href');
      if (!href || href.startsWith('#')) return;
      const destination = new URL(link.href, location.href);
      const here = new URL(location.href);
      const allowedProtocol = destination.protocol === 'file:' || destination.protocol === 'https:' || destination.protocol === 'http:';
      if (!allowedProtocol || destination.origin !== here.origin || destination.pathname === here.pathname) return;
      // Não interceptar links que saem da prévia ou navegação cruzando domínios.
      if ((here.protocol === 'file:' && destination.protocol !== 'file:') || (here.protocol !== 'file:' && !destination.pathname.startsWith(here.pathname.slice(0,here.pathname.lastIndexOf('/')+1)))) return;
      event.preventDefault();
      document.documentElement.classList.add('page-leaving');
      window.setTimeout(() => { location.href = destination.href; }, 165);
    });
    window.addEventListener('pageshow', () => document.documentElement.classList.remove('page-leaving'));
  }

  // Entrada de seções e cards conforme entram na tela, com alternativa acessível.
  const revealSelectors = ['.personal-intro-grid','.personal-two-col','.personal-work-grid','.section-top','.hobby-panel','.workflow','.personal-path','.inner-hero .shell','.project-card','.capability-card','.education-layout','.contact-terminal','.detail-section','.detail-art','.timeline-item','.nav-card','.lab-card'];
  if (motionOK && 'IntersectionObserver' in window) {
    const revealTargets = [...document.querySelectorAll(revealSelectors.join(','))];
    revealTargets.forEach((item, index) => {
      item.classList.add('reveal-target');
      item.style.setProperty('--reveal-delay', `${(index % 4) * 65}ms`);
    });
    document.documentElement.classList.add('reveal-enabled');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, {rootMargin:'0px 0px -8% 0px',threshold:.05});
    revealTargets.forEach(item => observer.observe(item));
  }

})();

// Imagens oficiais publicas usam fallback local se a rede estiver indisponivel.
document.querySelectorAll('img[data-fallback]').forEach(image => {
  image.addEventListener('error', () => {
    if (image.dataset.fallbackApplied) return;
    image.dataset.fallbackApplied = 'true';
    image.src = image.dataset.fallback;
  });
});
