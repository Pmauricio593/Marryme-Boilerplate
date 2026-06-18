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
