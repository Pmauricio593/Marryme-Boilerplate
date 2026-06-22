# CLAUDE.md — Regras do projeto MarryMe

Este arquivo é lido automaticamente pelo Claude Code. Ele orienta como agir neste repositório. Fontes de verdade: `CURSOR_CONTEXT_MARRYME.md` (produto/operação), `SKILL_MARRYME.md` (design/engenharia), `docs/engenharia/` (plano e padrões).

## O que é o projeto
Monorepo da MarryMe (agência de crescimento digital para prestadores de casamento, foco em músicos).
- `backend/` — Django 6 + DRF + Celery + Redis + Postgres. **Implementado.** É o foco atual.
- `frontend/` — Next.js (sistema interno + portal). **Ainda não criado.** Não trate como existente.
- Raiz — site institucional Jekyll. **Não redesenhar** nesta fase.

## Prioridade
CS primeiro (apps `prestadores`, `campanhas`, `roteiros`, `contas`). Prospecção/Apify **fora de foco** — não construir.

## Arquitetura (padrão obrigatório)
`View/API → Service → Integration → Model → Task`
- View fina: valida input, chama service/selector, serializa. Sem regra de negócio.
- Service: regra de negócio/escrita, dentro de `@transaction.atomic` quando relevante.
- Selector: leitura (querysets otimizados com select_related/prefetch_related).
- Integration (`integrations/`): isola APIs externas (Meta Ads, Claude). Sem regra de negócio.
- Model: estrutura + constraints + validação de domínio.
- Task (Celery): trabalho assíncrono; idempotente; chama service.
- App de referência: `apps/contas` (usa pacote `services/` e `views/`). Replicar esse padrão.

## Regras inegociáveis
1. Nunca exponha secrets/API keys (código, logs ou respostas). `.env` é local e ignorado pelo Git.
2. Nunca vaze stack trace em produção. Erros passam pelo handler `core/exceptions.py`.
3. Portal SEMPRE filtrado por `VinculoPrestador`; nunca confie em `prestador_id`/`query_params` do cliente para autorização.
4. Logs em stdout, logger `marryme.<dominio>` (existe dict LOGGING em settings).
5. Não refatore amplo sem ganho operacional claro. Mudança pequena e rastreável.
6. Não crie arquivos `.md` novos sem necessidade.
7. Não troque tipografia/cores fora dos tokens do `SKILL` (Cormorant Garamond + Plus Jakarta Sans).
8. Domínio em pt-BR; termos técnicos idiomáticos em inglês.

## Fluxo de trabalho
- Trabalhe no escopo de UMA sessão do `docs/engenharia/00-PLANO-EXECUCAO.md` por vez = 1 PR.
- Antes de codar: diagnostique o estado real do código.
- Teste acompanha a mudança (pytest; mocke integrações externas; cubra caso feliz + 403 + 400).
- Antes do PR: rode `make lint` e `make test`. Me mostre a saída.
- Commits em Conventional Commits: `tipo(escopo): descrição`.
- Se mudar arquitetura/endpoint/prioridade, atualize `CURSOR_CONTEXT_MARRYME.md`.

## Comandos úteis
```
make up            # Linux/Mac — no Windows: cd backend && .\mm.ps1 upd
make lint          # Windows: .\mm.ps1 lint
make test          # Windows: .\mm.ps1 test
```

## Quando estiver em dúvida
Pergunte antes de assumir. Não invente endpoints, dados, métricas ou depoimentos. Valide contra o código real. Se discordar de um padrão, proponha um ADR em `docs/adr/` — não improvise no PR.
