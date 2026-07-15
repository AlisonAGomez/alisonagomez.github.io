const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const assert = (condition, message) => { if (!condition) throw new Error(message); };

const script = read("script.js");
const style = read("style.css");
const circuitDecor = read("assets/img/decor/circuit-traces.svg");
const circuitMotion = read("assets/img/decor/circuit-motion.svg");
assert(!script.includes("typeNextFrame"), "Efeito de digitação não deveria existir.");
assert(script.includes("Escape"), "Menu precisa fechar com Escape.");
assert(script.includes('event.key !== "Tab"'), "Menu precisa conter o foco durante a navegação por teclado.");
assert(script.includes("menuLinks"), "Links do menu precisam participar do gerenciamento de foco.");
assert(script.includes("showModal"), "Lightbox acessível não foi inicializado.");
assert(script.includes("aria-expanded"), "Estado acessível do menu não foi implementado.");
assert(!script.includes('links[0]?.setAttribute("aria-current"'), "Página interna não pode marcar sempre o primeiro link.");
assert(script.includes('setCurrentSection(location.hash || "#home")'), "Home precisa inicializar a seção ativa antes do observer.");
assert(script.includes("const revealTargets"), "Reveal on scroll não foi inicializado.");
assert(script.includes("entry.isIntersecting"), "Reveal precisa responder à entrada na viewport.");
assert(script.includes('matchMedia("(prefers-reduced-motion: reduce)")'), "Motion precisa consultar a preferência de redução.");
assert(style.includes(".motion-ready .reveal-item"), "Estados visuais do reveal estão ausentes.");
assert(style.includes("@media (prefers-reduced-motion: reduce)"), "Fallback de movimento reduzido está ausente.");
assert(style.includes("circuit-traces.svg"), "Ambientação técnica de circuitos está ausente.");
assert(!style.includes("--grid-line"), "Grid técnico dominante não deveria permanecer.");
assert(circuitDecor.includes("01001110"), "Textura binária sutil está ausente.");
assert(circuitDecor.includes("<circle"), "Nós de conexão do circuito estão ausentes.");
assert(style.includes("circuit-motion.svg"), "Camada animada de circuitos está ausente.");
assert(style.includes(".lab-diagram"), "Diagrama responsivo do laboratório está sem estilos.");
assert(style.includes(".learning-track-grid"), "Grade de trilhas de estudo está sem estilos.");
assert(style.includes(".credentials-grid"), "Grade de certificações está sem estilos.");
assert(circuitMotion.includes("@keyframes circuit-flow"), "Pulso animado das trilhas está ausente.");
assert(circuitMotion.includes("@keyframes node-glow"), "Brilho animado dos nós está ausente.");
assert(circuitMotion.includes("@keyframes binary-breathe"), "Variação sutil dos binários está ausente.");
assert(circuitMotion.includes("@media (prefers-reduced-motion: reduce)"), "Asset animado não respeita movimento reduzido.");
assert(Buffer.byteLength(circuitDecor, "utf8") < 12000, "Asset de circuitos ficou pesado demais.");
assert(Buffer.byteLength(circuitMotion, "utf8") < 5000, "Asset animado ficou pesado demais.");
assert(!style.includes("@keyframes glitch"), "Glitch pesado não deve ser introduzido.");

const routeHelper = script.match(/function activeNavigationHashForPath\(pathname\) \{[\s\S]*?\n\}/);
assert(routeHelper, "Função de navegação ativa por rota ausente.");
const activeNavigationHashForPath = new Function(`${routeHelper[0]}; return activeNavigationHashForPath;`)();
for (const route of [
  "/cases/incidente-extensao-chrome/",
  "/cases/auditor-backups-dropbox/index.html",
  "/projects/",
  "/reports/index.html",
  "/automations/",
]) {
  assert(activeNavigationHashForPath(route) === "#cases", `${route}: deveria marcar Cases.`);
}
assert(activeNavigationHashForPath("/labs/vmware-security-lab/") === "#laboratory", "Laboratório deveria marcar a seção Laboratório.");
assert(activeNavigationHashForPath("/") === null, "A home deve usar a seção visível para definir o link ativo.");

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
  assert(html.includes('property="og:image:alt"'), `${file}: texto alternativo Open Graph ausente.`);
}

