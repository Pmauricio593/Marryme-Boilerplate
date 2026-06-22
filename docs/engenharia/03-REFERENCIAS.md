# Referências Bibliográficas — fundamentos de cada decisão

> Cada decisão do `00-PLANO-EXECUCAO.md` e do `01-PADROES-CODIGO.md` se apoia em fontes reconhecidas. Esta é a bibliografia de engenharia da MarryMe. Use-a para aprofundar quando uma sessão tocar um tema novo. Organizada por área; ao final, um mapa "lacuna → leitura".

---

## 1. Fundamentos de arquitetura e ofício

- **Martin, Robert C. — _Clean Code: A Handbook of Agile Software Craftsmanship_** (Prentice Hall, 2008). Nomes, funções pequenas, "deixe o código mais limpo do que encontrou". Base do "código óbvio" do nível sábio.
- **Martin, Robert C. — _Clean Architecture_** (Prentice Hall, 2017). Separação de camadas e dependências apontando para dentro. Fundamenta `View → Service → Integration → Model`.
- **Hunt, A.; Thomas, D. — _The Pragmatic Programmer_** (20th Anniversary Ed., Addison-Wesley, 2019). DRY, ortogonalidade, "não programe por coincidência". Base das regras de ouro.
- **Fowler, Martin — _Refactoring_** (2nd Ed., Addison-Wesley, 2018). Refatoração segura em passos pequenos. Fundamenta "refatorar só com testes e ganho claro".
- **Percival, H.; Gregory, B. — _Architecture Patterns with Python_** (O'Reilly, 2020). Services, repositórios, unidade de trabalho em Python. Base da camada de services/selectors.

## 2. Django e Django REST Framework (oficial e comunidade)

- **Django — Documentação oficial.** https://docs.djangoproject.com/ — settings, `LOGGING`, security, `check --deploy`, migrations, índices/constraints.
  - Logging: https://docs.djangoproject.com/en/stable/topics/logging/ (fundamenta Marco 1.1)
  - Deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/ (fundamenta Marco 1.3)
  - Database optimization: https://docs.djangoproject.com/en/stable/topics/db/optimization/ (fundamenta Marco 6.2)
- **Django REST Framework — Documentação oficial.** https://www.django-rest-framework.org/ — viewsets, serializers, permissions, throttling, pagination, versioning (Marcos 3, 4).
- **HackSoft — _Django Styleguide_.** https://github.com/HackSoftware/Django-Styleguide — **a referência central** da separação services (escrita) vs selectors (leitura) e views finas. Fundamenta o `01-PADROES` e o Marco 3.
- **Two Scoops of Django (Greenfeld & Roy)** — convenções de settings por ambiente, requirements em camadas, organização de apps. Fundamenta Marcos 0.1 e 1.2.
- **drf-spectacular — Documentação.** https://drf-spectacular.readthedocs.io/ — geração de OpenAPI 3 (Marco 4.1).
- **SimpleJWT — Documentação.** https://django-rest-framework-simplejwt.readthedocs.io/ — ciclo de access/refresh, rotação (já em uso; base do Marco 8.1).

## 3. Qualidade, estilo e ferramentas

- **PEP 8 — Style Guide for Python Code.** https://peps.python.org/pep-0008/ — base de todo o estilo; aplicado automaticamente por ruff/black.
- **PEP 20 — The Zen of Python.** https://peps.python.org/pep-0020/ — "explícito melhor que implícito", "simples melhor que complexo".
- **PEP 257 — Docstring Conventions.** https://peps.python.org/pep-0257/ — docstrings dos services/classes.
- **Ruff — Documentação.** https://docs.astral.sh/ruff/ — lint + import sort + format (Marco 0.1).
- **Black — Documentação.** https://black.readthedocs.io/ — formatação determinística.
- **pre-commit — Documentação.** https://pre-commit.com/ — hooks que barram problema antes do commit.

## 4. Testes

- **pytest + pytest-django — Documentação.** https://pytest-django.readthedocs.io/ — fixtures, `--reuse-db`, marcadores (Marco 2).
- **factory_boy — Documentação.** https://factoryboy.readthedocs.io/ — dados de teste declarativos.
- **Khorikov, Vladimir — _Unit Testing Principles, Practices, and Patterns_** (Manning, 2020). O que é um bom teste, mocks vs stubs, evitar testes frágeis. Fundamenta a regra "não afrouxar asserção".
- **Beck, Kent — _Test-Driven Development: By Example_** (Addison-Wesley, 2002). Ciclo red-green-refactor; "teste acompanha a mudança".

## 5. CI/CD, operação e doze fatores

- **Wiggins, Adam — _The Twelve-Factor App_.** https://12factor.net/ — config por env, logs como stream para stdout, processos stateless, backing services. **Já citado implicitamente no `SKILL`**; fundamenta Marcos 1 e 6.3.
- **GitHub Actions — Documentação.** https://docs.github.com/actions — pipelines de CI (Marco 5).
- **Conventional Commits 1.0.0.** https://www.conventionalcommits.org/ — padrão das mensagens de commit.
- **Semantic Versioning 2.0.0.** https://semver.org/ — versionamento de API/releases.
- **Nygard, Michael — _Release It!_** (2nd Ed., Pragmatic Bookshelf, 2018). Padrões de estabilidade: timeouts, retry, circuit breaker, idempotência. Fundamenta Celery resiliente (Marco 6.3).
- **Nygard, Michael — "Documenting Architecture Decisions" (ADR).** https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions — formato de ADR (Marco 7.2).

## 6. Celery / assíncrono

- **Celery — Documentação oficial.** https://docs.celeryq.dev/ — `autoretry_for`, `retry_backoff`, time limits, beat (Marco 6.3).
- **django-celery-beat / django-celery-results — Docs.** agendamento no banco e persistência de resultados (já em uso).

## 7. Segurança e privacidade

- **OWASP — _Top Ten_.** https://owasp.org/www-project-top-ten/ — controle de acesso quebrado (multi-tenant), exposição de dados sensíveis (Marco 7).
- **OWASP — _API Security Top 10_.** https://owasp.org/www-project-api-security/ — autorização em nível de objeto (BOLA) — exatamente o risco do portal por `VinculoPrestador`.
- **OWASP — _Cheat Sheet Series_.** https://cheatsheetseries.owasp.org/ — logging seguro, secrets, headers.
- **LGPD — Lei nº 13.709/2018.** base legal brasileira para tratamento de dados pessoais de prestadores e leads (scrubbing de PII, Marco 7.2).

## 8. Frontend (fase futura — Marco 8)

- **Next.js — Documentação (App Router).** https://nextjs.org/docs — server/client components, rotas.
- **TypeScript — Handbook.** https://www.typescriptlang.org/docs/ — tipos espelhando serializers.
- **Tailwind CSS — Docs.** https://tailwindcss.com/docs — utilitários, design tokens.
- **React Hook Form** (https://react-hook-form.com/) + **Zod** (https://zod.dev/) — formulários e validação (citados no `SKILL`).
- **Sonner** — https://sonner.emilkowal.ski/ — toasts (regra `SKILL`: nunca `alert()`).
- **WCAG 2.2** — https://www.w3.org/WAI/standards-guidelines/wcag/ — acessibilidade; `prefers-reduced-motion` (citado no `SKILL`).

---

## 9. Mapa lacuna → leitura

| Lacuna | Marco | Leitura primária |
|--------|-------|------------------|
| L1 Sem LOGGING | 1.1 | Django Logging docs; 12-Factor (logs) |
| L3 Sem lint/format | 0.1 | PEP 8; Ruff docs; Black docs; pre-commit |
| L4 Settings monolítico | 1.2 | Two Scoops of Django; 12-Factor (config) |
| L4 Hardening | 1.3 | Django deployment checklist; OWASP Top Ten |
| L2 Sem testes | 2.x | pytest-django; Khorikov; Beck (TDD) |
| L6 Services inconsistentes | 3.2 | HackSoft Styleguide; Architecture Patterns with Python |
| L11 Sem exceptions de domínio | 3.1 | Clean Architecture; Release It! |
| L7 Sem doc de API | 4.1 | drf-spectacular; DRF docs |
| L8 Sem CI/CD | 5.x | GitHub Actions docs; Conventional Commits |
| L9 Índices/N+1 | 6.x | Django DB optimization; Release It! |
| L10 Multi-tenant | 7.1 | OWASP API Security (BOLA); LGPD |

---

## 10. Ordem de leitura sugerida (trilha do sábio)

1. _The Pragmatic Programmer_ (mentalidade)
2. PEP 8 + PEP 20 (estilo e princípios)
3. HackSoft Django Styleguide (arquitetura que adotamos)
4. _Clean Code_ + _Refactoring_ (ofício)
5. pytest-django + Khorikov (testes que valem)
6. _The Twelve-Factor App_ + _Release It!_ (operação e resiliência)
7. OWASP API Security + LGPD (segurança do produto)
