# MarryMe Backend

Django 6 + DRF + Celery + PostgreSQL + Redis.

## Subir (Docker)

```bash
cp .env.example .env   # preencher SECRET_KEY
make upd
make migrate
```

API: http://localhost:8000/health/

## Comandos

**Windows (PowerShell):** use `.\mm.ps1` no lugar de `make`:

```powershell
.\mm.ps1 upd
.\mm.ps1 migrate
.\mm.ps1 lint
.\mm.ps1 test
```

**Linux/Mac ou Git Bash com GNU Make:**

| Comando | Função |
|---------|--------|
| `make up` / `make upd` | Sobe containers |
| `make migrate` | Aplica migrations |
| `make test` | Testes Django |
| `make pytest` | Testes pytest |
| `make lint` | ruff + black --check |
| `make format` | ruff --fix + black |
| `make cov` | Cobertura pytest |

## Estrutura

```text
apps/contas/       auth, convites, permissões (app de referência)
apps/prestadores/  pipeline e CRUD
apps/campanhas/    Meta Ads, Health Score
apps/roteiros/     chat IA
core/              infra transversal
integrations/      APIs externas
config/            settings, urls
```

## Documentação

- Plano de execução: `../docs/engenharia/00-PLANO-EXECUCAO.md`
- Checklist geral: `../CHECKLIST_PRODUCAO.md`
- Produto: `../CURSOR_CONTEXT_MARRYME.md`

## Dev local (sem Docker)

Comente `DATABASE_URL` no `.env` para SQLite. Instale deps:

```bash
pip install -r requirements/dev.txt
python manage.py runserver
```

## Smoke test (API — Swagger ou curl)

Pré-requisitos: Docker up (`.\mm.ps1 upd`), migrations aplicadas, usuário CS (`gate@test.com` / `gate123dev` se existir no seed local).

Base URL local: `http://localhost:8000` · Docs: `/api/v1/docs/`

| # | Passo | Endpoint | Esperado |
|---|--------|----------|----------|
| 1 | Health | `GET /health/` | 200 |
| 2 | Login CS | `POST /api/v1/auth/login/` | `access` + `refresh` |
| 3 | Listar prestadores | `GET /api/v1/prestadores/` | `{total, resultados, ...}` |
| 4 | Criar prestador | `POST /api/v1/prestadores/` | 201 |
| 5 | Atualizar fase | `POST /api/v1/prestadores/{id}/atualizar-fase/` | fase nova |
| 6 | Sync Meta | `POST /api/v1/prestadores/{id}/sync-meta/` | enfileirado ou ok |
| 7 | Health score | `GET /api/v1/health-scores/ultimo/?prestador={id}` | score ou 404 |
| 8 | Emitir convite | `POST /api/v1/prestadores/{id}/convites/` | `link_portal` |
| 9 | Listar convites | `GET /api/v1/prestadores/{id}/convites/` | paginado (`resultados`) |
| 10 | Validar token | `GET /api/v1/portal/convites/validar/?token=` | `valido: true` |
| 11 | Aceitar convite | `POST /api/v1/portal/convites/aceitar/` | tokens portal |
| 12 | Portal | login + `GET /api/v1/portal/perfil/` | dados do prestador |
| 13 | Chat | criar sessão → `POST .../mensagem/` ou `/stream/` | resposta IA |
| 14 | Finalizar roteiro | `POST /api/v1/sessoes/{id}/finalizar/` | `roteiro_final_id` |
| 15 | Relatório IA | `POST /api/v1/relatorios/{id}/gerar-analise/` → `GET` relatório | `dados_json.pauta_reuniao` |

**Celery obrigatório** nos passos 6, 13–15 (worker rodando). Rate limit ativo em prod (`429` em pt-BR).

## Deploy Railway (API — sem Vercel)

### Serviços

1. **Postgres** e **Redis** — plugins Railway, referenciar em `DATABASE_URL` e `REDIS_URL`.
2. **Web** — no painel Railway (serviço web):
   - **Root Directory:** `backend`
   - **Config-as-code file:** `/backend/railway.toml` (caminho absoluto no repo — o toml **não** segue o root directory)
   - Healthcheck: `GET /health/` (resposta esperada inclui `"openapi": true` após deploy correto)
3. **Celery worker** — **Config-as-code file:** `/backend/railway.worker.toml`, mesmo root `backend/`

> **Redeploy ≠ rebuild.** Se `/health/` não mostrar `"openapi": true`, o Railway pode estar servindo imagem Docker antiga. Faça **Deploy** do commit latest com **Clear build cache** (ou push novo commit). Confirme em Settings → Source que **Root Directory = `backend`**.

```bash
celery -A config worker --loglevel=info --concurrency=2
```

Celery Beat (sync Meta periódico) é opcional nesta fase — sync manual via API.

### Variáveis obrigatórias (web + worker)

| Variável | Exemplo / nota |
|----------|----------------|
| `DJANGO_ENV` | `prod` |
| `SECRET_KEY` | string longa aleatória |
| `DATABASE_URL` | Postgres Railway |
| `REDIS_URL` | Redis Railway |
| `ALLOWED_HOSTS` | domínio Railway, ex. `web-production-xxx.up.railway.app` |
| `ANTHROPIC_API_KEY` | para chat e Relatório IA |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` |
| `FRONTEND_URL` | URL Vercel do front — links de convite (`https://xxx.vercel.app`) |
| `CORS_ALLOWED_ORIGINS` | mesma URL Vercel + domínio final, separadas por vírgula |
| `META_ACCESS_TOKEN` | se usar sync Meta real |
| `SECURE_SSL_REDIRECT` | `True` em prod |

Web e worker devem compartilhar **as mesmas env vars** (mesmo `.env` no Railway).

## Deploy Vercel (frontend)

1. Importar repo — **Root Directory:** `frontend`
2. Framework: Next.js (detectado automaticamente)
3. Variável obrigatória:

| Variável | Valor |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | URL Railway da API, ex. `https://web-production-xxx.up.railway.app` |

4. Após deploy, atualizar no Railway: `FRONTEND_URL` e `CORS_ALLOWED_ORIGINS` com a URL Vercel
5. Redeploy Railway web se CORS mudou

CLI (alternativa):

```bash
cd frontend
npx vercel --prod
```

### Pós-deploy (full stack)

1. Confirmar `/health/` → 200
2. Rodar smoke (tabela acima) contra URL Railway
3. Verificar logs `marryme.campanhas` após passo 15 (task Relatório IA)
4. Smoke front: login CS → lista prestadores → portal convite (link com `FRONTEND_URL` correto)
