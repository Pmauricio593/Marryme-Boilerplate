# Contexto do projeto — MarryMe
# Site institucional + Sistema interno + Portal do cliente
# URL: https://marryme.com.br
# Backend: https://web-production-62d5c.up.railway.app
# Repositório: https://github.com/Pmauricio593/marrymesite
# Atualizado: Mai/2026

---

## O que é a MarryMe

Agência de marketing digital especializada exclusivamente em prestadores
de serviços para casamentos no Brasil — músicos, fotógrafos, celebrantes,
DJs e cerimonialistas. Foco no eixo Sul-Sudeste.

**O que a MarryMe entrega para cada cliente:**
- Gestão completa de campanhas no Meta Ads (Facebook e Instagram)
- Roteiros de vídeo de apresentação (para WhatsApp)
- Roteiros de CTA para anúncios Meta Ads
- Direção criativa para captação de materiais
- Propostas comerciais personalizadas
- Análise estratégica de posicionamento
- Acompanhamento de leads gerados pelas campanhas
- Relatórios de performance com Health Score automatizado
- Portal do cliente com visão do próprio desempenho

**Posicionamento:**
> "A agência especializada em crescimento digital para músicos,
> fotógrafos, celebrantes, DJs e cerimonialistas do Brasil."

**Tom da marca:** Sofisticado, confiante, próximo.
Elegante sem ser frio. Premium sem ser inacessível.

**3 pilares:**
- **Especialização** — 100% focados no mercado de casamentos
- **Acompanhamento** — Health Score exclusivo e relatórios reais
- **Resultados** — Leads qualificados via Meta Ads otimizado

**Categorias atendidas (cada uma tem cor própria no sistema):**
- Músico e Banda → $cor-musico #C084FC
- Fotógrafo e Videomaker → $cor-fotografo #F472B6
- Celebrante → $cor-celebrante #34D399
- DJ → $cor-dj #60A5FA
- Cerimonialista → $cor-cerimonialista #FBBF24

---

## Arquitetura geral do sistema

```
marryme.com.br (Jekyll)
└── Site institucional estático
    Captação de novos clientes prestadores
    Público: qualquer visitante

marryme.com.br/app (Next.js — em construção)
└── Sistema interno + Portal do cliente
    Equipe: dashboard completo, gestão, geração de conteúdo
    Prestador: próprio perfil, roteiros, health score, campanhas

api.marryme.com.br (Django — Railway)
└── Backend principal
    API REST completa
    Autenticação JWT por role
    Celery para processamento assíncrono
```

---

## Stack técnica — Site Jekyll (este projeto)

### Jekyll
- Gerador de site estático com suporte nativo a Sass/SCSS
- Layouts em Liquid (`_layouts/`), componentes em `_includes/`
- Conteúdo gerenciado via YAML em `_data/` e front matter nas páginas
- Sem build tool externo — `jekyll serve` compila tudo automaticamente
- Apenas arquivos `.html` — nunca `.md` nas páginas

### Sass / SCSS
- Compilado nativamente pelo Jekyll (sem Webpack, Vite ou Node)
- Todo CSS em `_sass/`, importado por `assets/css/main.scss`
- Usar variáveis para cores, tipografia e breakpoints — nunca hardcoded
- Usar `@mixin` para padrões repetidos
- Aninhamento BEM (`&__element`, `&--modifier`)
- Nunca usar `!important`

### Alpine.js
- Carregado via CDN no `_layouts/default.html`
- UI state local: menu mobile, acordeon, tabs, dropdown, sliders, filtros
- Diretivas: `x-data`, `x-show`, `x-bind`, `x-on`, `@click`, `x-transition`, `x-init`
- Nunca usar para lógica de negócio

### GSAP + AOS
- Ambos via CDN — sem instalação local
- AOS para scroll reveals: `data-aos="fade-up"`, `data-aos-delay="100"`
  `AOS.init({ once: true, duration: 800, easing: 'ease-out-cubic', offset: 80 })`
- GSAP para animações complexas: hero, timelines, parallax, counters, stroke draw
- Preferir animações em `opacity` e `transform` — nunca `width`, `height`, `top/left`
- Respeitar `prefers-reduced-motion`
- Nunca misturar AOS e GSAP no mesmo elemento

