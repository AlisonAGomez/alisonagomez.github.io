if (location.pathname.endsWith("/index.html")) {
  history.replaceState(null, "", location.pathname.replace(/index\.html$/, "") + location.search + location.hash);
}

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const year = document.getElementById("year");
const header = document.getElementById("siteHeader") || document.querySelector("header");
const menuToggle = document.getElementById("menuToggle");
const navigation = document.getElementById("mainNavigation") || document.getElementById("nav");

if (year) year.textContent = new Date().getFullYear();

function setMenuState(open, restoreFocus = false) {
  if (!menuToggle || !navigation) return;

  navigation.classList.toggle("is-open", open);
  navigation.classList.toggle("active", open);
  document.body.classList.toggle("nav-open", open);
  menuToggle.classList.toggle("is-open", open);
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");

  if (open) {
    const firstLink = navigation.querySelector("a");
    window.setTimeout(() => firstLink?.focus(), 40);
  } else if (restoreFocus) {
    menuToggle.focus();
  }
}

if (menuToggle && navigation) {
  menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    setMenuState(!isOpen, isOpen);
  });

  navigation.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setMenuState(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") {
      setMenuState(false, true);
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 860) setMenuState(false);
  });
}

function updateHeaderState() {
  header?.classList.toggle("is-scrolled", window.scrollY > 18);
}

updateHeaderState();
window.addEventListener("scroll", updateHeaderState, { passive: true });

const typing = document.getElementById("typing");
const phrases = [
  "segurança defensiva",
  "automação operacional",
  "infraestrutura e redes",
  "suporte técnico N2/N3",
  "análise de logs e evidências"
];

if (typing) {
  let phraseIndex = 0;
  let characterIndex = 0;
  let deleting = false;
  let timer;

  function schedule(delay) {
    window.clearTimeout(timer);
    timer = window.setTimeout(typeNextFrame, delay);
  }

  function typeNextFrame() {
    if (reducedMotion.matches) {
      typing.textContent = phrases[0];
      return;
    }

    const phrase = phrases[phraseIndex];
    typing.textContent = phrase.slice(0, characterIndex);

    if (!deleting && characterIndex < phrase.length) {
      characterIndex += 1;
      schedule(48);
      return;
    }

    if (!deleting) {
      deleting = true;
      schedule(1450);
      return;
    }

    if (characterIndex > 0) {
      characterIndex -= 1;
      schedule(26);
      return;
    }

    deleting = false;
    phraseIndex = (phraseIndex + 1) % phrases.length;
    schedule(260);
  }

  function resetTyping() {
    window.clearTimeout(timer);
    phraseIndex = 0;
    characterIndex = reducedMotion.matches ? phrases[0].length : 0;
    deleting = false;
    typing.textContent = reducedMotion.matches ? phrases[0] : "";
    if (!reducedMotion.matches) schedule(280);
  }

  reducedMotion.addEventListener?.("change", resetTyping);
  resetTyping();
}

const revealElements = document.querySelectorAll(".reveal");

if (reducedMotion.matches || !("IntersectionObserver" in window)) {
  revealElements.forEach((element) => element.classList.add("is-visible", "visible"));
} else {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible", "visible");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -40px" });

  revealElements.forEach((element) => revealObserver.observe(element));
}

function markCurrentNavigation() {
  if (!navigation) return;

  const links = [...navigation.querySelectorAll("a")];
  links.forEach((link) => link.removeAttribute("aria-current"));

  const currentPath = location.pathname.replace(/\/index\.html$/, "/");
  const isHome = currentPath === "/" || currentPath === "";

  if (!isHome) {
    const matchingLink = links.find((link) => {
      const url = new URL(link.href, location.href);
      return url.pathname !== "/" && currentPath.startsWith(url.pathname);
    });
    matchingLink?.setAttribute("aria-current", "page");
    return;
  }

  const sectionLinks = links.filter((link) => link.hash && link.pathname === location.pathname);
  const sections = sectionLinks
    .map((link) => document.querySelector(link.hash))
    .filter(Boolean);

  if (!sections.length || !("IntersectionObserver" in window)) {
    sectionLinks[0]?.setAttribute("aria-current", "location");
    return;
  }

  const activeObserver = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;

    sectionLinks.forEach((link) => {
      if (link.hash === `#${visible.target.id}`) {
        link.setAttribute("aria-current", "location");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }, { rootMargin: "-30% 0px -60%", threshold: [0, 0.1, 0.5] });

  sections.forEach((section) => activeObserver.observe(section));
}

markCurrentNavigation();

const internalPath = location.pathname.replace(/\/index\.html$/, "/");
const isHomePath = internalPath === "/" || internalPath === "";

if (!isHomePath && !document.querySelector(".page-back-shell")) {
  const shell = document.createElement("div");
  shell.className = "page-back-shell";
  const button = document.createElement("button");
  button.type = "button";
  button.className = "page-back-button";
  button.setAttribute("aria-label", "Voltar para a página anterior");
  button.textContent = "← Voltar";

  button.addEventListener("click", () => {
    let sameOriginReferrer = false;
    try {
      sameOriginReferrer = Boolean(document.referrer) && new URL(document.referrer).origin === location.origin;
    } catch {
      sameOriginReferrer = false;
    }

    if (sameOriginReferrer && history.length > 1) {
      history.back();
    } else {
      location.href = `${location.origin}/#home`;
    }
  });

  shell.appendChild(button);
  document.body.appendChild(shell);
}
