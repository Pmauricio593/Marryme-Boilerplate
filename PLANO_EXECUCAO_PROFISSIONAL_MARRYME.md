# Plano de Execucao Profissional — MarryMe

Baseado em:

- `CURSOR_CONTEXT_MARRYME.md`
- `SKILL_MARRYME.md`
- Backend Django existente em `backend/`
- Diretrizes Twelve-Factor App
- Estado real do repositorio em Jun/2026

Este plano organiza a evolucao do produto MarryMe para um nivel profissional, com ordem de implementacao, padroes de codigo, padroes visuais, governanca de imports, prevencao de bugs e criterios objetivos de validacao.

---

## 1. Diagnostico tecnico atual

### 1.1 Estado real do repositorio

O repositorio atual e um boilerplate com backend funcional e frontend ainda nao implementado como aplicacao Next.js.

```text
Marryme-Boilerplate/
├── backend/                     # Django + DRF + Celery + Docker
├── frontend/                    # Stubs de assets; app Next.js ainda nao criado
├── CURSOR_CONTEXT_MARRYME.md    # Fonte de verdade produto/operacao
├── SKILL_MARRYME.md             # Guia tecnico/design
└── .gitignore
```

Stack real confirmada:

- Backend: Django 6, Django REST Framework, SimpleJWT, PostgreSQL, Redis, Celery, django-celery-beat, django-celery-results.
- Deploy: Railway com Docker.
- Integracoes: Meta Ads API, Anthropic Claude API, Apify client instalado mas fora de prioridade.
- Frontend de produto: ainda nao criado.
- Supabase/Next.js App Router: citados como visao/contexto historico, mas nao presentes neste repositorio.

### 1.2 Forcas atuais

- Separacao backend ja segue o fluxo:

```text
View/API -> Service -> Integration -> Model -> Task
```

- Apps principais ja existem:
  - `apps.prestadores`
  - `apps.campanhas`
  - `apps.roteiros`
  - `apps.contas`
- Auth JWT com roles.
- Portal por API com convites e vinculos.
- Celery para processamento assincrono.
- Docker Compose com web, worker, beat, PostgreSQL e Redis.
- `.env.example` existe e reforca configuracao por variaveis de ambiente.

### 1.3 Riscos e lacunas principais

1. Frontend profissional ainda nao existe.
2. Testes automatizados ainda sao minimos fora de `apps.contas`.
3. Nao ha contrato OpenAPI formal.
4. Nao ha CI/CD versionado no repositorio.
5. Formula e nomenclatura do Health Score precisam ser reconciliadas entre regra de negocio, documentacao, backend e futura interface.
6. Documentacao cita endpoint antigo de primeiro acesso do portal, mas o codigo atual usa fluxo de convites.
7. Celery Beat depende de configuracao em banco/admin para agenda periodica.
8. Assets atuais em `frontend/` nao representam ainda o sistema interno em Next.js.

---

## 2. Principios obrigatorios de execucao

### 2.1 Twelve-Factor App aplicado ao projeto

1. **Codebase:** manter monorepo unico para backend, frontend e documentacao tecnica essencial.
2. **Dependencies:** declarar dependencias em manifestos (`requirements/base.txt`, futuro `package.json`).
3. **Config:** usar somente env vars para secrets, URLs, tokens e chaves externas.
4. **Backing services:** Postgres, Redis, Meta Ads, Claude e futuros servicos devem ser trocaveis por configuracao.
5. **Build/Release/Run:** separar build Docker/Next, release com env vars e execucao.
6. **Processes:** web, worker, beat e frontend devem ser stateless.
7. **Port binding:** `PORT` por env var em backend e frontend.
8. **Concurrency:** escalar horizontalmente web/worker sem estado compartilhado em memoria.
9. **Disposability:** processos devem iniciar rapido e finalizar com seguranca.
10. **Dev/prod parity:** Docker Compose local deve espelhar o maximo possivel producao.
11. **Logs:** logs em stdout; nao criar arquivos locais de log em runtime.
12. **Admin processes:** migrations, seeds e rotinas administrativas como comandos one-off.

### 2.2 Principio de produto

Toda funcao precisa responder a uma pergunta operacional:

- Ajuda CS a entender risco, prioridade ou proximo passo?
- Ajuda a gerar, aprovar ou reutilizar material de marketing?
- Ajuda o prestador a entender valor sem expor detalhe interno?
- Reduz trabalho manual da equipe pequena?

Se a resposta for nao, a funcao deve esperar.

### 2.3 Ordem de prioridade da MarryMe

1. CS: prestadores, pipeline, campanhas, Health Score e pautas de reuniao.
2. Conteudo: roteiros, historico, geracao IA e few-shot.
3. Portal: clareza para o cliente.
4. Vendas/onboarding: entrada organizada de novos clientes.
5. Prospeccao: somente depois da base operacional madura.

---

## 3. Arquitetura-alvo do repositorio

### 3.1 Backend Django

Manter o padrao atual:

```text
backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── authentication.py
│   ├── permissions.py
│   ├── pagination.py
│   └── exceptions.py
├── apps/
│   ├── contas/
│   ├── prestadores/
│   ├── campanhas/
│   └── roteiros/
└── integrations/
    ├── meta_ads.py
    ├── claude_ai.py
    └── apify_client.py
```

Regra de responsabilidade:

- `views.py`: recebe request, valida acao HTTP, chama service, retorna serializer.
- `serializers.py`: contrato de entrada e saida.
- `services.py`: regra de negocio.
- `tasks.py`: processo assincrono.
- `integrations/`: cliente externo sem regra de dominio.
- `models.py`: persistencia e invariantes simples de dados.
- `permissions.py`: matriz de acesso.

### 3.2 Frontend Next.js a ser criado

Estrutura recomendada:

```text
frontend/
├── app/
│   ├── (auth)/
│   │   └── login/
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── prestadores/
│   │   ├── campanhas/
│   │   └── roteiros/
│   └── portal/
│       ├── login/
│       ├── convite/
│       └── dashboard/
├── components/
│   ├── ui/
│   ├── layout/
│   └── domain/
│       ├── prestadores/
│       ├── campanhas/
│       ├── roteiros/
│       └── portal/
├── lib/
│   ├── api/
│   ├── auth/
│   ├── constants/
│   ├── formatters/
│   └── utils/
├── types/
├── styles/
└── middleware.ts
```

Regra central:

- Paginas podem orquestrar dados.
- Componentes de dominio nao fazem `fetch` direto.
- `lib/api` concentra HTTP, refresh token, erros e base URL.
- `types/` espelha serializers do backend.
- UI base fica em `components/ui`.
- Componentes operacionais ficam em `components/domain`.

---

## 4. Padroes de imports e organizacao de codigo

### 4.1 Python/Django

Ordem de imports:

```python
# 1. Standard library
import logging
from datetime import date

# 2. Django
from django.conf import settings
from django.db import transaction

# 3. Terceiros
from rest_framework import status, viewsets
from rest_framework.response import Response

# 4. Apps internos
from apps.prestadores.models import Prestador
from integrations.meta_ads import MetaAdsClient
from .serializers import PrestadorSerializer
from .services import PrestadorService
```

Regras:

- Evitar logica de negocio em `views.py`.
- Evitar chamada externa direta em `views.py`.
- Usar `select_related` e `prefetch_related` em listagens.
- Usar `transaction.atomic()` em operacoes com multiplas escritas.
- Nao retornar excecoes internas para o cliente.
- Logs devem usar namespaces `marryme.<app>`.
- Nao hardcodar token, URL, modelo Claude ou segredo.

### 4.2 TypeScript/Next.js

Ordem de imports:

```ts
// 1. React/Next
import Link from "next/link";

// 2. Bibliotecas externas
import { toast } from "sonner";

// 3. Imports internos absolutos
import { apiClient } from "@/lib/api/client";
import { formatCurrency } from "@/lib/formatters/currency";
import type { Prestador } from "@/types/prestadores";

// 4. Componentes locais
import { HealthScoreBadge } from "./health-score-badge";
```

Regras:

- Usar alias `@/`.
- Tipos compartilhados sempre com `type`.
- Nao usar `any` sem justificativa.
- Nao usar `alert()`.
- Tratar loading, erro e vazio em toda tela.
- Separar componente visual de regra de fetch.
- Nao expor tokens privados em `NEXT_PUBLIC_*`.

### 4.3 Nomes de arquivos