---

## Identidade visual

### Paleta de cores

```scss
// _sass/_variables.scss

// Cores principais
$primary:           #1A0A2E;   // Roxo noite — nav, footer, fundos premium
$primary-mid:       #2D1654;   // Roxo médio — hover, backgrounds internos
$secondary:         #C084FC;   // Lilás vibrante — destaques, eyebrows
$accent:            #E879F9;   // Rosa-lilás — CTAs, hover states
$accent-warm:       #F472B6;   // Rosa quente — elementos emocionais
$gold:              #D4AF37;   // Dourado premium
$gold-light:        #F5E6A3;

// CTA
$cta:               #E879F9;
$cta-hover:         #D946EF;
$cta-text:          #FFFFFF;

// Neutras
$text-dark:         #1A1A2E;
$text-mid:          #4A4A6A;
$text-muted:        #8A8AA8;
$bg-light:          #F8F5FF;
$bg-white:          #FFFFFF;
$bg-dark:           #0F0720;
$border:            #E8E0F0;
$border-focus:      #C084FC;

// Cores por categoria de prestador
$cor-musico:              #C084FC;   $cor-musico-light:        #F3E8FF;
$cor-fotografo:           #F472B6;   $cor-fotografo-light:     #FDF2F8;
$cor-celebrante:          #34D399;   $cor-celebrante-light:    #ECFDF5;
$cor-dj:                  #60A5FA;   $cor-dj-light:            #EFF6FF;
$cor-cerimonialista:      #FBBF24;   $cor-cerimonialista-light:#FFFBEB;

// Health Score — métrica exclusiva MarryMe
$hs-low:            #EF4444;   // 0–39  crítico
$hs-mid:            #F59E0B;   // 40–59 atenção
$hs-good:           #10B981;   // 60–79 bom
$hs-excellent:      #6366F1;   // 80–100 excelente

// Sombras
$shadow-sm:   0 1px 3px rgba(26, 10, 46, 0.08);
$shadow-md:   0 4px 16px rgba(26, 10, 46, 0.12);
$shadow-lg:   0 8px 32px rgba(26, 10, 46, 0.16);
$shadow-xl:   0 16px 48px rgba(26, 10, 46, 0.20);
$shadow-glow: 0 0 24px rgba(192, 132, 252, 0.35);

// Transições
$transition-fast:   all 0.15s ease;
$transition-base:   all 0.25s ease;
$transition-slow:   all 0.4s ease;
$transition-spring: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Tipografia

```scss
$font-display: 'Cormorant Garamond', Georgia, serif;
$font-body:    'Plus Jakarta Sans', system-ui, sans-serif;

// Escala
$text-xs:    0.75rem;    $text-4xl:   2.25rem;
$text-sm:    0.875rem;   $text-5xl:   3rem;
$text-base:  1rem;       $text-6xl:   3.75rem;
$text-lg:    1.125rem;   $text-7xl:   4.5rem;
$text-xl:    1.25rem;
$text-2xl:   1.5rem;
$text-3xl:   1.875rem;

// Breakpoints
$bp-sm:  640px;   $bp-xl:  1280px;
$bp-md:  768px;   $bp-2xl: 1536px;
$bp-lg:  1024px;
```

### Espaçamento e bordas

```scss
$spacing-xs: 0.25rem;  $spacing-2xl: 3rem;
$spacing-sm: 0.5rem;   $spacing-3xl: 4rem;
$spacing-md: 1rem;     $spacing-4xl: 6rem;
$spacing-lg: 1.5rem;   $spacing-5xl: 8rem;
$spacing-xl: 2rem;

$container-max:    1280px;
$container-wide:   1440px;
$container-narrow: 768px;

