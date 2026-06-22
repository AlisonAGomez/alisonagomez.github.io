/* Remove /index.html da barra quando alguém entra pelo link completo */
if (location.pathname.endsWith("/index.html")) {
  history.replaceState(null, "", location.pathname.replace(/index\.html$/, "") + location.hash + location.search);
}

const typing = document.getElementById("typing");

const phrases = [
  "Suporte N1/N2/N3 • Infraestrutura • Segurança",
  "Monitoramento com Zabbix e Grafana",
  "Firewalls • VPNs • Redes • pfSense",
  "Automação com Python, APIs e PowerShell",
  "Proxmox • Linux • Windows Server",
  "Blue Team • Logs • Phishing • Hardening",
  "Sinalyx: análise de logs com IA"
];

if (typing) {
  let phraseIndex = 0;
  let charIndex = 0;
  let deleting = false;

  function typeLoop() {
    const current = phrases[phraseIndex];

    if (!deleting) {
      typing.textContent = current.slice(0, charIndex + 1);
      charIndex++;

      if (charIndex === current.length) {
        deleting = true;
        setTimeout(typeLoop, 1300);
        return;
      }
    } else {
      typing.textContent = current.slice(0, charIndex - 1);
      charIndex--;

      if (charIndex === 0) {
        deleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
      }
    }

    setTimeout(typeLoop, deleting ? 42 : 78);
  }

  typeLoop();
}

const year = document.getElementById("year");
if (year) {
  year.textContent = new Date().getFullYear();
}

const menuToggle = document.getElementById("menuToggle");
const nav = document.getElementById("nav");

if (menuToggle && nav) {
  menuToggle.addEventListener("click", () => {
    nav.classList.toggle("active");
  });

  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("active");
    });
  });
}

const revealElements = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window && revealElements.length) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  revealElements.forEach((element) => observer.observe(element));
} else {
  revealElements.forEach((element) => element.classList.add("visible"));
}

/* Canvas otimizado:
   - Home mantém animação mais bonita
   - Páginas internas usam menos partículas para não travar
   - animação em requestAnimationFrame para maior fluidez
*/
const canvas = document.getElementById("matrixCanvas");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (canvas && !prefersReducedMotion) {
  const ctx = canvas.getContext("2d");
  const isHome = Boolean(document.getElementById("typing"));

  let width;
  let height;
  let particles = [];
  let lastFrame = 0;

  function resizeCanvas() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;

    const isMobile = width < 720;
    const isMedium = width < 1200;

    let amount;

    if (isHome) {
      amount = isMobile ? 42 : isMedium ? 68 : Math.min(Math.floor(width / 18), 105);
    } else {
      amount = isMobile ? 22 : isMedium ? 34 : 48;
    }

    particles = Array.from({ length: amount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.24,
      vy: (Math.random() - 0.5) * 0.24,
      size: Math.random() * 1.45 + 0.55
    }));
  }

  function drawNetwork(timestamp) {
lastFrame = timestamp;
    ctx.clearRect(0, 0, width, height);

    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = isHome ? "rgba(0, 170, 255, 0.72)" : "rgba(0, 170, 255, 0.48)";
      ctx.fill();
    }

    const maxDistance = width < 720 ? 82 : isHome ? 118 : 90;

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i];
        const b = particles[j];

        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDistance) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(0, 170, 255, ${0.15 * (1 - dist / maxDistance)})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(drawNetwork);
  }

  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();
  requestAnimationFrame(drawNetwork);
} else if (canvas) {
  canvas.style.display = "none";
}

const preloader = document.getElementById("preloader");
const preloaderBar = document.getElementById("preloaderBar");
const preloaderPercent = document.getElementById("preloaderPercent");
const preloaderStatus = document.getElementById("preloaderStatus");

if (preloader && preloaderBar && preloaderPercent && preloaderStatus) {
  const loadMessages = [
    "Validando identidade...",
    "Carregando módulos de interface...",
    "Estabelecendo canal seguro...",
    "Sincronizando portfólio...",
    "Acesso autorizado."
  ];

  function runPreloader() {
    let value = 0;
    let msgIndex = 0;

    const tick = setInterval(() => {
      value += Math.floor(Math.random() * 13) + 8;
      if (value > 100) value = 100;

      preloaderBar.style.width = value + "%";
      preloaderPercent.textContent = value + "%";

      const bucket = Math.min(loadMessages.length - 1, Math.floor((value / 100) * loadMessages.length));

      if (bucket !== msgIndex || value === 100) {
        msgIndex = bucket;
        preloaderStatus.textContent = loadMessages[msgIndex];
      }

      if (value >= 100) {
        clearInterval(tick);

        setTimeout(() => {
          preloader.classList.add("hide");
          document.body.classList.remove("loading");
        }, 360);
      }
    }, 105);
  }

  window.addEventListener("load", () => {
    setTimeout(runPreloader, 150);
  });
}
