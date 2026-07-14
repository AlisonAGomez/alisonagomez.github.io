# Diagnóstico do portfólio antes da reestruturação

Data: 14/07/2026  
Branch de trabalho: `codex/portfolio-seguranca-automacao`  
Baseline preservada: commit `1b101c6536c414ca579cdbfea3989899cf044709`

## Estrutura atual

- Home extensa em `index.html`, com dez seções de peso visual semelhante.
- Catálogos e páginas de detalhes gerados a partir de três arquivos JSON.
- Rotas públicas em `projects/`, `automations/` e `reports/`.
- Identidade visual concentrada em `style.css`, com 5.253 linhas.
- Comportamentos compartilhados em `script.js`, incluindo digitação, menu, retorno, revelação, canvas e preloader.
- Conteúdo atual do Auditor confirmado no commit `d2e660f` do repositório `dropbox-backup-auditor`.

## Problemas encontrados

1. A proposta profissional divide atenção entre muitas áreas e não prioriza Segurança da Informação e automação.
2. A home apresenta dez seções longas, com pouco contraste de importância entre cases, cursos, laboratórios e ferramentas.
3. O visual usa excesso de caixa alta, fonte monoespaçada, bordas ciano, efeitos de terminal, scanline, ruído, glitch e preloader temático.
4. Um projeto acadêmico solicitado para remoção permanece na home e em `assets/projects/projects.json`.
5. O botão de currículo aponta para `assets/curriculo-alison-gomez.pdf`, que é um placeholder de uma página. O currículo completo está em `assets/Curriculo_Alison_Gomez_Completo.pdf`.
6. O relatório do incidente existe em dois PDFs com hash SHA-256 idêntico.
7. A página 404 redireciona qualquer rota desconhecida silenciosamente para a home.
8. O menu mobile não atualiza `aria-expanded`, não fecha com Escape e não restaura o foco.
9. As páginas de detalhe não têm breadcrumb, sumário, navegação contextual ou CTA repetido ao final.
10. IDs inexistentes nos catálogos abrem o primeiro item, em vez de mostrar conteúdo não encontrado.
11. O catálogo de automações repete o mesmo bloco de impacto técnico e usa “Repositório em breve” como resposta genérica.
12. O Sinalyx é descrito de forma genérica e não separa claramente recursos implementados, limites e próximos passos.
13. O VeoNyx recebe destaque semelhante aos cases de segurança, apesar de ser conteúdo complementar.

## Evidências verificadas

- Currículo completo: mais de 57 empresas, média de 30 chamados por dia e cerca de 15 alertas diários.
- Currículo completo: auditoria de backups de 37 empresas e redução da rotina de quase 5 horas para 30 a 60 minutos.
- Auditor atual: integração direta apenas com Dropbox; os arquivos de VM são produzidos pelo Proxmox e auditados no Dropbox.
- Auditor atual: cursores incrementais, checkpoints, histórico de VMs, periodicidade, retenções, chunks do rclone e relatórios PDF, CSV e JSON.
- Sinalyx atual: parser, feature engineering, modelos, heurística, ensemble, decision engine, FastAPI, PostgreSQL e dashboard Vue.
- VeoNyx atual: Flutter, NestJS, PostgreSQL, Redis, BullMQ e MinIO, com recursos implementados e roadmap documentados no repositório.
- Incidente Chrome: persistência por Machine Level User Cloud Policy, retorno após remoção manual e comportamentos compatíveis com captura de sessão e inputs, conforme relatório técnico.

## Arquivos envolvidos

- `index.html`
- `style.css`
- `script.js`
- `404.html`
- `projects/index.html`
- `automations/index.html`
- `reports/index.html`
- `assets/projects/projects.json`
- `assets/automations/automations.json`
- `assets/reports/reports.json`
- PDFs, imagens de cases, metadados e documentação.

## Alterações planejadas

1. Remover integralmente o projeto acadêmico indicado e tratar sua URL antiga como conteúdo não encontrado.
2. Reduzir a home para hero, provas, cases, experiência, competências, formação e contato.
3. Reposicionar o portfólio para segurança e automação, seguidas por infraestrutura, redes e suporte.
4. Transformar Auditor e incidente Chrome em estudos de caso completos e verificáveis.
5. Atualizar Sinalyx e VeoNyx com base no estado real de seus repositórios.
6. Reestruturar catálogos, navegação e páginas de detalhes.
7. Substituir a estética de terminal por uma interface técnica, sóbria e legível.
8. Corrigir currículo, PDF duplicado, 404, acessibilidade, SEO e desempenho.
9. Adicionar validações automatizadas para HTML, JSON, links internos e conteúdo removido.

## Riscos de regressão

- Quebrar URLs públicas existentes ou caminhos relativos usados pelo GitHub Pages.
- Reintroduzir conteúdo antigo do Auditor ao editar o JSON.
- Fazer afirmações incompatíveis com o código atual de Sinalyx ou VeoNyx.
- Ocultar CTAs ou provocar overflow em telas pequenas.
- Deixar referências órfãs depois da remoção do projeto indicado ou de PDFs duplicados.

## Elementos que devem ser preservados

- Conteúdo e imagens atuais do Auditor de Backups Dropbox.
- Métricas confirmadas no currículo, sem extrapolação.
- Relatório técnico e evidências sanitizadas do incidente Chrome.
- Sinalyx como case relevante de segurança e análise de logs.
- VeoNyx como demonstração complementar de desenvolvimento e arquitetura.
- Identidade escura, destaque ciano moderado e navegação direta de retorno.
- Repositórios, LinkedIn, currículo e contato existentes.

## Limitação da captura inicial

O site respondeu HTTP 200 na prévia local. A captura automatizada do “antes” foi tentada nos viewports solicitados, mas o navegador interno falhou ao iniciar e Chrome/Firefox headless foram bloqueados pelo ambiente com erro de acesso. A validação visual será repetida na etapa final; a prévia local permanecerá disponível para inspeção manual.
