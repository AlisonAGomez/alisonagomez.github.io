# Relatório de implementação e validação da V3

Data da validação: 15/07/2026  
Branch: `codex/portfolio-v3-security-infra`  
Estado: pronta para revisão, sem merge e sem publicação

## Preservação e versionamento

- `main` publicada confirmada em `04d6daaeae422c5597a28895a3d24cd7aaac7797`.
- V1 preservada em `archive/portfolio-v1-legacy`, commit `61d808221603b7fb262a86144acad92312062418`.
- Tag da V1: `portfolio-v1-legacy-20260701`.
- V2 preservada em `archive/portfolio-v2-evidence`, apontando exatamente para a `main` publicada.
- Tag da V2: `portfolio-v2-evidence-20260714`, no mesmo hash da `main`.
- A V3 foi desenvolvida somente em `codex/portfolio-v3-security-infra`.

## Implementação

- Nova home orientada a recrutadores, com posicionamento em Infraestrutura, Redes, Suporte N1/N2/N3, Segurança da Informação e Automação.
- Foto original preservada e otimizada em WebP; enquadramento completo em desktop/notebook e remoção intencional nos formatos estreitos.
- Ordem principal dos cases: incidente do Chrome, Auditor de Backups e Sinalyx.
- Cases canônicos com problema, ação, resultado, evidências, decisões e limitações.
- Auditor de Backups com escopo factual: auditoria de backups já armazenados, sem afirmar que a aplicação executa o backup das VMs.
- Sinalyx apresentado como análise de logs, arquitetura de dados e segurança defensiva.
- VeoNyx apresentado como estudo complementar de arquitetura em desenvolvimento local.
- Rotas antigas mantidas como catálogos de compatibilidade e redirecionadas para os cases canônicos quando recebem IDs conhecidos.
- Navegação global, retorno seguro, menu mobile acessível, lightbox com retorno de foco e fechamento por `Escape`.
- Metadados únicos, canonical, Open Graph, Twitter Cards, JSON-LD, sitemap e robots.
- Imagens de home e compartilhamento otimizadas; evidências detalhadas carregadas sob demanda.

## Testes executados

- `py -3.10 tests/validate_portfolio.py`: aprovado.
- `node tests/validate_runtime.js`: aprovado.
- `node --check script.js`: aprovado.
- `git diff --check`: aprovado; apenas avisos locais de normalização LF/CRLF.
- Auditoria HTTP local: 32 recursos internos responderam sem erro.
- Navegador: nove páginas sem erros ou avisos de console, sem imagens quebradas e sem rolagem horizontal nos formatos testados.
- Rotas antigas: quatro redirecionamentos confirmados no navegador.
- Acessibilidade: um `h1` por página, textos alternativos, dimensões de imagem, skip link, foco visível, menu com `aria-expanded`, lightbox por teclado e contrastes principais WCAG AA entre 9.04:1 e 17.44:1.
- Segurança: nenhuma chave privada, arquivo de credencial, `.env` ou padrão conhecido de token encontrado na árvore pública.
- Capturas: 18 PNGs com dimensões exatas, íntegros e visualmente não vazios.

## Capturas para revisão

Matriz da home em `docs/capturas-v3/matriz/`:

- `home-1440x900.png`
- `home-1366x768.png`
- `home-1024x768.png`
- `home-768x1024.png`
- `home-390x844.png`
- `home-360x800.png`

Cases e evidências em `docs/capturas-v3/cases/`:

- Chrome, Auditor, Sinalyx e VeoNyx em 1440x900 e 390x844.
- Três cases da home em desktop e mobile.
- Evidência completa do Auditor e lightbox em 1280x720.

## Arquivos alterados ou adicionados

Código, conteúdo e configuração:

- `.gitignore`
- `404.html`
- `README.md`
- `index.html`
- `style.css`
- `script.js`
- `sitemap.xml`
- `projects/index.html`
- `automations/index.html`
- `reports/index.html`
- `assets/projects/projects.json`
- `cases/incidente-extensao-chrome/index.html`
- `cases/auditor-backups-dropbox/index.html`
- `cases/sinalyx/index.html`
- `cases/veonyx-arquitetura/index.html`
- `tests/validate_portfolio.py`
- `tests/validate_runtime.js`
- `docs/RELATORIO_VALIDACAO_V3.md`

Mídia otimizada:

- `assets/img/optimized/perfil-alison-900.webp`
- `assets/img/optimized/thumb-auditor.webp`
- `assets/img/optimized/thumb-chrome.webp`
- `assets/img/optimized/thumb-pendrivao.webp`
- `assets/img/optimized/thumb-sinalyx.webp`
- `assets/img/optimized/thumb-veonyx.webp`
- `assets/img/optimized/thumb-zabbix.webp`
- `assets/img/social/auditor-1200x630.jpg`
- `assets/img/social/chrome-1200x630.jpg`
- `assets/img/social/portfolio-v3-1200x630.jpg`
- `assets/img/social/sinalyx-1200x630.jpg`
- `assets/img/social/veonyx-1200x630.jpg`

Capturas versionadas:

- Os 18 arquivos listados em `docs/capturas-v3/matriz/` e `docs/capturas-v3/cases/`.

## Limitações registradas

- O pacote Lighthouse não está instalado e o navegador headless externo é bloqueado pelo sandbox do ambiente. Não foi produzido um score Lighthouse.
- O desempenho foi validado por renderização real, ausência de erros, imagens completas, carregamento sob demanda e orçamento dos arquivos principais. A home usa HTML de cerca de 20 KB, CSS de 25 KB, JavaScript de 6 KB e thumbnails WebP entre 22 KB e 48 KB.
- Links externos não foram alterados nem submetidos a ações autenticadas; a auditoria HTTP cobriu os recursos locais do site.
- A V3 não foi mesclada na `main`, não alterou o GitHub Pages e não foi publicada.

## Revisão local

```powershell
py -3.10 -m http.server 8132 --bind 127.0.0.1
```

Abrir `http://127.0.0.1:8132/` e revisar a branch antes de qualquer merge.
