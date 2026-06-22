# Padrões de Código — MarryMe Backend

> Este documento define **como** o código é organizado e escrito na MarryMe. Ele é o "como"; o `00-PLANO-EXECUCAO.md` é o "quando". Tudo aqui deriva do padrão já estabelecido no `CURSOR_CONTEXT_MARRYME.md` (`View → Service → Integration → Model → Task`) e do app `contas`, que é o nosso modelo de referência interno.
>
> Regra mãe: **consistência > preferência pessoal.** Se um padrão local já existe, siga-o. Mudança de padrão só via ADR (`docs/adr/`).

---

## 1. Anatomia de um app de domínio

Todo app de domínio deve, ao amadurecer, ter esta forma (o `contas` já está perto disso; os demais convergem nos Marcos 2–3):

```text
apps/<dominio>/
├── __init__.py
├── apps.py
├── admin.py
├── models.py            # só modelos + Meta + __str__ + propriedades simples
├── serializers.py       # contrato de entrada/saída da API
├── selectors.py         # LEITURA: funções que retornam querysets/objetos
├── services/            # ESCRITA/regra de negócio: 1 arquivo por caso de uso
│   ├── __init__.py
│   └── <caso_de_uso>_service.py
├── views/               # views finas (pacote quando há muitas; arquivo se poucas)
│   ├── __init__.py
│   └── <recurso>.py
├── tasks.py             # Celery (trabalho assíncrono)
├── urls.py              # roteamento do app
├── permissions.py       # permissões específicas do app (se houver)
├── constants.py         # choices, enums, limites (evitar números mágicos)
├── factories.py         # factory_boy para testes
└── tests/               # 1 arquivo por camada testada
    ├── test_views.py
    ├── test_services.py
    └── test_selectors.py
```

**Onde cada coisa mora (a regra de ouro do "View → Service → Integration → Model → Task"):**

| Camada | Responsabilidade | NÃO faz |
|--------|------------------|---------|
| **View** | Receber request, validar input (serializer), chamar service/selector, devolver response. **Fina.** | Regra de negócio, query complexa, chamada a API externa. |
| **Serializer** | Contrato de dados (entrada e saída), validação de formato. | Regra de negócio pesada, efeitos colaterais. |
| **Selector** | Leitura: montar querysets otimizados (`select_related`/`prefetch_related`). | Escrita, mutação de estado. |
| **Service** | Escrita: orquestra regra de negócio, transações, levanta exceptions de domínio. | Conhecer detalhes de HTTP (request/response). |
| **Integration** | Falar com APIs externas (Meta Ads, Claude, Apify). Isolar o "mundo lá fora". | Regra de negócio do produto. |
| **Model** | Estrutura de dados, invariantes (constraints), validação de domínio (`clean`). | Lógica de aplicação, chamadas externas. |
| **Task** | Executar trabalho demorado/assíncrono chamando services. | Conter regra de negócio que deveria estar no service. |

> **Teste mental:** se você precisa importar `rest_framework` dentro de um service, provavelmente colocou lógica de HTTP no lugar errado. Se importa `requests`/SDK externo fora de `integrations/`, isolou mal.

---

## 2. Padrão de imports

Ordenado automaticamente pelo **ruff (regra `I`)**, mas o padrão mental é:

```python
# 1) Biblioteca padrão
import logging
from datetime import timedelta

# 2) Terceiros
from django.db import models
from rest_framework import viewsets

# 3) First-party (apps, core, config, integrations)
from core.permissions import IsCS
from integrations.meta_ads import MetaAdsClient

# 4) Local (mesmo app) — imports relativos
from .models import Prestador
from .selectors import prestadores_do_responsavel
```

**Regras**

- **First-party = imports absolutos** (`from apps.campanhas.services...`), declarados como `known-first-party` no `pyproject.toml`.
- **Mesmo app = import relativo** (`from .models import ...`) — é o que o código já faz e mantém o app portátil.
- **Nunca** `from x import *` em código de aplicação (exceção: `settings/__init__.py` e `dev/prod.py`, onde `import *` é idiomático e marcado com `# noqa`).
- **Sem import circular:** se `services` precisa de `selectors` e vice-versa, o desenho está errado — selector não chama service.
- Um logger por módulo, no topo: `logger = logging.getLogger('marryme.<dominio>')`.

---

## 3. Models

Padrão observado em `prestadores/models.py` (UUID PK, `choices`, `Meta` com `ordering`/`verbose_name`, `__str__`). Elevar para nível sábio:

```python
class Prestador(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ... campos ...
    fase = models.CharField(max_length=20, choices=FASES, default='onboarding')

    class Meta:
        ordering = ['-atualizado_em']
        verbose_name = 'Prestador'
        verbose_name_plural = 'Prestadores'
        indexes = [                                   # Marco 6
            models.Index(fields=['fase']),
            models.Index(fields=['categoria']),
            models.Index(fields=['responsavel']),
        ]
        constraints = [                               # Marco 6
            models.CheckConstraint(
                check=models.Q(ticket_medio_estimado__gte=0),
                name='ticket_medio_nao_negativo',
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nome_artistico} ({self.categoria})"

    def clean(self):
        # validação de domínio (estado com 2 letras, etc.)
        ...
```

**Regras**

- `choices` e enums vivem em `constants.py`, não inline, quando reaproveitados.
- Todo campo monetário: `DecimalField` (nunca `Float`) — já é o padrão do projeto.
- `JSONField` (`dados_entrevista`, `analise_estrategica`) com `default=dict` — manter; nunca `default={}` (mutável compartilhado).
- Toda relação tem `related_name` explícito e `on_delete` consciente (já feito em `responsavel`).
- Datas: `criado_em = auto_now_add`, `atualizado_em = auto_now`. Padronizar nomes em pt-BR em todos os models.

---

## 4. Serializers — o contrato

- Um serializer de **lista** (resumido) e um de **detalhe** (completo) quando a tela pede — o `roteiros` já faz isso (`ChatSessaoListSerializer` vs `ChatSessaoSerializer`). Replicar onde a lista for pesada.
- Serializer é **contrato**: o frontend (Marco 8) gera tipos TS a partir dele (via OpenAPI). Mudou serializer → mudou contrato → comunicar.
- Validação de formato no serializer (`validate_<campo>`). Validação de **regra de negócio** no service.
- Campos sensíveis (prompts internos, tokens, logs) **nunca** entram em serializer de portal (regra `SKILL`).

---

## 5. Views finas

Padrão a seguir (o `roteiros/views.py` é um bom exemplo de ViewSet com `@action`):

```python
class PrestadorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCS]
    serializer_class = PrestadorSerializer

    def get_queryset(self):
        # delega a leitura ao selector (Marco 3.3)
        return prestadores_visiveis_para(self.request.user)

    @action(detail=True, methods=['post'], url_path='atualizar-fase')
    def atualizar_fase(self, request, pk=None):
        prestador = self.get_object()
        nova_fase = request.data.get('fase')
        PrestadorService().mudar_fase(prestador, nova_fase)   # regra no service
        return Response(PrestadorSerializer(prestador).data)
```

**Regras**

- View não decide regra de negócio. Ela orquestra: valida → chama service/selector → serializa.
- `get_queryset` nunca confia em `query_params` para autorização — filtra por `request.user` / `VinculoPrestador` (segurança, Marco 7).
- Mensagens de erro de input via serializer; erros de negócio via exception de domínio (o handler central traduz).

---

## 6. Services e Selectors (separação leitura/escrita)

Padrão inspirado no **HackSoft Django Styleguide** (ver `03-REFERENCIAS.md`), adaptado ao que o `contas` já pratica.

**Service (escrita):**

```python
# apps/prestadores/services/fase_service.py
import logging
from django.db import transaction
from core.exceptions_domain import DomainError
from ..models import Prestador

logger = logging.getLogger('marryme.prestadores')

class PrestadorService:
    @transaction.atomic
    def mudar_fase(self, prestador: Prestador, nova_fase: str) -> Prestador:
        if nova_fase not in dict(Prestador.FASES):
            raise DomainError('Fase inválida.')
        prestador.fase = nova_fase
        prestador.save(update_fields=['fase', 'atualizado_em'])
        logger.info("Fase alterada: %s -> %s", prestador.id, nova_fase)
        return prestador
```

**Selector (leitura):**

```python
# apps/prestadores/selectors.py
from .models import Prestador

def prestadores_visiveis_para(user):
    qs = Prestador.objects.select_related('responsavel')
    if user.role == 'admin':
        return qs
    return qs.filter(responsavel=user)
```

**Regras**