$radius-sm:   4px;    $radius-xl:   24px;
$radius-md:   8px;    $radius-full: 9999px;
$radius-lg:   16px;
```

---

## Estrutura de arquivos do site

```
marryme-site/
│
├── _layouts/
│   ├── default.html          # Shell: head, topbar, nav, footer, CDNs
│   └── page.html             # Páginas internas
│
├── _includes/
│   ├── nav/
│   │   ├── topbar.html       # Instagram, WhatsApp, "Atendemos todo o Brasil"
│   │   └── navbar.html       # Nav + dropdown categorias + CTA (Alpine.js)
│   ├── footer/
│   │   └── footer.html       # 4 colunas: marca, nav, categorias, contato
│   ├── global/
│   │   ├── cta-contato.html  # Seção de conversão — fundo $bg-dark
│   │   ├── depoimentos.html  # Slider Alpine.js — depoimentos de prestadores
│   │   └── resultados.html   # Stats com counter GSAP
│   ├── home/
│   │   ├── hero.html         # Gradiente $bg-dark→$primary, GSAP timeline
│   │   ├── para-quem.html    # 5 cards de categorias com cores próprias
│   │   ├── como-funciona.html # Timeline zig-zag 5 etapas
│   │   ├── diferenciais.html # Cards + card destaque Health Score
│   │   └── numeros.html      # Stats counter — fundo $primary
│   ├── sobre/
│   │   ├── hero-sobre.html
│   │   ├── historia.html
│   │   ├── missao-valores.html
│   │   └── equipe.html
│   ├── servicos/
│   │   ├── hero-servicos.html
│   │   ├── lista-servicos.html
│   │   ├── health-score.html  # Arc SVG animado — gauge exclusivo
│   │   └── processo-servico.html
│   ├── clientes/
│   │   ├── hero-clientes.html
│   │   ├── filtro-categorias.html  # Pills Alpine.js
│   │   └── cases.html
│   ├── como-funciona/
│   │   ├── hero-processo.html
│   │   ├── timeline.html
│   │   └── faq.html           # Accordion Alpine.js
│   └── contato/
│       ├── hero-contato.html
│       ├── formulario.html
│       └── whatsapp-direto.html
│
├── _sass/
│   ├── _variables.scss
│   ├── _base.scss
│   ├── _typography.scss
│   ├── _nav.scss
│   ├── _components.scss
│   ├── _layout.scss
│   ├── _animations.scss
│   ├── _responsive.scss
│   ├── global/
│   │   ├── _hero.scss, _footer.scss, _cta-contato.scss, _depoimentos.scss
│   ├── pages/home/
│   │   ├── _para-quem.scss, _como-funciona.scss, _diferenciais.scss, _numeros.scss
│   ├── pages/sobre/
│   │   ├── _hero.scss, _historia.scss, _missao-valores.scss, _equipe.scss
│   ├── pages/servicos/
│   │   ├── _hero.scss, _lista-servicos.scss, _health-score.scss, _processo-servico.scss
│   ├── pages/clientes/
│   │   ├── _hero.scss, _filtro.scss, _cases.scss
│   ├── pages/como-funciona/
│   │   ├── _hero.scss, _timeline.scss, _faq.scss
│   └── pages/contato/
│       ├── _hero.scss, _formulario.scss
│
├── _data/
│   ├── nav.yml
│   ├── categorias.yml         # 5 categorias com cor, slug, exemplos
│   ├── servicos.yml           # Meta Ads, Roteiros, HS, Direção Criativa, etc.
│   ├── processo.yml           # 5 etapas: Onboarding → Voo de Cruzeiro
│   ├── diferenciais.yml       # Pilares da MarryMe
│   ├── resultados.yml         # 42 prestadores, 12 estados, HS médio 58
│   ├── depoimentos.yml        # Airton Sax, Rony Ribeiro, Padre Beto, etc.
│   ├── faq.yml
│   └── equipe.yml
│
├── assets/
│   ├── css/main.scss          # Importa todos os _sass/
│   ├── js/
│   │   ├── main.js            # AOS.init(), smooth scroll, active nav
│   │   ├── gsap-home.js       # Animações homepage
│   │   ├── gsap-sobre.js      # Timeline história
│   │   └── gsap-servicos.js   # Gauge Health Score
│   ├── images/
│   │   ├── logo/
│   │   │   ├── marryme-logo.svg
│   │   │   ├── marryme-logo-branco.svg
│   │   │   └── favicon.ico
│   │   ├── home/, clientes/, equipe/
│   │   └── og-image.jpg
│   └── video/
│       └── hero-background.mp4  # opcional
│
├── index.html
├── sobre.html
├── servicos.html
├── clientes.html
├── como-funciona.html
├── contato.html
│
├── backend/                   # Django — subprojeto no mesmo repositório
│   ├── apps/
│   │   ├── prestadores/       # Cadastro, pipeline, portal do cliente
│   │   ├── campanhas/         # Meta Ads, Health Score, relatórios
│   │   └── roteiros/          # Chat, sessões, few-shot, geração IA
│   ├── core/                  # Auth, permissions, pagination, exceptions
│   ├── integrations/          # Meta Ads, Claude AI, Apify
│   ├── docker/
│   ├── docker-compose.yml
│   └── railway.toml
│
├── _config.yml
├── CURSOR_CONTEXT_MARRYME.md  # este arquivo
└── SKILL_MARRYME.md
```

---

## _config.yml base

```yaml
title: "MarryMe"
tagline: "Marketing Digital para Prestadores de Casamentos"
description: "A agência especializada em crescimento digital para músicos,
  fotógrafos, celebrantes, DJs e cerimonialistas do Brasil."