Padrao:

```text
health-score-card.tsx
prestador-status-badge.tsx
campaign-metrics-table.tsx
chat-message-list.tsx
```

Evitar:

```text
Card2.tsx
NewDashboard.tsx
utils2.ts
temp.ts
```

---

## 5. Design system e estrutura visual

### 5.1 Tokens obrigatorios

Tipografia:

- Headings e numeros de destaque: Cormorant Garamond.
- Corpo, botoes, labels e dashboard: Plus Jakarta Sans.
- Nao usar Inter, Geist ou Poppins sem decisao explicita.

Cores base:

```text
primary: #1A0A2E
primary-mid: #2D1654
secondary: #C084FC
accent: #E879F9
accent-warm: #F472B6
gold: #D4AF37
text-dark: #1A1A2E
text-mid: #4A4A6A
text-muted: #8A8AA8
bg-light: #F8F5FF
bg-white: #FFFFFF
bg-dark: #0F0720
border: #E8E0F0
```

Health Score:

```text
saudavel: #10B981
atencao: #F59E0B
em_risco: #EF4444
excelente/destaque: #6366F1
```

Categorias:

```text
musico: #C084FC
fotografo: #F472B6
celebrante: #34D399
dj: #60A5FA
cerimonialista: #FBBF24
```

### 5.2 Componentes-base

Primeiro lote:

- `Button`
- `Input`
- `Textarea`
- `Select`
- `Badge`
- `Card`
- `Skeleton`
- `EmptyState`
- `ErrorState`
- `PageHeader`
- `Tabs`
- `Table`
- `Dialog`
- `DropdownMenu`
- `ToastProvider`

Regras:

- Componentes de UI nao conhecem dominio MarryMe.
- Componentes de dominio usam componentes de UI.
- Variantes devem ser explicitas.
- Estados de erro precisam de mensagem acionavel.
- Estados vazios precisam orientar o proximo passo.

### 5.3 Layout operacional

Dashboard interno:

```text
Sidebar fixa
├── Prestadores
├── Campanhas
├── Roteiros
├── Relatorios
└── Configuracoes

Topbar
├── Busca
├── Atalhos
└── Usuario

Conteudo
├── Header da pagina
├── Cards de resumo
├── Filtros
└── Lista/tabela principal
```

Detalhe do prestador:

```text
Header
├── Nome artistico
├── Categoria
├── Fase
├── Responsavel
└── Acoes rapidas

Coluna principal
├── Health Score
├── Campanhas
├── Roteiros
└── Historico operacional

Coluna lateral
├── Dados comerciais
├── Contatos
├── Metas
└── Alertas
```

Chat de roteiros:

```text
Split-screen
├── Esquerda: historico e mensagens
└── Direita: roteiro final em construcao
```

Portal do cliente:

```text
Visao simples
├── Saudacao e proximo passo
├── Resumo de campanhas
├── Health Score traduzido
├── Roteiros aprovados
└── Contato/CS responsavel
```

---

## 6. Plano de execucao por ciclos

Cada ciclo deve terminar com:

- Codigo pequeno e revisavel.
- Teste ou checklist objetivo.
- Validacao de permissao e dados sensiveis.
- Atualizacao de documentacao apenas quando contrato, arquitetura ou endpoint mudar.

### Ciclo 0 — Congelamento do estado real e contratos criticos

Objetivo:

Criar uma base confiavel antes de construir frontend e novas telas.

Passos:

1. Revisar endpoints reais em `config/urls.py` e `apps/*/urls.py`.
2. Corrigir referencias documentais ao fluxo antigo de primeiro acesso.
3. Formalizar o fluxo atual do portal:
   - validar convite;
   - aceitar convite;
   - login portal;
   - resolver vinculo ativo;
   - filtrar dados por prestador.
4. Reconciliar a formula oficial do Health Score.
5. Definir nomes finais dos campos exibidos no frontend.
6. Listar serializers que serao espelhados em TypeScript.

Criterios de aceite:

- Nao ha endpoint documentado que nao exista no codigo.
- Health Score possui regra unica aprovada.
- Matriz role x endpoint esta clara.
- Nenhum segredo aparece em documento ou frontend.

Prevencao de bugs:

- Nao iniciar dashboard antes de fechar contrato de serializers.
- Nao exibir Health Score sem breakdown alinhado ao backend.
- Nao permitir que usuario portal consulte prestador por ID arbitrario.

### Ciclo 1 — Qualidade minima profissional do backend

Objetivo:

Transformar o backend funcional em base segura para frontend e operacao.

Passos:

1. Adicionar testes para `apps.prestadores`:
   - listagem com filtros;
   - criacao por CS;
   - atualizacao de fase;
   - bloqueio de delete para nao admin.
2. Adicionar testes para `apps.campanhas`:
   - calculo do Health Score;
   - status `saudavel`, `atencao`, `em_risco`;
   - prestador sem `meta_ad_account_id`;
   - task enfileirada.
3. Adicionar testes para `apps.roteiros`:
   - criar sessao;
   - enviar mensagem;
   - finalizar sessao;
   - aprovar roteiro para few-shot.
4. Ampliar testes de portal:
   - convite expirado;
   - vinculo titular;
   - vinculo assessoria;
   - tentativa de acesso a outro prestador.
5. Padronizar erros de API:
   - `{ "erro": "mensagem" }`;
   - detalhes de validacao em formato previsivel.
6. Revisar queries de listagem com `select_related` e `prefetch_related`.

Criterios de aceite:

- `python manage.py test` passa localmente.
- Fluxos de permissao sensiveis possuem testes.
- Nao ha view nova com regra de negocio pesada.
- Logs continuam em stdout.

Prevencao de bugs:

- Testar permissao por role antes de construir tela.
- Usar factories/fixtures pequenas e legiveis.
- Evitar mock excessivo em regra de dominio; mockar apenas APIs externas.

### Ciclo 2 — Contrato OpenAPI e governanca de API

Objetivo:

Dar ao frontend um contrato estavel e reduzir bugs de integracao.

Passos:

1. Adicionar geracao de schema OpenAPI via biblioteca compativel com DRF.
2. Expor schema em ambiente interno.
3. Nomear tags por dominio:
   - Auth;
   - Prestadores;
   - Campanhas;
   - Roteiros;
   - Portal.
4. Revisar serializers para campos obrigatorios, readonly e formatos.
5. Definir convencao de paginacao, filtros e erros.

Criterios de aceite:

- Schema inclui endpoints reais.
- Frontend consegue gerar ou espelhar tipos a partir do contrato.
- Endpoints sensiveis nao aparecem com permissao ambigua.

Prevencao de bugs:

- Nao tratar schema como substituto de testes.
- Validar manualmente endpoints de streaming SSE, pois OpenAPI nem sempre descreve bem streaming.

### Ciclo 3 — CI/CD e padrao de verificacao

Objetivo:

Evitar regressao silenciosa.

Passos:

1. Criar workflow de CI para backend:
   - instalar dependencias;
   - rodar migrations check;
   - rodar testes;
   - validar import/lint se ferramenta for adotada.
2. Validar build Docker.
3. Definir comando padrao local:
   - `make test`;
   - futuro `npm run lint`;
   - futuro `npm run typecheck`.
4. Documentar em arquivo existente quando necessario.

Criterios de aceite:

- PR nao passa com teste quebrado.
- Build Docker falha se dependencia ou migration estiver inconsistente.
- Comandos locais e CI usam a mesma base.

Prevencao de bugs:

- Nao depender de SQLite para validar comportamento que em producao roda em Postgres.
- Manter env vars de CI explicitas e sem secrets reais.

### Ciclo 4 — Fundacao do frontend Next.js

Objetivo:

Criar a aplicacao frontend profissional sem ainda tentar construir todas as telas.

Passos:

1. Criar app Next.js dentro de `frontend/`.
2. Configurar TypeScript estrito.
3. Configurar Tailwind com tokens MarryMe.
4. Configurar alias `@/`.
5. Configurar fontes:
   - Cormorant Garamond;
   - Plus Jakarta Sans.
6. Criar estrutura:
   - `app/`;
   - `components/ui`;
   - `components/layout`;
   - `components/domain`;
   - `lib/api`;
   - `lib/auth`;
   - `types`;
   - `styles`.
7. Criar `lib/api/client.ts` com:
   - base URL por env var;
   - headers;
   - tratamento de erro;
   - refresh token planejado.
