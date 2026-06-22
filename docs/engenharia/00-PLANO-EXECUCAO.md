# Plano de Execução de Engenharia — MarryMe Backend

> **Objetivo deste documento**
> Levar o backend da MarryMe do estado atual (boilerplate funcional, porém imaturo em qualidade) até o nível **"sábio profissional"**: um sistema que um engenheiro sênior assinaria embaixo — testado, observável, seguro, documentado e fácil de evoluir.
>
> Este é um **plano de execução formal**, dividido em **marcos** e **sessões**. Cada sessão tem objetivo, pré-requisitos, passo a passo com comandos exatos, arquivos a tocar, critério de aceite (Definition of Done) e a mensagem de commit. As sessões foram desenhadas para serem executadas ao longo dos dias, com auxílio do **Cursor** e do **Claude Code** (ver `02-OPERACAO-IA.md`).
>
> Fontes de verdade que este plano respeita e nunca contradiz: `CURSOR_CONTEXT_MARRYME.md` (produto/operação) e `SKILL_MARRYME.md` (design/engenharia). Padrões de código detalhados em `01-PADROES-CODIGO.md`. Bibliografia em `03-REFERENCIAS.md`.

---

## 0. Como ler e usar este plano

1. **Ordem importa.** Os marcos foram ordenados por dependência técnica. Não pule o Marco 0 e o Marco 1 — eles são a fundação. Sem `LOGGING`, testes e ferramentas de qualidade, todo o resto é construído sobre areia.
2. **Uma sessão = um Pull Request.** Cada sessão termina em um PR pequeno e rastreável. Isso respeita a diretriz do `CURSOR_CONTEXT` ("manter mudanças pequenas e rastreáveis").
3. **Nunca refatore sem ganho operacional claro.** O `CURSOR_CONTEXT` proíbe refatoração ampla. Por isso, cada sessão é cirúrgica: muda um aspecto, valida, entrega.
4. **CS é a prioridade.** Quando houver conflito de tempo, priorize o que destrava o time interno (apps `prestadores`, `campanhas`, `roteiros`, `contas`). Prospecção/Apify ficam fora de foco.
5. **Marque o checklist.** Ao final de cada sessão, marque o DoD. Só abra a próxima sessão com a anterior verde.

### Convenções de notação

- `$` = comando de terminal. Quando for dentro do container, é explícito (`docker compose exec web ...`).
- `📁` = arquivo/pasta a criar ou editar.
- `✅ DoD` = Definition of Done — critério objetivo de "pronto".
- `🤖 Prompt` = sugestão de prompt para Cursor/Claude Code.
- `💾 Commit` = mensagem de commit (padrão Conventional Commits).

---

## 1. Modelo de Níveis — de Aprendiz a Sábio

O alvo "nível do sábio" precisa de uma régua objetiva. Adotamos uma escada de maturidade de engenharia. Use-a para saber **onde você está** e **o que falta**. (Ajuste os nomes se o seu mentor usar outra nomenclatura — a substância é o que importa.)

| Nível | Nome | O que caracteriza | Marcos que entregam |
|-------|------|-------------------|---------------------|
| 1 | **Aprendiz** | "Funciona na minha máquina." Código roda, mas sem testes, sem padrão, sem observabilidade. | *(estado atual)* |
| 2 | **Praticante** | Ambiente reprodutível, lint/format automáticos, logging real, config separada por ambiente. | Marco 0, Marco 1 |
| 3 | **Profissional** | Testado de verdade (cobertura medida), arquitetura consistente em todos os apps, contratos de API explícitos. | Marco 2, Marco 3, Marco 4 |
| 4 | **Especialista** | CI/CD que barra regressão, performance medida, integrações resilientes (retry, idempotência). | Marco 5, Marco 6 |
| 5 | **Sábio** | Segurança e isolamento auditados, decisões documentadas (ADRs), o sistema ensina quem chega depois. Frontend integrado ao contrato. | Marco 7, Marco 8 |

**Princípio do sábio:** o código não é só correto — ele é *óbvio*. Quem chega depois entende em minutos por que cada coisa está onde está. Esse é o teste final de cada sessão.

---

## 2. Diagnóstico do Estado Atual (linha de base)

Levantamento feito sobre o código real do repositório (`backend/`). É o ponto de partida honesto.

### O que já está bom (preservar)

