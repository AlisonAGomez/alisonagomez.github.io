# Portfólio Alison Gomez

Portfólio profissional publicado no GitHub Pages com foco em Segurança da Informação e automação, seguido por infraestrutura, redes e suporte técnico.

## Posicionamento

O site apresenta experiências e projetos com base em evidências verificáveis:

- automação da auditoria de backups em ambiente multiempresa;
- resposta a incidente com extensão maliciosa no Chrome;
- análise de logs de firewall com o Sinalyx;
- suporte, monitoramento, redes e infraestrutura;
- desenvolvimento aplicado com o VeoNyx.

O conteúdo diferencia funcionalidades implementadas, itens em validação, roadmap e limitações. Dados de clientes, credenciais e identificadores internos não são publicados.

## Rotas principais

- Home: <https://alisonagomez.github.io/>
- Projetos: <https://alisonagomez.github.io/projects/>
- Sinalyx: <https://alisonagomez.github.io/projects/?id=sinalyx>
- VeoNyx: <https://alisonagomez.github.io/projects/?id=veonyx>
- Automações: <https://alisonagomez.github.io/automations/>
- Auditor de Backups Dropbox: <https://alisonagomez.github.io/automations/?id=auditor-backups-dropbox>
- Relatórios: <https://alisonagomez.github.io/reports/>
- Incidente Chrome: <https://alisonagomez.github.io/reports/?id=extensao-maliciosa-chrome>

## Estrutura

- `index.html`: página inicial orientada a recrutadores.
- `projects/`: catálogo e detalhes de projetos.
- `automations/`: catálogo e estudos de caso de automações.
- `reports/`: relatórios e cases de segurança defensiva.
- `assets/projects/projects.json`: conteúdo estruturado dos projetos.
- `assets/automations/automations.json`: conteúdo estruturado das automações.
- `assets/reports/reports.json`: conteúdo estruturado dos relatórios.
- `assets/curriculo-alison-gomez.pdf`: currículo canônico publicado.
- `tests/validate_portfolio.py`: validação de HTML, JSON, links e assets.

## Validação local

```powershell
py -3.10 -m http.server 8132 --bind 127.0.0.1
py -3.10 tests\validate_portfolio.py
node --check script.js
```

Abra <http://127.0.0.1:8132/> para revisar o resultado antes de publicar.

## Publicação segura

As alterações devem ser preparadas em branch própria e revisadas localmente. A branch e a tag `fallback/pre-reestrutura-portfolio-20260714` preservam o estado anterior a esta reestruturação.