8. Criar `sonner` como padrao de feedback.
9. Criar layout base autenticado e layout auth.

Criterios de aceite:

- `npm run build` passa.
- `npm run lint` passa.
- Nao ha secrets no client.
- Todas as telas iniciais possuem loading, erro e vazio quando aplicavel.

Prevencao de bugs:

- Nao conectar tela direto ao backend sem tipo definido.
- Nao colocar access token em lugar inseguro sem decisao explicita.
- Nao misturar componentes de dominio com `fetch`.

### Ciclo 5 — Auth de equipe

Objetivo:

Permitir que equipe interna acesse o sistema com JWT.

Passos:

1. Criar tela `/login`.
2. Integrar `POST /api/v1/auth/login/`.
3. Implementar armazenamento seguro conforme estrategia escolhida.
4. Implementar refresh token com `POST /api/v1/auth/refresh/`.
5. Criar middleware ou protecao de rota.
6. Criar logout.
7. Exibir usuario e role na topbar.

Criterios de aceite:

- Usuario sem token nao acessa dashboard.
- Token expirado tenta refresh.
- Falha de login mostra toast com mensagem clara.
- Role fica disponivel para controle visual de acoes.

Prevencao de bugs:

- Nao exibir stack trace de erro de auth.
- Nao guardar service role ou API externa no frontend.
- Nao depender apenas de bloqueio visual; backend segue como autoridade.

### Ciclo 6 — Dashboard de prestadores para CS

Objetivo:

Entregar a primeira tela operacional de alto impacto.

Passos:

1. Criar rota `/prestadores`.
2. Integrar `GET /api/v1/prestadores/`.
3. Criar filtros:
   - fase;
   - categoria;
   - busca;
   - responsavel quando suportado.
4. Criar cards de resumo:
   - total ativo;
   - em risco;
   - em atencao;
   - onboarding;
   - sem sync recente.
5. Criar tabela/lista com:
   - nome artistico;
   - categoria;
   - fase;
   - cidade/estado;
   - Health Score;
   - ultima atualizacao;
   - responsavel;
   - acoes.
6. Criar estados:
   - loading;
   - erro;
   - vazio;
   - filtro sem resultado.

Criterios de aceite:

- CS entende prioridades em menos de uma tela.
- Filtros nao quebram paginacao.
- Prestador sem Health Score aparece como pendente, nao como zero critico.
- Acoes respeitam role.

Prevencao de bugs:

- Normalizar status e fases em constantes.
- Evitar comparar string solta espalhada em componentes.
- Tratar pagina vazia separada de erro de API.

### Ciclo 7 — Detalhe do prestador

Objetivo:

Centralizar operacao de CS por cliente.

Passos:

1. Criar rota `/prestadores/[id]`.
2. Integrar detalhe do prestador.
3. Criar header operacional.
4. Criar painel de dados comerciais.
5. Criar timeline/historico inicial quando houver fonte.
6. Criar acoes:
   - atualizar fase;
   - sincronizar Meta;
   - abrir roteiros;
   - abrir campanhas.
7. Criar componentes:
   - `PrestadorHeader`;
   - `PrestadorInfoCard`;
   - `PipelineStageBadge`;
   - `HealthScoreCard`;
   - `MetaSyncButton`.

Criterios de aceite:

- Todas as informacoes importantes do cliente ficam em uma pagina.
- Atualizacao de fase usa endpoint existente.
- Sync Meta mostra status enfileirado.
- Tela trata prestador inexistente ou sem permissao.

Prevencao de bugs:

- Nao assumir que `meta_ad_account_id` existe.
- Nao disparar sync duplicado sem feedback.
- Nao deixar acao destrutiva exposta para role errada.

### Ciclo 8 — Campanhas e Health Score

Objetivo:

Transformar dados de campanha em acao de CS.

Passos:

1. Criar componentes de Health Score com breakdown.
2. Integrar endpoints:
   - metricas;
   - health scores;
   - relatorios;
   - gerar analise.
3. Mostrar:
   - score;
   - status;
   - motivo;
   - proxima acao sugerida.
4. Criar visual diferenciado para:
   - saudavel;
   - atencao;
   - em risco;
   - sem dados.
5. Criar area de pauta de reuniao.