- **Estrutura de apps por domínio** (`apps/contas`, `apps/prestadores`, `apps/campanhas`, `apps/roteiros`) — alinhada ao `CURSOR_CONTEXT`.
- **Camada `core/`** com `authentication.py`, `permissions.py`, `pagination.py`, `exceptions.py` — boa base de infraestrutura transversal.
- **Padrão `View → Service → Integration → Model → Task`** já presente (ex.: `campanhas/services.py` chama `integrations/meta_ads.py`).
- **`contas`** já adota o padrão maduro: pacote `services/` (vários arquivos) e pacote `views/` — é o modelo a replicar.
- **Handler de exceções centralizado** (`core/exceptions.py`) com tradução de erros em pt-BR.
- **Config por env vars** via `python-decouple`; `.env` **não** está versionado (correto); há `.env.example`.
- **Celery** configurado (broker Redis, resultados no Postgres via `django-celery-results`), beat com `DatabaseScheduler`.
- **Docker** (web + celery), `Makefile`, deploy Railway, `whitenoise` para estáticos.

### Lacunas que separam do nível sábio (atacar)

| # | Lacuna | Evidência no código | Marco que resolve |
|---|--------|---------------------|-------------------|
| L1 | **Sem `LOGGING` configurado** | `getLogger('marryme.*')` usado em `core/`, `campanhas`, `roteiros`, mas **não existe dict `LOGGING`** em `settings.py`. Logs caem no handler raiz, sem formato nem nível controlado. | Marco 1 |
| L2 | **Testes só em `contas`** | `campanhas/tests.py`, `prestadores/tests.py`, `roteiros/tests.py` são stubs (`# Create your tests here.`). | Marco 2 |
| L3 | **Sem lint/format/import-sort** | Nenhum `ruff`, `black`, `isort`, `pre-commit` no projeto. Ordem de import inconsistente entre arquivos. | Marco 0 |
| L4 | **`settings.py` monolítico** | Um único arquivo, sem split `base/dev/prod`, sem hardening (`SECURE_*`, HSTS, cookies seguros). | Marco 1 |
| L5 | **`requirements` sem camadas** | Só `base.txt` (pinado, bom), mas sem `dev.txt` (pytest, ruff, etc.) nem separação prod. | Marco 0 |
| L6 | **Camada de services inconsistente** | `contas` usa pacote `services/`; `campanhas`/`prestadores`/`roteiros` usam `services.py` único. Sem padrão de *selectors* (leitura) vs *services* (escrita). | Marco 3 |
| L7 | **Sem documentação de API** | Não há OpenAPI/Swagger. Contrato vive só no código e no `CURSOR_CONTEXT`. | Marco 4 |
| L8 | **Sem CI/CD** | Nenhum workflow (`.github/workflows`). Nada barra um PR que quebra teste ou lint. | Marco 5 |
| L9 | **Models sem índices/constraints explícitos** | Ex.: `Prestador` sem `indexes`/`constraints`; sem validação de domínio além de `choices`. Risco de N+1 não auditado. | Marco 6 |
| L10 | **Segurança/multi-tenant não auditados** | Isolamento do portal por `VinculoPrestador` precisa de teste que prove que prestador A não vê dados de B. | Marco 7 |
| L11 | **Sem exceptions de domínio** | Services levantam `ValueError`/genéricas (ex.: `TokenService`); o handler não distingue erro de negócio de erro técnico. | Marco 3 |

---

## 3. Visão Geral dos Marcos

```text
Marco 0  Fundação de qualidade        (Aprendiz → Praticante)       ~2 sessões
Marco 1  Observabilidade & Config     (Praticante)                  ~3 sessões
Marco 2  Testes de verdade            (Praticante → Profissional)   ~4 sessões
Marco 3  Arquitetura consistente      (Profissional)                ~3 sessões
Marco 4  Contrato de API              (Profissional → Especialista) ~2 sessões
Marco 5  CI/CD                        (Especialista)                ~2 sessões
Marco 6  Performance & resiliência    (Especialista → Sábio)        ~3 sessões
Marco 7  Segurança & multi-tenant     (Sábio)                       ~2 sessões
Marco 8  Frontend Next.js (contrato)  (Sábio, fase futura)          ~3+ sessões
```

> **Ritmo sugerido:** 1 sessão por dia útil. Marcos 0→7 cabem em ~4 semanas de execução focada. O Marco 8 é a ponte para o frontend e só começa depois do backend sólido (regra do `CURSOR_CONTEXT`).

---

# MARCO 0 — Fundação de Qualidade

