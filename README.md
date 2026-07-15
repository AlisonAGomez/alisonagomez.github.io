# Portfólio Alison Gomez V3

Portfólio profissional estático com foco em Infraestrutura, Redes, Suporte N1/N2/N3, Segurança da Informação e Automação Operacional.

## Estado

- Branch de revisão: `codex/portfolio-v3-security-infra`
- Produção preservada: `main` no commit `04d6daaeae422c5597a28895a3d24cd7aaac7797`
- V1 legada: `archive/portfolio-v1-legacy` e `portfolio-v1-legacy-20260701`
- V2 publicada: `archive/portfolio-v2-evidence` e `portfolio-v2-evidence-20260714`

Nenhum merge ou deploy da V3 deve ser feito antes da aprovação visual.

## Rotas canônicas

- `/cases/incidente-extensao-chrome/`
- `/cases/auditor-backups-dropbox/`
- `/cases/sinalyx/`
- `/cases/veonyx-arquitetura/`
- `/labs/vmware-security-lab/`

As rotas antigas em `reports/`, `automations/` e `projects/` continuam disponíveis e redirecionam os IDs principais.

## Revisão local

```powershell
py -3.10 -m http.server 8132 --bind 127.0.0.1
py -3.10 tests\validate_portfolio.py
node --check script.js
node tests\validate_runtime.js
```

Abra `http://127.0.0.1:8132/` para revisar a V3 localmente.

## Conteúdo e privacidade

- O currículo publicado é a fonte canônica para cargos, empresas e datas.
- Evidências do incidente e do Auditor são sanitizadas.
- Credenciais, identificadores internos, dados reais de clientes, `.env` e artefatos de execução não fazem parte do site.
