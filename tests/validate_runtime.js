const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const assert = (condition, message) => { if (!condition) throw new Error(message); };

const script = read("script.js");
assert(!script.includes("typeNextFrame"), "Efeito de digitação não deveria existir.");
assert(script.includes("Escape"), "Menu precisa fechar com Escape.");
assert(script.includes("showModal"), "Lightbox acessível não foi inicializado.");
assert(script.includes("aria-expanded"), "Estado acessível do menu não foi implementado.");

const cases = [
  "cases/incidente-extensao-chrome/index.html",
  "cases/auditor-backups-dropbox/index.html",
  "cases/sinalyx/index.html",
  "cases/veonyx-arquitetura/index.html",
];
for (const file of cases) {
  const html = read(file);
  assert(html.includes('class="case-toc"'), `${file}: sumário ausente.`);
  assert(html.includes('id="lightbox"'), `${file}: lightbox ausente.`);
  assert(html.includes('rel="canonical"'), `${file}: canonical ausente.`);
  assert(html.includes('application/ld+json'), `${file}: dados estruturados ausentes.`);
}

const auditor = read("cases/auditor-backups-dropbox/index.html");
assert(auditor.includes("não executa o backup das VMs"), "Escopo do Auditor está ambíguo.");
assert(auditor.includes("object-fit: contain") || read("style.css").includes("object-fit: contain"), "Evidência do Auditor pode ser cortada.");

const chrome = read("cases/incidente-extensao-chrome/index.html");
assert(chrome.includes("vetor inicial não confirmado"), "Limitação central do incidente não foi preservada.");
assert(chrome.includes("16 páginas"), "Extensão do relatório não foi documentada.");

const oldRoutes = [
  ["reports/index.html", "incidente-extensao-chrome"],
  ["automations/index.html", "auditor-backups-dropbox"],
  ["projects/index.html", "sinalyx"],
  ["projects/index.html", "veonyx-arquitetura"],
];
for (const [file, marker] of oldRoutes) assert(read(file).includes(marker), `${file}: compatibilidade ${marker} ausente.`);

console.log("RUNTIME OK");
console.log("- Menu, lightbox, cases canônicos e rotas antigas: OK");