**Nível alvo:** Aprendiz → Praticante.
**Por quê primeiro:** sem ferramentas de qualidade automáticas, todo código novo nasce inconsistente. Estabelecer o "trilho" antes de andar.
**Não fazer:** nenhuma mudança de lógica de negócio neste marco. Só ferramentas e config.

## Sessão 0.1 — Ferramentas de qualidade (ruff + black + pre-commit)

**Objetivo:** lint, formatação e ordenação de imports automáticos e padronizados.
**Pré-requisitos:** ambiente local rodando (`make up` ou venv).

**Passo a passo**

1. Criar 📁 `backend/requirements/dev.txt`:
   ```text
   -r base.txt
   ruff==0.6.9
   black==24.10.0
   pre-commit==4.0.1
   pytest==8.3.3
   pytest-django==4.9.0
   pytest-cov==5.0.0
   factory-boy==3.3.1
   Faker==30.3.0
   model-bakery==1.20.0
   ```
   > `isort` não precisa ser instalado à parte: o **ruff** já ordena imports (regra `I`). Mantemos `black` para formatação e `ruff` para lint + import sort.

2. Criar 📁 `backend/pyproject.toml` com a config central (única fonte de verdade de estilo):
   ```toml
   [tool.ruff]
   target-version = "py314"
   line-length = 100
   extend-exclude = ["migrations", "staticfiles", "venv"]

   [tool.ruff.lint]
   select = ["E", "F", "I", "UP", "B", "DJ", "C4", "SIM"]
   # E/F pyflakes+pycodestyle, I isort, UP pyupgrade,
   # B bugbear, DJ flake8-django, C4 comprehensions, SIM simplify
   ignore = ["E501"]  # comprimento de linha fica com o black

   [tool.ruff.lint.isort]
   known-first-party = ["apps", "core", "config", "integrations"]
   section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

   [tool.black]
   line-length = 100
   target-version = ["py314"]
   extend-exclude = "migrations|staticfiles|venv"
   ```

3. Criar 📁 `backend/.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.6.9
       hooks:
         - id: ruff
           args: [--fix]
         - id: ruff-format
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v5.0.0
       hooks:
         - id: trailing-whitespace
         - id: end-of-file-fixer
         - id: check-merge-conflict
         - id: check-yaml
         - id: detect-private-key   # impede vazar secret
   ```

4. Instalar e ativar:
   ```bash
   $ pip install -r requirements/dev.txt
   $ pre-commit install
   ```

5. Rodar uma vez sobre todo o projeto e revisar o diff **com calma** (não aceitar mudança que altere comportamento):
   ```bash
   $ ruff check . --fix
   $ black .
   $ pre-commit run --all-files
   ```

6. Criar 📁 `backend/.editorconfig` (consistência entre editores/Cursor):
   ```ini
   root = true
   [*]
   charset = utf-8
   end_of_line = lf
   insert_final_newline = true
   trim_trailing_whitespace = true
   indent_style = space
   [*.py]
   indent_size = 4
   [*.{yml,yaml,json,toml}]
   indent_size = 2
   ```

**✅ DoD**
- [ ] `ruff check .` retorna 0 erros.
- [ ] `black --check .` retorna "would not reformat".
- [ ] `pre-commit run --all-files` passa.
- [ ] Nenhuma mudança de comportamento no diff (só estilo/imports).
- [ ] Migrations **não** foram tocadas pelo formatter (excluídas).

**🤖 Prompt (Cursor/Claude Code)**
> "Aplique o pyproject.toml e o pre-commit que acabei de adicionar. Rode ruff --fix e black. Me mostre o diff agrupado por tipo de mudança (imports, espaçamento, simplificações). Não altere nenhuma lógica; se um fix do ruff mudar comportamento, reverta e me avise."

**💾 Commit**
```
chore(qa): adiciona ruff, black e pre-commit com config central
```

## Sessão 0.2 — Makefile, README de engenharia e .gitignore

**Objetivo:** comandos padronizados e onboarding de dev em 1 página.

**Passo a passo**

1. Expandir 📁 `backend/Makefile` com alvos de qualidade (mantendo os atuais):
   ```makefile
   lint:
   	ruff check .
   	black --check .

   format:
   	ruff check . --fix
   	black .

   test:
   	docker compose exec web pytest

   cov:
   	docker compose exec web pytest --cov=apps --cov=core --cov-report=term-missing
   ```

