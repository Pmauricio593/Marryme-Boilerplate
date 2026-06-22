# Checklist de Produção — MarryMe

Acompanhe o progresso do plano de 8 semanas. Marque `[x]` conforme validar com o time.

**Fontes:** `docs/engenharia/00-PLANO-EXECUCAO.md` · `CURSOR_CONTEXT_MARRYME.md` · `SKILL_MARRYME.md`

**Última atualização:** Jun/2026

---

## Legenda

- `[ ]` pendente
- `[x]` concluído e validado por você
- `[~]` em andamento

---

## Semana 0 — Governança

- [x] Docs de engenharia em `docs/engenharia/`
- [x] `CLAUDE.md` na raiz
- [x] `.cursorrules` na raiz
- [x] Skill `.cursor/skills/marryme-sessao-engenharia/SKILL.md`
- [x] `CURSOR_CONTEXT_MARRYME.md` com link para `docs/engenharia/`
- [x] Você leu e validou este checklist

---

## Semanas 1–2 — Fundação (Marco 0 + Marco 1)

### Sessão 0.1 — Qualidade de código
- [x] `backend/requirements/dev.txt` (ruff, black, pre-commit, pytest)
- [x] `backend/pyproject.toml`
- [x] `backend/.pre-commit-config.yaml`
- [x] `backend/.editorconfig`
- [x] `ruff check .` sem erros (validado localmente)
- [x] `black --check .` ok (validado localmente)
- [x] `pre-commit run --all-files` ok (rode após `pre-commit install`)

### Sessão 0.2 — DX
- [x] `Makefile` com `lint`, `format`, `cov`, `pytest`
- [x] `backend/README.md` de engenharia
- [x] `.gitignore` cobre `.ruff_cache`, `.pytest_cache`, `htmlcov/`
- [x] `make lint` e `make test` funcionam — **Windows:** `.\mm.ps1 lint` e `.\mm.ps1 test` (Docker rodando)

### Sessão 1.1 — LOGGING
- [x] Dict `LOGGING` em settings
- [x] `LOG_LEVEL` no `.env.example`
- [x] Login gera log `marryme.auth` no console (validar com Docker)

### Sessão 1.2 — Settings split
- [x] `config/settings/` base / dev / prod
- [x] `DJANGO_ENV` no `.env.example`
- [x] `docker compose up` continua ok
- [x] Railway com `DJANGO_ENV=prod`

### Sessão 1.3 — Hardening prod
- [x] `check --deploy` sem warnings críticos
- [x] Erro 500 sem stack trace em prod
- [x] Cookies Secure em prod

**Gate semana 2:** `[x]` `make lint && make test` verdes · logs visíveis · deploy intacto

---

## Semanas 3–4 — Testes + OpenAPI + Frontend base

### Backend
- [x] pytest + `conftest.py` + factories
- [x] Testes `prestadores` (CRUD, fase, 403)
- [x] Testes `campanhas` — Health Score 39/40/69/70
- [x] Reforço testes `contas` + `roteiros` básico
- [x] `drf-spectacular` — `/api/v1/docs/`
- [x] `make cov` com cobertura medida

### Frontend
- [x] Next.js 14 scaffold (`app/`, `lib/api`, `types/`, tokens)
- [x] Login equipe (`POST /api/v1/auth/login/`)
- [x] Sonner para feedback (sem `alert()`)

**Gate semana 4:** CS loga no front local · OpenAPI lista contas + prestadores

---

## Semanas 5–6 — Sistema interno CS

### Telas
- [x] Dashboard prestadores (filtros, loading/erro/vazio)
- [x] Detalhe prestador (fase, sync Meta)
- [x] Campanhas + Health Score com ação traduzida
- [x] Convites CS (emitir / reenviar / revogar)
- [ ] Relatório IA + pauta de reunião

### Engenharia paralela
- [ ] `core/exceptions_domain.py`
- [x] CI GitHub Actions (lint + pytest)

**Gate semana 6:** Pipeline CS completo no front (criar → fase → health → convite)

---

## Semanas 7–8 — Portal + Roteiros + Go-live interno

### Portal (staging)
- [x] Página `/portal/convite?token=`
- [x] Aceitar convite + login portal
- [x] Perfil, campanhas, roteiros (assessoria restrita)

### Roteiros CS
- [x] Chat por prestador + streaming
- [x] Finalizar + aprovar roteiro

### Segurança e deploy
- [x] Testes isolamento — prestador A não vê B (Marco 7.1)
- [ ] N+1 corrigido nas listas CS
- [ ] ADRs iniciais em `docs/adr/`
- [ ] Deploy Railway + Vercel
- [ ] Smoke test documentado

**Gate semana 8:** Equipe opera 100% no sistema · portal staging ok · CI verde · Marco 7.1 verde

---

## Pós-semana 8 — Gate clientes reais

- [ ] Envio real WhatsApp/email de convites
- [ ] Revisão LGPD / PII em logs
- [ ] Fluxo assessoria validado manualmente
- [ ] Primeiro prestador real onboardado

---

## Níveis de maturidade (referência)

```text
[x] PRATICANTE   — Marco 0 + 1
[x] PROFISSIONAL — Marco 2 + 3 + 4 (parcial — front base + OpenAPI)
[ ] ESPECIALISTA — Marco 5 + 6
[ ] SÁBIO        — Marco 7
[ ] SÁBIO+FRONT  — Marco 8 completo
```

---

## Fora de escopo (não fazer agora)

- Prospecção / Apify
- Redesign site institucional
- Cobrança automática
- Magic link sem senha

---

## Notas da validação (preencha junto)

| Data | Sessão | Validado por | Observação |
|------|--------|--------------|------------|
| Jun/2026 | Gate S1–2 (Marco 0+1) | você | lint/test ok · logs marryme.auth · compose + Railway /health/ · check --deploy limpo |