- Escrita relevante dentro de `@transaction.atomic`.
- `save(update_fields=[...])` quando só alguns campos mudam (o projeto já usa isso em `roteiros`).
- Logs com `%s` (lazy), não f-string, em chamadas de logging.
- Selector sempre otimiza relação que a view/serializer vai acessar (anti-N+1, Marco 6.2).

---

## 7. Integrations

`integrations/` isola SDKs e HTTP externo (`meta_ads.py`, `claude_ai.py`, `apify_client.py`). Mantê-los assim:

- Recebem config por parâmetro/env, não leem `request`.
- Lançam erro técnico claro; o service traduz para exception de domínio quando faz sentido para o usuário.
- Sem retry "escondido" — resiliência (retry/backoff) é decidida na **task** (Marco 6.3).
- Apify existe, mas **não é foco** (regra do `CURSOR_CONTEXT`): não expandir.

---

## 8. Tasks (Celery)

```python
@shared_task(bind=True, autoretry_for=(RequestException,),
             retry_backoff=True, max_retries=5, soft_time_limit=300)
def sync_meta_prestador(self, prestador_id):
    CampanhaService().sincronizar(prestador_id)   # idempotente
```

**Regras**

- Task chama service; não contém regra de negócio.
- **Idempotência:** reexecutar não duplica dados (usar `update_or_create`/chaves naturais nas métricas Meta).
- `soft_time_limit` < `CELERY_TASK_TIME_LIMIT` (hoje 30 min) para liberar limpeza.
- Logar início/fim com IDs para rastreabilidade.

---

## 9. Erros e exceptions

- **Erro de formato/input** → serializer → 400 automático.
- **Erro de regra de negócio** → `DomainError` (e subclasses) → handler central traduz para status semântico + mensagem pt-BR.
- **Erro técnico inesperado** → handler loga com `exc_info=True` e retorna 500 genérico (sem stack). Já é o comportamento de `core/exceptions.py`; só falta o ramo de `DomainError` (Marco 3.1).
- Nunca `except: pass`. Nunca engolir exceção sem logar.

---

## 10. Testes (padrão)

- **pytest** (não `unittest.TestCase`, exceto o legado de `contas` que migra).
- Estrutura: `tests/test_<camada>.py`.
- Dados via **factory_boy** (`factories.py`), não criação manual repetida.
- Integrações externas **sempre mockadas** (zero rede no teste).
- Todo endpoint tem: caso feliz + caso de permissão negada (403) + caso de input inválido (400).
- Nome de teste descreve o comportamento: `test_prestador_nao_acessa_dados_de_outro_prestador`.

```python
def test_cs_lista_prestadores(api_cs, prestador_factory):
    prestador_factory.create_batch(3)
    resp = api_cs.get('/api/v1/prestadores/')
    assert resp.status_code == 200
    assert resp.data['total'] == 3        # formato MarryMePagination
```

---

## 11. Nomenclatura e idioma

- **Domínio em pt-BR** (já é o padrão: `prestador`, `roteiro`, `campanha`, `fase`, `vinculo`). Manter.
- **Termos técnicos universais em inglês** quando idiomáticos (`serializer`, `viewset`, `queryset`, `task`).
- Classes `PascalCase`, funções/variáveis `snake_case`, constantes `UPPER_SNAKE`.
- Sufixos consistentes: `*Service`, `*Serializer`, `*ViewSet`, `*Factory`, `*Client` (integrations).
- URLs em pt-BR e kebab-case (`atualizar-fase`, `roteiros-finais`) — já é o padrão.

---

## 12. Git e PRs

- **Conventional Commits:** `tipo(escopo): descrição` (`feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `perf`, `ci`, `security`).
- 1 PR = 1 sessão = 1 assunto. Diff pequeno e revisável.
- Antes do PR: `make lint && make test` verdes.
- PR descreve: o que muda, por quê, como testar, e qual lacuna (L1–L11) fecha.

---

## 13. Checklist rápido de revisão (cole no template de PR)

```text
[ ] View fina? (sem regra de negócio)
[ ] Regra de negócio no service? Leitura no selector?
[ ] Integração externa isolada em integrations/?
[ ] Sem secret/API key no código ou na resposta?
[ ] Sem stack trace vazando (DEBUG=False)?
[ ] Portal filtrado por VinculoPrestador (se aplicável)?
[ ] Testes: caso feliz + 403 + 400?
[ ] make lint && make test verdes?
[ ] Conventional Commit + PR pequeno?
[ ] CURSOR_CONTEXT atualizado se mudou arquitetura/endpoint?
```