2. Conferir 📁 `backend/.gitignore` cobre: `.env`, `*.sqlite3`, `__pycache__/`, `.pytest_cache/`, `htmlcov/`, `.ruff_cache/`, `celerybeat-schedule*`.
   > `celerybeat-schedule` já está no `.gitignore` e **não** está versionado (verificado). Só garanta que continua ignorado e adicione os caches novos (`.pytest_cache/`, `.ruff_cache/`, `htmlcov/`). Se algum dia aparecer tracked: `git rm --cached backend/celerybeat-schedule`.

3. Criar 📁 `backend/README.md` com: stack, como subir (Docker e venv), comandos `make`, mapa de pastas, e link para `docs/engenharia/`.

**✅ DoD**
- [ ] `make lint`, `make format`, `make test`, `make cov` funcionam.
- [ ] `celerybeat-schedule` não aparece mais em `git status` como tracked.
- [ ] README permite que um dev novo suba o projeto sem perguntar nada.

**💾 Commit**
```
chore(dx): expande Makefile, README de engenharia e limpa .gitignore
```

---

# MARCO 1 — Observabilidade & Configuração

**Nível alvo:** Praticante.
**Por quê:** sem logging estruturado e config por ambiente, você não enxerga o que o sistema faz em produção, e segredos/segurança ficam frágeis. **Esta é a lacuna mais urgente (L1).**

## Sessão 1.1 — Configurar `LOGGING` (corrige L1)

**Objetivo:** os `getLogger('marryme.*')` espalhados pelo código passam a produzir logs reais, em stdout (regra do `SKILL_MARRYME`: "logs em stdout").

**Passo a passo**

1. Em 📁 `backend/config/settings.py`, adicionar o dict `LOGGING` (logo após `REST_FRAMEWORK`/`SIMPLE_JWT`):
   ```python
   LOG_LEVEL = config('LOG_LEVEL', default='INFO')

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{asctime} {levelname} {name} {message}',
               'style': '{',
           },
           'json': {  # produção: 1 linha por evento, fácil de indexar
               'format': '{"ts":"%(asctime)s","level":"%(levelname)s",'
                         '"logger":"%(name)s","msg":"%(message)s"}',
           },
       },
       'handlers': {
           'console': {
               'class': 'logging.StreamHandler',
               'formatter': 'verbose' if DEBUG else 'json',
           },
       },
       'root': {'handlers': ['console'], 'level': 'WARNING'},
       'loggers': {
           'marryme': {  # captura marryme.auth, marryme.campanhas, etc.
               'handlers': ['console'],
               'level': LOG_LEVEL,
               'propagate': False,
           },
           'django.request': {
               'handlers': ['console'],
               'level': 'ERROR',
               'propagate': False,
           },
       },
   }
   ```

2. Padronizar os nomes de logger por app (já são `marryme.<app>`): confirmar em `core/authentication.py` (`marryme.auth`), `core/exceptions.py` (`marryme.exceptions`), `campanhas/services.py` (`marryme.campanhas`), `roteiros/*` (`marryme.roteiros`). Onde faltar, padronizar para `marryme.<app>`.

3. Adicionar `LOG_LEVEL=INFO` ao `.env.example`.

**✅ DoD**
- [ ] Subindo o servidor, um login gera no console: `... INFO marryme.auth Auth OK: ...`.
- [ ] Em `DEBUG=False`, o log sai em formato JSON (1 linha por evento).
- [ ] Nenhum logger "marryme.*" fica sem handler.

**🤖 Prompt**
> "Adicione o dict LOGGING em config/settings.py conforme docs/engenharia/00-PLANO-EXECUCAO.md Sessão 1.1. Depois faça uma busca por logging.getLogger no backend e confirme que todos os nomes começam com 'marryme.'. Liste os que não seguem o padrão."

**💾 Commit**
```
feat(core): configura LOGGING estruturado (console/JSON) para loggers marryme.*
```

## Sessão 1.2 — Split de settings (`base/dev/prod`) — corrige L4

**Objetivo:** separar config por ambiente sem quebrar nada (Railway aponta para `config.settings`).

**Passo a passo**

1. Transformar 📁 `config/settings.py` em pacote 📁 `config/settings/`:
   ```text
   config/settings/
   ├── __init__.py      # decide o módulo por DJANGO_ENV
   ├── base.py          # tudo que é comum (o conteúdo atual, menos toggles)
   ├── dev.py           # from .base import *  ; DEBUG=True; CORS liberado local
   └── prod.py          # from .base import *  ; hardening (ver Sessão 1.3)
   ```