Criterios de aceite:

- Score nunca aparece sem contexto.
- Status gera recomendacao operacional.
- Relatorio IA deixa claro o que foi dado real e o que e analise.
- Frontend nao inventa metrica faltante.

Prevencao de bugs:

- Alinhar pesos e nomes do Health Score antes da interface.
- Tratar limitacao da Meta API para campanhas de mensagens.
- Nao comparar CPL/CTR sem checar nulos.

### Ciclo 9 — Chat de roteiros split-screen

Objetivo:

Substituir fluxo antigo por experiencia conversacional rastreavel.

Passos:

1. Criar rota `/roteiros`.
2. Criar listagem de sessoes por prestador.
3. Criar rota `/roteiros/[sessaoId]`.
4. Integrar:
   - criar sessao;
   - listar mensagens;
   - enviar mensagem;
   - streaming SSE;
   - finalizar sessao;
   - aprovar roteiro final.
5. Criar layout split-screen:
   - chat;
   - roteiro final.
6. Criar estados de streaming:
   - conectando;
   - recebendo;
   - finalizado;
   - erro.
7. Criar fallback para resposta completa se streaming falhar, se o backend suportar.

Criterios de aceite:

- Historico fica persistido.
- Streaming mostra progresso real.
- Roteiro final nao se confunde com conversa.
- Aprovacao entra no fluxo few-shot.

Prevencao de bugs:

- Sanitizar exibicao de texto gerado.
- Evitar perda de mensagem em refresh.
- Nao duplicar mensagem se SSE reconectar.
- Tratar timeout da API Claude.

### Ciclo 10 — Portal do prestador

Objetivo:

Entregar uma camada simples de valor para o cliente sem expor informacao interna.

Passos:

1. Criar rotas:
   - `/portal/login`;
   - `/portal/convite`;
   - `/portal/dashboard`.
2. Integrar:
   - validar convite;
   - aceitar convite;
   - login portal;
   - perfil;
   - campanhas;
   - roteiros.
3. Criar dashboard do cliente:
   - saudacao;
   - resumo de campanhas;
   - Health Score traduzido;
   - roteiros aprovados;
   - proximo passo.
4. Criar linguagem nao tecnica.
5. Criar controles por permissao de vinculo.

Criterios de aceite:

- Prestador acessa apenas dados proprios.
- Assessoria ve apenas o que seu vinculo permite.
- Portal nao mostra prompts internos.
- Portal nao mostra logs, tokens ou detalhes de integracao.

Prevencao de bugs:

- Backend sempre filtra por vinculo.
- Frontend nao aceita `prestador_id` arbitrario em query como fonte de verdade.
- Testar convite expirado e convite ja usado.

### Ciclo 11 — Onboarding operacional

Objetivo:

Organizar entrada de novos clientes sem criar complexidade antes da hora.

Passos:

1. Revisar campos de `Prestador`.
2. Criar formulario de cadastro com RHF + Zod.
3. Validar categoria, cidade, estado, WhatsApp, Instagram e metas.
4. Associar responsavel.
5. Definir fase inicial `onboarding`.
6. Permitir editar dados de entrevista.
7. Preparar base para checklist futuro.

Criterios de aceite:

- SDR/CS cadastra prestador sem depender do admin Django.
- Dados essenciais ficam completos.
- Campos opcionais aparecem como pendentes, nao como erro bloqueante.

Prevencao de bugs:

- Validar no frontend e no backend.
- Nao aceitar categoria fora das choices do backend.
- Nao criar duplicidade por email/Instagram sem regra definida.

### Ciclo 12 — Observabilidade e operacao

Objetivo:

Permitir diagnosticar erros reais sem depender de prints ou logs locais.

Passos:

1. Padronizar loggers por app:
   - `marryme.prestadores`;
   - `marryme.campanhas`;
   - `marryme.roteiros`;
   - `marryme.contas`.
2. Garantir logs em stdout.
3. Adicionar contexto seguro em logs:
   - IDs;
   - app;
   - acao;
   - status.
4. Nunca logar tokens, prompts sensiveis completos ou dados privados desnecessarios.
5. Criar health checks para web e worker quando aplicavel.
6. Monitorar falhas de Celery.

Criterios de aceite:

- Erro de sync Meta e rastreavel por `prestador_id`.
- Erro de Claude e rastreavel por sessao, sem expor segredo.
- Deploy mostra logs uteis na plataforma.

Prevencao de bugs:

- Nao salvar log em arquivo local.
- Nao engolir excecao silenciosamente em task critica.
- Usar retry com limite claro.

### Ciclo 13 — Institucional e copy

Objetivo:

Ajustar comunicacao sem redesenhar o site antes da base interna amadurecer.

Passos:

1. Preservar foco em musicos.
2. Ajustar copy para reforcar:
   - agenda;
   - contratos;
   - WhatsApp;
   - campanha;
   - follow-up;
   - acompanhamento por dados.
3. Introduzir Health Score e portal apenas se estiverem em producao.
4. Nao inventar metricas, cases ou depoimentos.

Criterios de aceite:

- Copy segue tom humano, elegante e comercial.
- Promessa nao supera o que o produto entrega.
- CTA para WhatsApp e claro.

Prevencao de bugs:

- Nao misturar institucional com app interno.
- Nao trocar layout sem decisao explicita.

### Ciclo 14 — Prospecção e Apify

Objetivo:

Retomar prospeccao apenas depois da base CS/portal estar madura.

Passos:

1. Auditar `integrations/apify_client.py`.
2. Definir se prospeccao vira app Django proprio ou job externo.
3. Criar modelo de lead somente se houver fluxo operacional claro.
4. Garantir opt-out, origem dos dados e rastreabilidade.
5. Evitar misturar leads frios com prestadores clientes.

Criterios de aceite:

- Prospecção nao afeta performance do sistema CS.
- Jobs rodam assincronos.
- Leads nao contaminam base de clientes.

Prevencao de bugs:

- Nao rodar scraping em request web.
- Nao salvar dados sem origem.
- Nao chamar Claude em massa sem limite/custo definido.

---

## 7. Checklist anti-bugs por area

### Backend

- [ ] Toda nova view chama service quando ha regra de negocio.
- [ ] Toda API externa passa por `integrations/`.
- [ ] Toda task Celery tem retry, limite e log.
- [ ] Toda permissao sensivel tem teste.
- [ ] Toda listagem grande usa paginacao.
- [ ] Toda configuracao vem de env var.
- [ ] Nenhuma secret aparece em codigo, log ou resposta.
- [ ] Toda migration e reversivel ou justificada.

### Frontend

- [ ] Toda tela tem loading.
- [ ] Toda tela tem erro.
- [ ] Toda lista tem estado vazio.
- [ ] Todo formulario valida com schema.
- [ ] Todo feedback usa Sonner.
- [ ] Nenhum componente de dominio faz fetch direto.
- [ ] Nenhum token sensivel fica exposto.
- [ ] Toda acao sensivel tambem e bloqueada no backend.

### Dados e permissoes

- [ ] Usuario portal acessa apenas seu vinculo.
- [ ] Assessoria respeita permissoes efetivas.
- [ ] Admin/dev nao dependem de workaround visual.
- [ ] CS tem acesso ao necessario para operar.
- [ ] SDR nao acessa informacao fora do escopo.

### IA e conteudo

- [ ] Prompts usam dados reais.
- [ ] Claude nao recebe segredo.
- [ ] Resposta gerada nao vira dado aprovado sem acao humana.
- [ ] Roteiro aprovado entra no few-shot com categoria e tipo corretos.
- [ ] PDF via Claude usa header beta obrigatorio quando aplicavel.

### Meta Ads

- [ ] Token vem de env var ou banco conforme regra.
- [ ] Token nao e exposto no frontend.
- [ ] Campanha sem video nao quebra Health Score.
- [ ] Limitacao de retencao em campanhas de mensagens e tratada como limitacao da plataforma.
- [ ] Sync manual e sync periodico nao duplicam estado critico.

---

## 8. Definicoes pendentes antes de codar telas criticas

1. Formula final do Health Score:
   - confirmar se fica a regra operacional CPL 40%, Orcamento 30%, Leads 20%, CTR 10%;
   - ou se sera mantida a formula atual do backend com CPM/hook/retencao/frequencia/CTR.
