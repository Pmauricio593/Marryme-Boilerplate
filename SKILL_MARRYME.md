# Design & Engineering Skill — MarryMe

Atualizado: Jun/2026  
Escopo: site institucional, sistema interno, portal do cliente e backend Django.

Este arquivo é guia de implementação. Ele não deve fingir que o frontend completo já existe. O estado real do projeto está em `CURSOR_CONTEXT_MARRYME.md`.

---

## Baseline de Produto

A MarryMe opera como agência especializada em crescimento digital para prestadores de casamento.

Prioridade atual:

1. Sistema interno para CS
2. Dashboard de prestadores, campanhas e Health Score
3. Chat/roteiros com IA
4. Portal do cliente
5. Ajustes de copy do institucional

Prospecção automatizada e Apify não são foco nesta fase.

---

## Baseline Visual

- `DESIGN_VARIANCE`: 5
- `MOTION_INTENSITY`: 5
- `VISUAL_DENSITY`: 4 para sistema interno; 3 para institucional

Tom visual:

- Sofisticado
- Humano
- Premium sem parecer inacessível
- Operacionalmente claro no sistema interno

Evitar visual de SaaS genérico, dashboard poluído ou site de agência com clichês.

---

## Stack por Frente

### Site institucional

Status: layout atual preservado; copy ajustável.

Diretriz:

- Não redesenhar agora
- Não trocar arquitetura visual agora
- Ajustar textos para clareza, conversão e consistência
- Manter foco principal em músicos de casamento
- Introduzir multi-categoria com cuidado, sem diluir a promessa

Se o site estático for reconstruído futuramente:

- Jekyll pode ser usado para institucional
- Templates Liquid em `.html`
- Dados em YAML
- SCSS modular
- Alpine.js/AOS/GSAP via CDN somente quando fizer sentido

### Sistema interno

Status: Next.js ainda não criado.

Quando criado:

- Next.js App Router
- TypeScript
- Tailwind CSS
- Sonner
- React Hook Form + Zod para formulários relevantes
- Cliente API centralizado em camada própria
- Rotas por domínio: auth, prestadores, campanhas, roteiros, portal
- Componentes organizados por função operacional

### Backend

Status: implementado.

Stack:

- Django
- Django REST Framework
- SimpleJWT
- Celery + Redis
- PostgreSQL
- Railway
- Docker Compose local
- Claude API
- Meta Ads API

Padrão:

```text
View/API -> Service -> Integration -> Model -> Task
```

---

## Identidade Visual

### Tipografia

- Cormorant Garamond: títulos, headings e números de destaque
- Plus Jakarta Sans: corpo, nav, botões, labels, formulários, dashboards

Nunca usar Inter, Geist ou Poppins no produto MarryMe sem decisão explícita.

### Cores

Usar tokens/variáveis. Evitar hex hardcoded espalhado.

Referência:

```scss
$primary: #1A0A2E;
$primary-mid: #2D1654;
$secondary: #C084FC;
$accent: #E879F9;
$accent-warm: #F472B6;
$gold: #D4AF37;

$text-dark: #1A1A2E;
$text-mid: #4A4A6A;
$text-muted: #8A8AA8;
$bg-light: #F8F5FF;
$bg-white: #FFFFFF;
$bg-dark: #0F0720;
$border: #E8E0F0;

$cor-musico: #C084FC;
$cor-fotografo: #F472B6;
$cor-celebrante: #34D399;
$cor-dj: #60A5FA;
$cor-cerimonialista: #FBBF24;

$hs-low: #EF4444;
$hs-mid: #F59E0B;
$hs-good: #10B981;
$hs-excellent: #6366F1;
```

### Bordas, cards e sombras

- Cards operacionais: raio entre 8px e 12px
- Pills e badges: raio full
- Sombras discretas, nunca neon decorativo
- Bordas leves para estrutura
- Dashboard deve favorecer legibilidade, não efeito visual

---

## Copy Institucional

O site atual fala bem com músicos. A copy deve preservar:

- Agenda
- Contratos fechados
- Funil que fecha
- Criativos e WhatsApp
- Comercial e follow-up
- ROI e processo repetível

Padrão de linguagem:

- Direto
- Elegante
- Sem jargão corporativo
- Sem promessas irreais
- Sem inventar números, cases ou depoimentos

Exemplos de direção:

- Ruim: "Potencialize sua presença digital com soluções inovadoras."
- Melhor: "Mais noivos certos chegando no WhatsApp, com campanha, criativo e follow-up trabalhando juntos."

Não alterar layout do institucional nesta fase.

---

## Sistema Interno — UX Prioritária

O sistema é ferramenta de trabalho do time. CS tem prioridade.

### Dashboard de prestadores

Deve responder rápido:

- Quem está em risco?
- Quem precisa de reunião?
- Quem está sem atualização?
- Quem está em onboarding?
- Quem está pronto para growth/renovação?

Estados obrigatórios:

- Loading
- Erro
- Lista vazia
- Filtro sem resultado

### Detalhe do prestador

Deve concentrar:

- Dados comerciais
- Fase
- Responsável
- Campanhas
- Health Score
- Roteiros
- Histórico operacional

### Campanhas e Health Score

Não mostrar apenas número. Sempre traduzir em ação:

- Saudável: manter/otimizar
- Atenção: revisar criativo, orçamento, campanha ou comercial
- Risco: pauta urgente de CS

### Roteiros

Prioridade de UX:

- Chat por prestador
- Histórico por sessão
- Upload/arquivos futuramente
- Streaming de resposta
- Roteiro final separado da conversa
- Aprovação do roteiro final

---

## Portal do Cliente

O portal deve ser uma camada de clareza para o prestador, não um dashboard técnico.

Prestador deve ver:

- Perfil e dados próprios
- Campanhas principais
- Health Score traduzido
- Roteiros aprovados
- Próximos passos simples

Prestador não deve ver:

- Dados de outros clientes
- Configurações internas
- Prompts internos
- Chaves, logs ou detalhes técnicos

---

## Backend — Regras de Código

### Configuração

- Tudo por env vars
- Nunca hardcodar secrets
- `.env` apenas local e ignorado pelo Git
- Serviços externos tratados como backing services

### Organização

- Views finas
- Services com regra de negócio
- Integrations para APIs externas
- Tasks para processos assíncronos
- Serializers como contrato de entrada/saída

### Logs e processos

- Logs em stdout
- Sem arquivos de runtime versionados
- Processos stateless
- Celery para trabalho demorado

### Segurança

- API keys nunca no frontend
- Portal sempre filtrado por `VinculoPrestador` (`apps.contas`)
- Validar role antes de expor ação sensível
- Evitar retornos com stack trace ou detalhes internos

---

## Frontend — Regras de Código

Quando o Next.js for criado:

### Estrutura sugerida

```text
frontend/
├── app/
│   ├── (auth)/
│   ├── (dashboard)/
│   └── portal/
├── components/
│   ├── ui/
│   ├── layout/
│   └── domain/
├── lib/
│   ├── api/
│   ├── auth/
│   └── utils/
├── types/
└── styles/
```

### Padrões

- `lib/api` concentra fetch/client
- `types` espelha serializers importantes
- Componentes de domínio não devem conter fetch direto
- Usar server/client components com critério
- `sonner` para feedback
- Nunca `alert()`
- Skeletons para telas de CS
- Lazy loading para telas pesadas

---

## Integração Frontend ↔ Backend

Base local:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Produção temporária:

```env
NEXT_PUBLIC_API_URL=https://web-production-62d5c.up.railway.app/api/v1
```

Produção ideal:

```env
NEXT_PUBLIC_API_URL=https://api.marryme.com.br/api/v1
```

Auth:

```http
Authorization: Bearer <access_token>
```

Fluxos prioritários:

1. Login equipe
2. Listagem de prestadores
3. Detalhe do prestador
4. Health Score e relatórios
5. Sessões de roteiro
6. Portal do cliente

---

## Animações e Performance

### Site institucional

- Animar apenas `transform` e `opacity`
- Respeitar `prefers-reduced-motion`
- Não misturar AOS e GSAP no mesmo elemento
- Imagens com `loading="lazy"` quando possível
- SVG para ícones
- WebP para imagens reais

### Sistema interno

- Priorizar velocidade e clareza
- Evitar animações que atrasem fluxo de trabalho
- Skeletons simples
- Tabelas/listas performáticas
- Evitar renderizar listas grandes sem paginação ou virtualização

---

## Health Score

Health Score é métrica operacional central para CS e diferencial de produto para o cliente.

Deve sempre responder:

- Qual a saúde da campanha?
- Por que está assim?
- O que CS deve fazer agora?

Faixas:

- 70+ saudável
- 40-69 atenção
- abaixo de 40 em risco

Ao comunicar para cliente, traduzir em linguagem simples. Ao comunicar para equipe, mostrar breakdown e recomendação.

---

## Proibições

- Não criar prospecção/Apify agora
- Não criar novo `.md` sem necessidade
- Não inventar métricas, depoimentos ou números
- Não expor API keys no frontend
- Não usar `alert()`
- Não fazer refatoração ampla sem ganho operacional claro
- Não redesenhar institucional nesta fase
- Não tratar frontend Next.js como existente antes de ser criado

---

## Checklist de Entrega

### Antes de mexer no backend

- [ ] A mudança pertence a app existente?
- [ ] Afeta CS?
- [ ] Afeta portal/prestador?
- [ ] Precisa de migration?
- [ ] Usa env var para config externa?
- [ ] Mantém secrets fora do Git?

### Antes de mexer no frontend

- [ ] Endpoint real existe?
- [ ] Contrato do serializer foi conferido?
- [ ] Tem loading/erro/vazio?
- [ ] Auth e roles foram considerados?
- [ ] Não há API key no client?
- [ ] Toast usa Sonner?

### Antes de mexer no institucional

- [ ] Layout foi preservado?
- [ ] Copy mantém foco em músicos?
- [ ] Não há dados inventados?
- [ ] CTA está claro?
- [ ] Tom segue MarryMe?

---

## Ordem Recomendada de Construção

1. Consolidar backend e permissões dos apps existentes
2. Criar frontend Next.js com login e shell do dashboard
3. Criar dashboard de prestadores para CS
4. Criar detalhe do prestador
5. Integrar campanhas e Health Score
6. Integrar roteiros/chat
7. Criar portal do cliente
8. Ajustar copy institucional
9. Só depois avaliar prospecção