2. Em `base.py`, manter INSTALLED_APPS, MIDDLEWARE, DRF, JWT, Celery, LOGGING.
3. `__init__.py` decide o módulo por env var:
   ```python
   import os
   _env = os.environ.get('DJANGO_ENV', 'dev')
   if _env == 'prod':
       from .prod import *  # noqa
   else:
       from .dev import *  # noqa
   ```
4. Confirmar `DJANGO_SETTINGS_MODULE = 'config.settings'` em `manage.py`, `wsgi.py`, `asgi.py`, `celery.py`.
5. Definir `DJANGO_ENV=prod` no Railway; `dev` é o default local.

**✅ DoD**
- [ ] `python manage.py check` passa em dev e com `DJANGO_ENV=prod`.
- [ ] `docker compose up` continua subindo igual.
- [ ] Deploy Railway funciona com `DJANGO_ENV=prod`.

**💾 Commit**
```
refactor(config): divide settings em base/dev/prod por DJANGO_ENV
```

## Sessão 1.3 — Hardening de segurança (prod) + erros não vazam

**Objetivo:** produção segura por padrão (regra do `SKILL_MARRYME`: "evitar retornos com stack trace").

**Passo a passo**

1. Em 📁 `config/settings/prod.py`:
   ```python
   from .base import *  # noqa

   DEBUG = False
   SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Railway
   SECURE_HSTS_SECONDS = 31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   SECURE_HSTS_PRELOAD = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_CONTENT_TYPE_NOSNIFF = True
   X_FRAME_OPTIONS = 'DENY'
   ```
2. Confirmar que `core/exceptions.py` não vaza stack (ele padroniza a resposta). Validar com teste em DEBUG=False.
3. Rodar a checagem de deploy do Django:
   ```bash
   $ DJANGO_ENV=prod python manage.py check --deploy
   ```
   Resolver cada warning relevante.

**✅ DoD**
- [ ] `check --deploy` sem warnings críticos.
- [ ] Em prod, erro 500 retorna `{"erro": "...", "status": 500}` sem stack.
- [ ] Cookies de sessão/CSRF marcados Secure em prod.

**💾 Commit**
```
feat(security): hardening de produção (HSTS, SSL redirect, cookies seguros)
```

---

# MARCO 2 — Testes de Verdade

**Nível alvo:** Praticante → Profissional.
**Por quê:** o `contas` já tem testes; os outros três apps são stubs (L2). Sem testes, nenhuma refatoração futura é segura.
**Meta de cobertura:** começar medindo, depois exigir **≥ 80%** nas camadas `services`/`views` dos apps de domínio.

## Sessão 2.1 — Migrar para pytest + fixtures + factories

**Passo a passo**

1. Criar 📁 `backend/pytest.ini`:
   ```ini
   [pytest]
   DJANGO_SETTINGS_MODULE = config.settings
   python_files = tests.py test_*.py *_tests.py
   addopts = --reuse-db --strict-markers
   ```
2. Criar 📁 `backend/conftest.py` com fixtures base (cliente API autenticado por role):
   ```python
   import pytest
   from rest_framework.test import APIClient

   @pytest.fixture
   def api():
       return APIClient()

   @pytest.fixture
   def usuario_cs(db, django_user_model):
       return django_user_model.objects.create_user(
           username='cs1', password='x', role='cs')

   @pytest.fixture
   def api_cs(api, usuario_cs):
       api.force_authenticate(user=usuario_cs)
       return api
   ```
3. Criar uma `factories.py` por app de domínio usando `factory_boy` (ex.: `PrestadorFactory`, `CampanhaFactory`). Padrão em `01-PADROES-CODIGO.md`, seção Testes.

**✅ DoD**
- [ ] `pytest` roda e o teste atual de `contas` passa sob pytest.
- [ ] `--reuse-db` acelera reexecução.

**💾 Commit**
```
test(infra): adota pytest, conftest com fixtures e factory_boy
```

## Sessão 2.2 — Testes do app `prestadores`

**Cobrir:** CRUD via API com permissão `IsCS`; `atualizar-fase`; `sync-meta` (mockando `MetaAdsClient`); `__str__`; ordering. Provar que role `prestador` **não** acessa endpoints de equipe.

**✅ DoD**
- [ ] ≥ 80% de cobertura em `prestadores/views.py` e `services.py`.
- [ ] Teste negativo de permissão (403) presente.

