if (location.pathname.endsWith("/index.html")) {
  history.replaceState(null, "", location.pathname.replace(/index\.html$/, "") + location.search + location.hash);
}

const header = document.getElementById("siteHeader");
const menuToggle = document.getElementById("menuToggle");
const navigation = document.getElementById("mainNavigation");
const year = document.getElementById("year");

if (year) year.textContent = String(new Date().getFullYear());

function setMenuState(open, restoreFocus = false) {
  if (!menuToggle || !navigation) return;
  navigation.classList.toggle("is-open", open);
  menuToggle.classList.toggle("is-open", open);
  menuToggle.setAttribute("aria-expanded", String(open));
  menuToggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
  document.body.classList.toggle("nav-open", open);

  if (open) {
    window.setTimeout(() => navigation.querySelector("a")?.focus(), 30);
  } else if (restoreFocus) {
    menuToggle.focus();
  }
}

if (menuToggle && navigation) {
  menuToggle.addEventListener("click", () => {
    setMenuState(menuToggle.getAttribute("aria-expanded") !== "true", true);
  });
  navigation.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMenuState(false)));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") setMenuState(false, true);
  });
  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) setMenuState(false);
  });
}

function updateHeader() {
  header?.classList.toggle("is-scrolled", window.scrollY > 12);
}
updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });
window.addEventListener("load", () => {
  if (!location.hash) return;
  const anchor = document.getElementById(location.hash.slice(1));
  if (!anchor) return;
  window.requestAnimationFrame(() => window.requestAnimationFrame(() => anchor.scrollIntoView({ block: "start" })));
});

function markCurrentNavigation() {
  if (!navigation) return;
  const links = [...navigation.querySelectorAll("a")];
  const currentPath = location.pathname.replace(/\/index\.html$/, "/");
  const onHome = currentPath === "/" || currentPath === "";

  if (!onHome) {
    links[0]?.setAttribute("aria-current", "page");
    return;
  }

  const sectionLinks = links.filter((link) => link.hash && link.pathname === location.pathname);
  const sections = sectionLinks.map((link) => document.querySelector(link.hash)).filter(Boolean);
  if (!("IntersectionObserver" in window) || !sections.length) return;

  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    sectionLinks.forEach((link) => {
      if (link.hash === `#${visible.target.id}`) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }, { rootMargin: "-30% 0px -60%", threshold: [0, 0.15, 0.5] });
  sections.forEach((section) => observer.observe(section));
}
markCurrentNavigation();

const toc = document.querySelector(".case-toc");
if (toc && "IntersectionObserver" in window) {
  const links = [...toc.querySelectorAll("a[href^='#']")];
  const targets = links.map((link) => document.getElementById(link.hash.slice(1))).filter(Boolean);
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach((link) => {
      if (link.hash === `#${visible.target.id}`) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }, { rootMargin: "-24% 0px -66%", threshold: [0, 0.2, 0.5] });
  targets.forEach((target) => observer.observe(target));
}

const lightbox = document.getElementById("lightbox");
const lightboxImage = document.getElementById("lightboxImage");
const lightboxTitle = document.getElementById("lightboxTitle");
const lightboxCaption = document.getElementById("lightboxCaption");
const lightboxClose = document.getElementById("lightboxClose");
let lightboxTrigger = null;

document.querySelectorAll("[data-lightbox]").forEach((trigger) => {
  trigger.addEventListener("click", (event) => {
    if (!lightbox || !lightboxImage) return;
    event.preventDefault();
    lightboxTrigger = trigger;
    lightboxImage.src = trigger.href;
    lightboxImage.alt = trigger.dataset.alt || "Evidência técnica ampliada";
    if (lightboxTitle) lightboxTitle.textContent = trigger.dataset.title || "Evidência técnica";
    if (lightboxCaption) lightboxCaption.textContent = trigger.dataset.caption || "";
    lightbox.showModal();
    lightboxClose?.focus();
  });
});

function closeLightbox() {
  if (!lightbox?.open) return;
  lightbox.close();
  lightboxTrigger?.focus();
}

lightboxClose?.addEventListener("click", closeLightbox);
lightbox?.addEventListener("click", (event) => {
  if (event.target === lightbox) closeLightbox();
});
lightbox?.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeLightbox();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && lightbox?.open) {
    event.preventDefault();
    closeLightbox();
  }
});

document.querySelectorAll("[data-back]").forEach((button) => {
  button.addEventListener("click", () => {
    let sameOrigin = false;
    try { sameOrigin = Boolean(document.referrer) && new URL(document.referrer).origin === location.origin; } catch { sameOrigin = false; }
    if (sameOrigin && history.length > 1) history.back();
    else location.href = `${location.origin}/#cases`;
  });
});
