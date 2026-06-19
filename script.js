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

document.getElementById("year").textContent = new Date().getFullYear();

const menuToggle = document.getElementById("menuToggle");
const nav = document.getElementById("nav");

menuToggle.addEventListener("click", () => {
  nav.classList.toggle("active");
});

nav.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("active");
  });
});

const revealElements = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

revealElements.forEach((element) => observer.observe(element));

const canvas = document.getElementById("matrixCanvas");
const ctx = canvas.getContext("2d");

let width;
let height;
let particles;

function resizeCanvas() {
  width = canvas.width = window.innerWidth;
  height = canvas.height = window.innerHeight;

  const amount = Math.min(Math.floor(width / 11), 145);

  particles = Array.from({ length: amount }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.35,
    vy: (Math.random() - 0.5) * 0.35,
    size: Math.random() * 1.8 + 0.7
  }));
}

function drawNetwork() {
  ctx.clearRect(0, 0, width, height);

  for (const p of particles) {
    p.x += p.vx;
    p.y += p.vy;

    if (p.x < 0 || p.x > width) p.vx *= -1;
    if (p.y < 0 || p.y > height) p.vy *= -1;

    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(0, 170, 255, 0.75)";
    ctx.fill();
  }

  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i];
      const b = particles[j];
      const dx = a.x - b.x;
      const dy = a.y - b.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 120) {
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = `rgba(0, 170, 255, ${0.16 * (1 - dist / 120)})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }

  requestAnimationFrame(drawNetwork);
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();
drawNetwork();

const preloader = document.getElementById("preloader");
const preloaderBar = document.getElementById("preloaderBar");
const preloaderPercent = document.getElementById("preloaderPercent");
const preloaderStatus = document.getElementById("preloaderStatus");

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
    value += Math.floor(Math.random() * 9) + 4;
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
      }, 420);
    }
  }, 130);
}

window.addEventListener("load", () => {
  setTimeout(runPreloader, 180);
});