**💾 Commit**
```
test(prestadores): cobre CRUD, atualização de fase e sync Meta (mock)
```

## Sessão 2.3 — Testes do app `campanhas` (Health Score)

**Cobrir:** cálculo de **Health Score** com faixas do `SKILL_MARRYME` (70+ saudável, 40–69 atenção, <40 risco) — este é o coração de CS, então é o teste mais valioso do projeto. Mockar Meta Ads e Claude. Testar `TokenService` (token permanente não renova).

**✅ DoD**
- [ ] Faixas de Health Score testadas nos limiares (39, 40, 69, 70).
- [ ] Integrações externas mockadas (zero chamada real de rede no teste).
- [ ] `gerar-analise` testado com cliente Claude fake.

**💾 Commit**
```
test(campanhas): cobre Health Score, métricas e geração de análise (mocks)
```

## Sessão 2.4 — Testes do app `roteiros` + reforço em `contas`

**Cobrir:** criação de sessão, `mensagem` (mock Claude), `stream` (verificar formato SSE `data: ... [DONE]`), `arquivar`, `finalizar`, `aprovar`. Em `contas`: fluxo convite-primeiro completo (validar token → aceitar → cria usuário) e isolamento por `VinculoPrestador`.

**✅ DoD**
- [ ] Streaming testado sem chamar a API real.
- [ ] Fluxo de convite ponta a ponta verde.
- [ ] Cobertura global do projeto medida e registrada no README.

**💾 Commit**
```
test(roteiros,contas): cobre chat/stream e fluxo de convite
```

---

# MARCO 3 — Arquitetura Consistente

**Nível alvo:** Profissional.
**Por quê:** padronizar para que todo app "se pareça" — quem entende um, entende todos (L6, L11). Detalhes e exemplos em `01-PADROES-CODIGO.md`.

## Sessão 3.1 — Exceptions de domínio (corrige L11)

1. Criar 📁 `core/exceptions_domain.py` com hierarquia:
   ```python
   class DomainError(Exception):
       """Erro de regra de negócio (não é bug). HTTP 400/409."""
       mensagem = 'Operação inválida.'
       status_code = 400

   class RecursoIndisponivel(DomainError):
       mensagem = 'Recurso temporariamente indisponível.'
       status_code = 503
   # ... ConviteExpirado, TokenMetaAusente, etc.
   ```
2. Ensinar `core/exceptions.py` (handler) a reconhecer `DomainError` e responder com `mensagem`/`status_code`.
3. Trocar `raise ValueError(...)` dos services (ex.: `TokenService`) por exceptions de domínio.

**✅ DoD**
- [ ] Erros de negócio retornam status semântico (não 500).
- [ ] Teste cobre pelo menos 2 exceptions de domínio.

**💾 Commit** `refactor(core): exceptions de domínio e handler semântico`

## Sessão 3.2 — Padronizar camada de services em pacote (corrige L6)

Replicar o padrão maduro de `contas/services/` para `prestadores`, `campanhas`, `roteiros`: converter `services.py` em pacote `services/` com um arquivo por caso de uso. **Uma sessão por app se ficar grande** — manter PRs pequenos.

**✅ DoD**
- [ ] Imports atualizados; testes do Marco 2 continuam verdes.
- [ ] Nenhuma mudança de comportamento (só organização).

**💾 Commit** `refactor(<app>): converte services.py em pacote services/`

## Sessão 3.3 — Selectors (leitura) e views finas

1. Introduzir `selectors.py` por app para queries de leitura (separar leitura de escrita — padrão HackSoft).
2. Garantir que `views` só orquestram: validam input (serializer) → chamam service/selector → serializam saída. Nada de regra de negócio na view.

**✅ DoD**
- [ ] Querysets complexos saíram das views para selectors.
- [ ] Views não têm `if` de regra de negócio.

**💾 Commit** `refactor(arch): introduz selectors e afina as views`

---

# MARCO 4 — Contrato de API

**Nível alvo:** Profissional → Especialista.

## Sessão 4.1 — OpenAPI com drf-spectacular (corrige L7)

1. Adicionar `drf-spectacular` ao `base.txt`; registrar em INSTALLED_APPS e `DEFAULT_SCHEMA_CLASS`.
2. Expor `/api/v1/schema/` e `/api/v1/docs/` (Swagger UI).
3. Anotar views/serializers com `@extend_schema` onde o inferido não basta (ex.: actions `mensagem`, `stream`).