url: "https://marryme.com.br"
baseurl: ""
lang: "pt-BR"

contact:
  whatsapp: "5511999999999"
  whatsapp_message: "Olá! Vim pelo site e quero saber mais sobre os serviços da MarryMe."
  email: "contato@marryme.com.br"
  instagram: "marryme.ag"

social:
  instagram: "https://instagram.com/marryme.ag"
  whatsapp: "https://wa.me/5511999999999"

plugins:
  - jekyll-seo-tag
  - jekyll-sitemap

sass:
  style: compressed
  sass_dir: _sass

permalink: /:title/
exclude:
  - Gemfile, Gemfile.lock, README.md, node_modules
  - CURSOR_CONTEXT_MARRYME.md, SKILL_MARRYME.md
  - backend/
```

---

## Como cada página monta suas sections

```html
<!-- index.html -->
---
layout: default
title: "MarryMe — Marketing Digital para Prestadores de Casamentos"
description: "..."
extra_js:
  - /assets/js/gsap-home.js
---
{% include home/hero.html %}
{% include home/para-quem.html %}
{% include home/como-funciona.html %}
{% include home/diferenciais.html %}
{% include home/numeros.html %}
{% include global/depoimentos.html %}
{% include global/cta-contato.html %}
```

```html
<!-- servicos.html -->
---
layout: default
title: "Serviços — O que a MarryMe Entrega"
extra_js:
  - /assets/js/gsap-servicos.js
---
{% include servicos/hero-servicos.html %}
{% include servicos/lista-servicos.html %}
{% include servicos/health-score.html %}
{% include servicos/processo-servico.html %}
{% include global/depoimentos.html %}
{% include global/cta-contato.html %}
```

---

## Backend Django — contexto completo

### URLs de produção

```
Base:     https://web-production-62d5c.up.railway.app
Health:   /health/
Admin:    /admin/
API:      /api/v1/
```

### Endpoints principais

```
Auth equipe:    POST /api/v1/auth/login/
Auth refresh:   POST /api/v1/auth/refresh/
Auth prestador: POST /api/v1/portal/auth/login/
Primeiro acesso: POST /api/v1/portal/auth/primeiro-acesso/

Prestadores:    GET/POST /api/v1/prestadores/
Detalhe:        GET/PUT/DELETE /api/v1/prestadores/{id}/
Fases:          POST /api/v1/prestadores/{id}/atualizar-fase/
Sync Meta:      POST /api/v1/prestadores/{id}/sync-meta/

Health Score:   GET /api/v1/health-scores/?prestador={id}
Último HS:      GET /api/v1/health-scores/ultimo/?prestador={id}
Métricas:       GET /api/v1/metricas/?prestador={id}
Relatórios:     GET/POST /api/v1/relatorios/

Chat sessões:   GET/POST /api/v1/sessoes/
Mensagem:       POST /api/v1/sessoes/{id}/mensagem/
Stream:         POST /api/v1/sessoes/{id}/stream/
Roteiros:       GET /api/v1/roteiros-finais/?prestador={id}
Aprovar:        POST /api/v1/roteiros-finais/{id}/aprovar/