const home = read("index.html");
assert(!home.includes("case-card-featured"), "Destaque permanente não deve existir nos cards.");
assert(home.includes("Análise e resposta a malware"), "Novo card de resposta a malware ausente.");
assert(home.includes("Automação operacional"), "Novo card de automação operacional ausente.");
assert(!home.includes("<strong>16</strong><span>páginas</span>"), "Card antigo de 16 páginas ainda existe.");
assert(!home.includes("<strong>3</strong><span>formatos</span>"), "Card antigo de 3 formatos ainda existe.");
assert(home.includes('id="laboratory"'), "Seção Laboratório ausente na home.");
assert(home.includes("assets/img/certifications/ibsec-boas-praticas-sanitizado.webp"), "Evidência sanitizada IBSEC ausente.");
assert(home.includes('rel="noopener noreferrer"'), "Links de prática precisam usar noopener e noreferrer.");
assert(!home.includes("Relatório completo, sem corte lateral"), "Texto antigo do Auditor não deve ser publicado.");
assert(home.includes("Recorte do relatório consolidado com título, indicadores e prioridades da semana"), "Nova thumbnail do Auditor sem alt específico.");

const auditor = read("cases/auditor-backups-dropbox/index.html");
assert(auditor.includes("não executa o backup das VMs"), "Escopo do Auditor está ambíguo.");
assert(auditor.includes("Relatório consolidado para revisão operacional"), "Título revisado do relatório consolidado ausente.");
assert(auditor.includes("object-fit: contain") || read("style.css").includes("object-fit: contain"), "Evidência do Auditor pode ser cortada.");

const chrome = read("cases/incidente-extensao-chrome/index.html");
assert(chrome.includes("vetor inicial não confirmado"), "Limitação central do incidente não foi preservada.");
assert(chrome.includes("16 páginas"), "Extensão do relatório não foi documentada.");

const lab = read("labs/vmware-security-lab/index.html");
for (const marker of ["Kali Linux", "Windows Server", "Ubuntu Server", "Windows 10", "pfSense"]) {
  assert(lab.includes(marker), `Laboratório sem a VM ${marker}.`);
}
assert(lab.includes("Não são realizados testes contra terceiros"), "Política de uso controlado ausente.");
assert(lab.includes('data-back-fallback="laboratory"'), "Retorno seguro do laboratório está ausente.");
assert(lab.includes('rel="canonical"'), "Página do laboratório sem canonical.");
assert(lab.includes('application/ld+json'), "Página do laboratório sem dados estruturados.");

const oldRoutes = [
  ["reports/index.html", "incidente-extensao-chrome"],
  ["automations/index.html", "auditor-backups-dropbox"],
  ["projects/index.html", "sinalyx"],
  ["projects/index.html", "veonyx-arquitetura"],
];
for (const [file, marker] of oldRoutes) {
  const html = read(file);
  assert(html.includes(marker), `${file}: compatibilidade ${marker} ausente.`);
  assert(html.includes('content="noindex,follow"'), `${file}: noindex,follow ausente.`);
  assert(html.includes("Catálogo técnico"), `${file}: identificação de catálogo ausente.`);
  assert(!html.includes("Rota de compatibilidade"), `${file}: rótulo antigo ainda presente.`);
}

for (const forbidden of [
  "docs/capturas-v3",
  "docs/RELATORIO_VALIDACAO_V3.md",
  "docs/auditoria-portfolio-20260714.md",
]) {
  assert(!fs.existsSync(path.join(root, forbidden)), `${forbidden}: artefato interno ainda está na árvore pública.`);
}
assert(fs.existsSync(path.join(root, "assets/img/cases/veonyx/arquitetura.webp")), "WebP da arquitetura VeoNyx ausente.");
assert(!fs.existsSync(path.join(root, "assets/img/cases/veonyx/arquitetura.png")), "PNG pesado da arquitetura VeoNyx ainda existe.");
assert(read("cases/veonyx-arquitetura/index.html").includes("arquitetura.webp"), "Case VeoNyx não usa a mídia otimizada.");

console.log("RUNTIME OK");
console.log("- Menu, navegação ativa, motion acessível, cases, SEO, mídia e rotas antigas: OK");