**✅ DoD**
- [ ] `/api/v1/docs/` lista todos os endpoints do `CURSOR_CONTEXT`.
- [ ] Schema gerado sem warnings.

**💾 Commit** `feat(api): documentação OpenAPI via drf-spectacular`

## Sessão 4.2 — Throttling, versionamento e paginação consistentes

1. Configurar `DEFAULT_THROTTLE_CLASSES`/`RATES` (anon + user) — protege a API e as integrações pagas (Claude/Meta).
2. Formalizar versionamento (`/api/v1/` já existe; documentar política de v2).
3. Garantir que toda lista usa `MarryMePagination`.

**✅ DoD**
- [ ] Estouro de rate limit retorna 429 com a mensagem pt-BR do handler.
- [ ] Todas as listas paginadas no formato `{total, paginas, ...}`.

**💾 Commit** `feat(api): throttling e paginação consistentes`

---

# MARCO 5 — CI/CD

**Nível alvo:** Especialista.

## Sessão 5.1 — GitHub Actions: lint + testes + cobertura (corrige L8)

1. Criar 📁 `.github/workflows/ci.yml`: matriz com Postgres + Redis de serviço; passos `ruff check`, `black --check`, `pytest --cov` com gate mínimo (`--cov-fail-under=80`).
2. Rodar em `push` e `pull_request`.

**✅ DoD**
- [ ] PR que quebra teste/lint fica vermelho e bloqueia merge.
- [ ] Badge de CI no README.

**💾 Commit** `ci: pipeline de lint, testes e cobertura no GitHub Actions`

## Sessão 5.2 — pre-commit no CI, Dependabot e deploy documentado

1. Job que roda `pre-commit run --all-files`.
2. 📁 `.github/dependabot.yml` para pip e github-actions.
3. Documentar o deploy Railway (`railway.toml`, `DJANGO_ENV=prod`, migrations no entrypoint) no README.

**✅ DoD**
- [ ] Dependabot abre PRs de atualização.
- [ ] Runbook de deploy escrito.

**💾 Commit** `ci: pre-commit, dependabot e runbook de deploy`

---

# MARCO 6 — Performance & Resiliência

**Nível alvo:** Especialista → Sábio.

## Sessão 6.1 — Índices, constraints e validação de models (corrige L9)

1. Adicionar `Meta.indexes` nos campos de filtro frequentes (ex.: `Prestador.fase`, `categoria`, `responsavel`; `HealthScore` por prestador+data).
2. Adicionar `constraints` (ex.: unicidade de vínculo ativo, faixas válidas).
3. Validação de domínio em `clean()`/validators (ex.: `estado` com 2 letras, valores monetários ≥ 0).
4. Gerar e revisar migrations.

**✅ DoD**
- [ ] Migrations criadas e aplicadas sem perda de dados.
- [ ] Teste prova que constraint barra dado inválido.

**💾 Commit** `perf(models): índices, constraints e validação de domínio`

## Sessão 6.2 — Auditoria de N+1 e query optimization

1. Instalar `nplusone`/`django-debug-toolbar` em dev.
2. Adicionar `select_related`/`prefetch_related` nos querysets das views/selectors (ex.: `Prestador.responsavel`, sessões→mensagens).
3. Medir antes/depois (nº de queries) e registrar no PR.

**✅ DoD**
- [ ] Endpoints de lista sem N+1.
- [ ] Contagem de queries documentada no PR.

**💾 Commit** `perf(query): elimina N+1 com select/prefetch_related`

## Sessão 6.3 — Celery resiliente (retry, idempotência, time limits)

1. Tasks de `campanhas`/`roteiros` com `autoretry_for`, `retry_backoff`, `max_retries`.
2. Idempotência nas syncs Meta (não duplicar métricas ao reprocessar).
3. Confirmar `CELERY_TASK_TIME_LIMIT` e adicionar `soft_time_limit`.

**✅ DoD**
- [ ] Task que falha por rede tenta de novo com backoff.
- [ ] Reexecutar uma sync não duplica registros.

**💾 Commit** `feat(tasks): retry com backoff e idempotência nas syncs`

---

# MARCO 7 — Segurança & Multi-tenant

**Nível alvo:** Sábio.

## Sessão 7.1 — Auditoria de isolamento do portal (corrige L10)

**O teste mais importante de segurança do produto:** provar que o prestador A **nunca** vê dados do prestador B.