Portal perfil:  GET /api/v1/portal/perfil/
```

### Roles e permissões

```
admin     → acesso total
dev       → acesso total
cs        → acesso total exceto deletar
sdr       → leitura + criação
prestador → apenas próprios dados via portal
```

### Health Score — fórmula oficial

```
Custo por Mensagem Iniciada  35 pts
Hook Rate                    25 pts
Retenção (ThruPlay)          20 pts — redistribuído se indisponível
Frequência                   10 pts
CTR botão de mensagem        10 pts

Score >= 70 → saudável ($hs-good / $hs-excellent)
Score 40-69 → atenção ($hs-mid)
Score < 40  → em risco ($hs-low)

Campanhas de Mensagens: ThruPlay indisponível via API Meta →
20 pts redistribuídos automaticamente para Hook Rate.
```

### Serviços Railway ativos

```
web            → Django + Gunicorn (porta 8080)
celery-worker  → processamento assíncrono
celery-beat    → tarefas agendadas (sync Meta toda segunda 8h)
PostgreSQL     → banco principal
Redis          → broker de filas
```

---

## Padrões de componentes

### Botões

```scss
.btn {
  display: inline-flex; align-items: center; gap: $spacing-sm;
  padding: 0.75rem 1.5rem; font-family: $font-body;
  font-size: $text-sm; font-weight: 600;
  border-radius: $radius-full; transition: $transition-spring;

  &--primary {
    background: $cta; color: $cta-text;
    &:hover { background: $cta-hover; box-shadow: $shadow-glow; }
  }
  &--outline {
    background: transparent; border: 1px solid rgba(255,255,255,0.3); color: white;
    &:hover { border-color: $secondary; color: $secondary; }
  }
  &--large { padding: 1rem 2rem; font-size: $text-lg; }
}
```

### Eyebrow

```scss
.eyebrow {
  display: inline-block; font-family: $font-body;
  font-size: $text-sm; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: $secondary; margin-bottom: $spacing-md;

  &--white { color: $accent; }
  &--gold  { color: $gold; }
}
```

---

## Padrões GSAP

```javascript
// Hero timeline
gsap.timeline({ delay: 0.2 })
  .from('#hero-eyebrow',  { opacity: 0, y: 30, duration: 0.6, ease: 'power3.out' })
  .from('#hero-title',    { opacity: 0, y: 30, duration: 0.7, ease: 'power3.out' }, '-=0.3')
  .from('#hero-subtitle', { opacity: 0, y: 30, duration: 0.6, ease: 'power3.out' }, '-=0.3')
  .from('#hero-ctas',     { opacity: 0, y: 30, duration: 0.5, ease: 'power3.out' }, '-=0.2');

// Counter animado
ScrollTrigger.create({
  trigger: '.numeros-section', start: 'top 80%', once: true,
  onEnter: () => {
    document.querySelectorAll('.counter').forEach(el => {
      gsap.fromTo(el, { textContent: 0 }, {
        textContent: parseInt(el.dataset.target),
        duration: 2, ease: 'expo.out',
        snap: { textContent: 1 },
        onUpdate() { el.textContent = Math.round(parseFloat(el.textContent)); }
      });
    });
  }
});

// Health Score gauge (arc SVG)
// strokeDashoffset animado de comprimento total até valor do score
// Cor dinâmica: $hs-low / $hs-mid / $hs-good / $hs-excellent
```

---

## Padrões Alpine.js

```html
<!-- Slider depoimentos -->
<div x-data="{ active: 0 }"
     x-init="setInterval(() => active = (active + 1) % 5, 5000)">
  <div x-show="active === 0" x-transition>...</div>
  <button @click="active = 0" :class="{ 'is-active': active === 0 }"></button>
</div>

<!-- Filtro categorias -->
<div x-data="{ filtro: 'todos' }">
  <button @click="filtro = 'musico'" :class="{ 'is-active': filtro === 'musico' }">Músicos</button>
  <div x-show="filtro === 'todos' || filtro === 'musico'" x-transition>...</div>
</div>

<!-- FAQ accordion -->
<div x-data="{ aberto: null }">
  <button @click="aberto = aberto === 0 ? null : 0">Pergunta</button>
  <div x-show="aberto === 0" x-transition>Resposta</div>