2. Estrategia de armazenamento de JWT no frontend:
   - cookies httpOnly via camada backend/frontend;
   - ou armazenamento client-side com riscos controlados.
3. Dominio final de API:
   - temporario Railway;
   - futuro `api.marryme.com.br`.
4. Se o frontend ficara em `/app` dentro de `marryme.com.br` ou dominio/subdominio separado.
5. Nivel de acesso de `dev`, `admin`, `cs`, `sdr`, `prestador` e `assessoria` por tela.
6. Politica de aprovacao de roteiros para few-shot.
7. Agenda real de Celery Beat para sincronizacao Meta.

---

## 9. Ordem recomendada de implementacao

```text
0. Alinhar contratos e Health Score
1. Ampliar testes backend
2. Criar OpenAPI
3. Criar CI
4. Criar frontend Next.js base
5. Implementar auth equipe
6. Implementar dashboard de prestadores
7. Implementar detalhe do prestador
8. Implementar campanhas e Health Score
9. Implementar chat de roteiros split-screen
10. Implementar portal do prestador
11. Implementar onboarding operacional
12. Fortalecer observabilidade
13. Ajustar institucional sem redesenho
14. Retomar prospeccao/Apify somente depois
```

Regra de ouro:

Nao avancar para uma tela nova se a anterior ainda nao possui contrato, permissao, loading, erro, vazio e teste minimo do fluxo principal.

---

## 10. Referencias tecnicas e bibliograficas

### Arquitetura e operacao

- Wiggins, A. *The Twelve-Factor App*. https://12factor.net/
- Fowler, M. *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.
- Evans, E. *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley, 2003.
- Richardson, C. *Microservices Patterns*. Manning, 2018.

### Django, DRF e backend

- Django Software Foundation. *Django Documentation*. https://docs.djangoproject.com/
- Encode OSS. *Django REST Framework Documentation*. https://www.django-rest-framework.org/
- Simple JWT. *Django REST Framework SimpleJWT Documentation*. https://django-rest-framework-simplejwt.readthedocs.io/
- Celery Project. *Celery Documentation*. https://docs.celeryq.dev/
- PostgreSQL Global Development Group. *PostgreSQL Documentation*. https://www.postgresql.org/docs/
- Redis. *Redis Documentation*. https://redis.io/docs/

### Frontend, React e Next.js

- Vercel. *Next.js App Router Documentation*. https://nextjs.org/docs/app
- React Team. *React Documentation*. https://react.dev/
- Microsoft. *TypeScript Handbook*. https://www.typescriptlang.org/docs/
- Tailwind Labs. *Tailwind CSS Documentation*. https://tailwindcss.com/docs
- React Hook Form. *Documentation*. https://react-hook-form.com/
- Zod. *Documentation*. https://zod.dev/

### Segurança, acessibilidade e qualidade

- OWASP Foundation. *OWASP Application Security Verification Standard*. https://owasp.org/www-project-application-security-verification-standard/
- OWASP Foundation. *OWASP API Security Top 10*. https://owasp.org/API-Security/
- W3C. *Web Content Accessibility Guidelines 2.2*. https://www.w3.org/TR/WCAG22/
- Google. *web.dev Core Web Vitals*. https://web.dev/vitals/
- Nielsen Norman Group. *10 Usability Heuristics for User Interface Design*. https://www.nngroup.com/articles/ten-usability-heuristics/

### Integracoes

- Meta. *Marketing API Documentation*. https://developers.facebook.com/docs/marketing-apis/
- Anthropic. *Messages API Documentation*. https://docs.anthropic.com/
- Railway. *Railway Documentation*. https://docs.railway.app/

---

## 11. Criterio de sistema profissional completo

O sistema pode ser considerado em nivel profissional quando:

1. CS consegue operar a carteira diaria sem admin Django.
2. Prestadores, campanhas, Health Score e roteiros estao integrados em fluxo unico.
3. Portal mostra valor ao cliente sem expor detalhe interno.
4. Backend possui testes nos fluxos sensiveis.
5. Frontend possui typecheck, lint, estados de UI e padrao visual consistente.
6. CI impede regressao basica.
7. Logs permitem diagnostico em producao.
8. Secrets estao fora do codigo.
9. Jobs demorados rodam fora do request web.
10. Documentacao essencial diferencia estado atual de visao futura.