1. Escrever testes que autenticam como `prestador` vinculado a A e tentam acessar campanhas/roteiros/perfil de B → esperar 403/404.
2. Revisar todos os `get_queryset` do portal: devem filtrar por `VinculoPrestador` ativo, nunca por `query_params` confiáveis do cliente.
3. Revisar `assessoria` (subordinado) — visão configurável, não total.

**✅ DoD**
- [ ] Suite de testes de isolamento multi-tenant verde.
- [ ] Nenhum endpoint de portal aceita `prestador_id` arbitrário do cliente.

**💾 Commit** `security(portal): testes de isolamento por VinculoPrestador`

## Sessão 7.2 — Segredos, headers e ADRs

1. Verificar que nenhuma API key aparece em logs/respostas (regra `SKILL`).
2. Adicionar (opcional) Sentry com scrubbing de PII.
3. Iniciar 📁 `docs/adr/` (Architecture Decision Records): registrar decisões já tomadas (split de settings, services em pacote, exceptions de domínio). **Um ADR curto por decisão estrutural.**

**✅ DoD**
- [ ] Nenhum secret em log.
- [ ] Pelo menos 3 ADRs escritos.

**💾 Commit** `docs(adr): registra decisões de arquitetura; security: scrub de PII`

---

# MARCO 8 — Frontend Next.js (contrato)

**Nível alvo:** Sábio (fase futura — só após backend sólido, conforme `CURSOR_CONTEXT`).
**Escopo aqui:** não construir o produto inteiro, e sim estabelecer a **fundação e o contrato** com o backend, no padrão do `SKILL_MARRYME` (estrutura `app/`, `lib/api`, `types/` espelhando serializers, Sonner, estados loading/erro/vazio, design tokens).

## Sessão 8.1 — Scaffold + cliente API centralizado

1. Criar `frontend/` Next.js App Router + TypeScript + Tailwind, com a estrutura do `SKILL_MARRYME` (seção Frontend).
2. `lib/api/client.ts`: fetch central com base URL via `NEXT_PUBLIC_API_URL`, header `Authorization: Bearer`, refresh JWT.
3. Tokens de design (cores, tipografia Cormorant Garamond + Plus Jakarta Sans) em `styles/`.

**✅ DoD**
- [ ] Build do Next passa.
- [ ] Nenhuma API key no client.
- [ ] Tokens de design centralizados (sem hex hardcoded espalhado).

## Sessão 8.2 — Login equipe + shell do dashboard

Fluxo 1 do `SKILL` (login equipe) ponta a ponta contra o backend real, com Sonner para feedback e estados de erro.

## Sessão 8.3 — `types/` espelhando serializers + dashboard de prestadores

Gerar tipos a partir do schema OpenAPI (Marco 4) para manter front e back em contrato. Dashboard de CS com loading/erro/vazio/filtro-sem-resultado obrigatórios.

**💾 Commits** `feat(frontend): scaffold + cliente API` · `feat(frontend): login equipe` · `feat(frontend): tipos OpenAPI + dashboard CS`

---

## 4. Checklist Mestre de Progresso (níveis)

```text
[ ] PRATICANTE   — Marco 0 e 1 completos (qa, logging, settings, hardening)
[ ] PROFISSIONAL — Marco 2, 3, 4 completos (testes >=80%, arquitetura, OpenAPI)
[ ] ESPECIALISTA — Marco 5, 6 completos (CI/CD, performance, Celery resiliente)
[ ] SÁBIO        — Marco 7 completo (segurança/multi-tenant, ADRs)
[ ] SÁBIO+FRONT  — Marco 8 em andamento (contrato front<->back)
```

## 5. Regras de ouro para toda sessão (resumo executável)

1. **Diagnostique antes de mexer** (Modus Operandi do `CURSOR_CONTEXT`).
2. **PR pequeno, 1 assunto, commit no padrão Conventional Commits.**
3. **Teste acompanha a mudança** — nada de "testo depois".
4. **Sem secret no código, sem stack trace na resposta, sem API key no front.**
5. **Não refatore amplo sem ganho operacional claro.**
6. **CS primeiro.** Prospecção/Apify fora de foco.
7. **Rode `make lint && make test` antes de abrir o PR.**
8. **Atualize `CURSOR_CONTEXT_MARRYME.md` se mudar arquitetura, endpoint ou prioridade.**

> Próximos arquivos: padrões concretos em `01-PADROES-CODIGO.md`, condução das sessões com IA em `02-OPERACAO-IA.md`, e a bibliografia que fundamenta cada escolha em `03-REFERENCIAS.md`.