</div>
```

---

## Proibições globais (anti-IA)

- **Sem glows neon** — exceção: `$shadow-glow` no CTA hover
- **Sem preto puro** — usar `$text-dark` (#1A1A2E)
- **Sem gradientes em texto** de headers
- **Sem sombras decorativas** — bordas 0.5px
- **Sem border-radius > 8px** em cards (50px só em pills)
- **Nunca Cormorant Garamond** no corpo, nav ou botões
- **Nunca Inter, Geist, Poppins** — só Cormorant + Plus Jakarta Sans
- **Sem grids genéricos** de 3 cards iguais — usar magazine grid
- **Sem nomes genéricos** — usar Airton Sax, Rony Ribeiro, Padre Beto
- **Sem números fake** — usar 42 prestadores, 12+ estados, HS 58
- **Sem lorem ipsum** — usar textos reais da MarryMe
- **ANTI-EMOJI** — nunca emojis em código ou conteúdo
- **Nunca `.md`** nas páginas — apenas `.html`
- **Animar só** `transform` e `opacity`

---

## Visão de produto e escalabilidade

### O que o sistema entrega hoje
```
Site institucional (captação)
Sistema interno (gestão da equipe)
Portal do cliente (prestador vê próprio desempenho)
```

### O que vem a seguir
```
Cobrança automática via WhatsApp Business API
SDR automatizado (atendimento de leads por IA)
Prospecção automatizada (Apify + Claude + Instagram)
Exportação de proposta comercial em PDF
Análise IA dos relatórios de campanha
```

### Visão de longo prazo (multi-tenant / SaaS)
```
Hoje: MarryMe usa o sistema internamente

Próximo: Portal do cliente (prestadores acessam)

Futuro: Outras agências de marketing para casamentos
        pagam mensalidade para usar o sistema

Escalabilidade: adicionar campo agencia_id nos models
                middleware de tenant filtra automaticamente
                zero reescrita — arquitetura já suporta
```

### Por que não é CRM
O sistema vai além de organizar contatos e pipeline.
Gera conteúdo de marketing com IA, analisa campanhas em tempo real,
aprende com os melhores resultados (few-shot), entrega portal para
o cliente acompanhar tudo. É um sistema de inteligência operacional
especializado no mercado de casamentos.

---

## Prompts úteis para o Cursor

```
"Crie _includes/nav/navbar.html com Alpine.js: topbar com Instagram e
WhatsApp, nav com logo MarryMe, dropdown de Categorias com bolinha na cor
de cada categoria ($cor-*), botão CTA 'Quero ser cliente'. SCSS em _nav.scss."

"Crie _includes/home/hero.html com gradiente $bg-dark→$primary, círculos
desfocados com $secondary e $accent, título Cormorant Garamond, subtítulo
Plus Jakarta Sans, 2 CTAs. GSAP timeline: eyebrow→título→subtítulo→CTAs."

"Crie _includes/servicos/health-score.html com arc SVG animado 0-100,
cor dinâmica ($hs-low/$hs-mid/$hs-good/$hs-excellent), número central
Cormorant Garamond, breakdown dos 5 componentes com barras menores."

"Crie _includes/home/numeros.html iterando site.data.resultados com
counter GSAP ScrollTrigger. Número em <strong> Cormorant, sufixo em
<span> Jakarta. Fundo $primary, grid 4 colunas, entrada elastic.out."

"Crie _data/categorias.yml com as 5 categorias: id, nome, slug,
descricao, icone, cor (#hex), cor_light (#hex), exemplos (array)."
```

---

## Performance

- Hardware acceleration: só `transform` e `opacity`
- Z-index: topbar 201, navbar 200, dropdown 9999, hero 1, toast 500, WhatsApp 500
- `font-display: swap` + preconnect Google Fonts
- `loading="lazy"` em todas as imagens (exceto primeira de slideshow)
- SVG para ícones e logos, WebP para fotos
- `will-change` só no dropdown e animações contínuas
- `prefers-reduced-motion` verificado no início de cada script GSAP
- Scripts pesados só nas páginas que precisam via `extra_js`
