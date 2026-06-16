# Design Engineering Skill — MarryMe
# Guia completo de construção do site institucional + sistema interno
# Atualizado: Mai/2026

---

## 1. BASELINE DE DESIGN

- **DESIGN_VARIANCE:** 5 (1=Simetria perfeita, 10=Caos artístico)
- **MOTION_INTENSITY:** 6 (1=Estático, 10=Cinematográfico)
- **VISUAL_DENSITY:** 3 (1=Galeria de arte/Arejado, 10=Cockpit/Dados compactos)

Tom visual: **sofisticado, confiante e próximo** — nunca frio/corporativo,
nunca infantil. Referência: mercado de casamentos premium no Brasil.

---

## 2. STACK — NÃO NEGOCIÁVEL

### Site institucional (Jekyll)
- **Gerador:** Jekyll estático. Sem Node, Webpack, Vite ou React.
- **Templates:** Liquid (`.html`). Layouts em `_layouts/`, componentes em `_includes/`.
- **Dados:** YAML em `_data/` e front matter nas páginas.
- **Estilos:** Sass/SCSS nativo pelo Jekyll. Todo CSS em `_sass/`, importado por `assets/css/main.scss`.
- **Interatividade:** Alpine.js via CDN — UI state (menu, acordeon, tabs, filtros, sliders).
- **Animações:** AOS via CDN para scroll reveals. GSAP + ScrollTrigger via CDN para animações complexas.
- **Formato:** Apenas `.html` — nunca `.md` nas páginas.

### Backend (Django — Railway)
- **Framework:** Django 6.0 + Django REST Framework
- **Auth:** JWT com `djangorestframework-simplejwt`
- **Filas:** Celery + Redis
- **IA:** Anthropic Claude (`claude-sonnet-4-6`)
- **Meta Ads:** Graph API v18.0
- **Deploy:** Railway (web + celery-worker + celery-beat + PostgreSQL + Redis)
- **Padrão de código:** View → Service → Integration → Model → Task

### Sistema interno (Next.js — em construção)
- **Framework:** Next.js 14 App Router + Tailwind CSS
- **Deploy:** Vercel
- **Consome:** API Django via JWT

---

## 3. ARQUITETURA SCSS MODULAR

```
_sass/
  _variables.scss       # Cores, tipografia, espaçamento, breakpoints
  _base.scss            # Reset, body, container, section, links
  _typography.scss      # Headings, parágrafos, eyebrows, listas
  _nav.scss             # Topbar, navbar, dropdown, mobile drawer
  _components.scss      # Botões, badges, pills, cards, tags, inputs
  _layout.scss          # Grid, container, section spacing
  _animations.scss      # Keyframes, AOS overrides, prefers-reduced-motion
  _responsive.scss      # Media queries globais

  global/
    _hero.scss           # Hero homepage + hero páginas internas
    _footer.scss         # Footer 4 colunas
    _cta-contato.scss    # Seção de conversão
    _depoimentos.scss    # Slider Alpine.js
    _resultados.scss     # Stats counter

  pages/home/
    _para-quem.scss      # Cards 5 categorias
    _como-funciona.scss  # Preview do processo
    _diferenciais.scss   # Cards diferenciais + Health Score destaque
    _numeros.scss        # Stats full-width fundo $primary

  pages/sobre/
    _hero.scss, _historia.scss, _missao-valores.scss, _equipe.scss

  pages/servicos/
    _hero.scss, _lista-servicos.scss, _health-score.scss, _processo-servico.scss

  pages/clientes/
    _hero.scss, _filtro.scss, _cases.scss

  pages/como-funciona/
    _hero.scss, _timeline.scss, _faq.scss

  pages/contato/
    _hero.scss, _formulario.scss
```

**Regra:** ao criar nova seção, criar o partial correspondente e importar no `main.scss`.
Nunca adicionar CSS avulso. Nunca valores hardcoded — sempre variáveis.

---

## 4. IDENTIDADE VISUAL — REGRAS ABSOLUTAS

### Tipografia
- **Cormorant Garamond** — **exclusivo para títulos, headings e números de destaque**.
  Nunca no corpo, nav, botões ou labels.
- **Plus Jakarta Sans** — todo o resto: nav, corpo, botões, badges, labels,
  formulários, sufixos de stats.
- Respeitar a escala `$text-xs` a `$text-7xl` do `_variables.scss`.

### Cores
Nunca valores hexadecimais diretos. Sempre variáveis SCSS:

```
Fundos escuros:     $bg-dark, $primary, $primary-mid
Fundos claros:      $bg-white, $bg-light
CTAs:               $cta, $cta-hover, $secondary
Texto:              $text-dark, $text-mid, $text-muted
Categorias:         $cor-{categoria}, $cor-{categoria}-light
Health Score:       $hs-low, $hs-mid, $hs-good, $hs-excellent
Bordas:             $border, $border-focus
Sombras:            $shadow-sm/md/lg/xl, $shadow-glow (só no CTA hover)
```

### Bordas e superfícies
- Bordas: `0.5px solid $border`
- `border-radius` máximo `8px` em cards. Exceção: pills `50px`.
- Dropdown navbar: única exceção com `box-shadow` (`$shadow-md`).
- Nunca `box-shadow` decorativo em outros elementos.

### Espaçamento
- Usar sempre a escala `$spacing-xs` a `$spacing-5xl`.
- Seções com `padding: $spacing-5xl 0` como padrão.
- Container com `max-width: $container-max` e `margin: 0 auto`.

---

## 5. REGRAS DE ALPINE.JS

- Diretivas: `x-data`, `x-show`, `x-bind`, `x-on`, `@click`, `x-transition`, `x-init`.
- Só UI state local — nunca lógica de negócio.
- Cada componente autocontido no seu `x-data`.

### Padrões implementados

**Slider de depoimentos:**
```html
<div x-data="{ active: 0, total: 5 }"
     x-init="setInterval(() => active = (active + 1) % total, 5000)">
  <div x-show="active === 0" x-transition>...</div>
  <button @click="active = 0"
          :class="{ 'is-active': active === 0 }"></button>
</div>
```
Itens empilhados com `position: absolute; inset: 0; opacity: 0`.
`.is-active { opacity: 1 }` com `transition: opacity 1.2s ease`.

**Filtro de categorias:**
```html
<div x-data="{ filtro: 'todos' }">
  <button @click="filtro = 'musico'"
          :class="{ 'is-active': filtro === 'musico' }">Músicos</button>
  <div x-show="filtro === 'todos' || filtro === 'musico'"
       x-transition>...</div>
</div>
```

**FAQ accordion:**
```html
<div x-data="{ aberto: null }">
  <button @click="aberto = aberto === 0 ? null : 0">Pergunta</button>
  <div x-show="aberto === 0" x-transition>Resposta</div>
</div>
```

**Dropdown navbar:**
Usar `x-transition:enter`, `x-transition:enter-start` com classes CSS.

---

## 6. REGRAS DE ANIMAÇÃO

### AOS
```html
data-aos="fade-up" data-aos-delay="100"
```
```javascript
AOS.init({ once: true, duration: 800, easing: 'ease-out-cubic', offset: 80 });
```

### GSAP — regras
- Animar só `opacity` e `transform` — nunca `width`, `height`, `top/left`.
- Verificar `prefers-reduced-motion` no início de cada script e fazer `return` se ativo.
- Nunca misturar AOS e GSAP no mesmo elemento.
- Scripts GSAP carregados via `extra_js` no front matter da página.

### Padrões GSAP implementados

**Hero timeline:**
```javascript
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
gsap.timeline({ delay: 0.2 })
  .from('#hero-eyebrow',  { opacity: 0, y: 30, duration: 0.6, ease: 'power3.out' })
  .from('#hero-title',    { opacity: 0, y: 30, duration: 0.7, ease: 'power3.out' }, '-=0.3')
  .from('#hero-subtitle', { opacity: 0, y: 30, duration: 0.6, ease: 'power3.out' }, '-=0.3')
  .from('#hero-ctas',     { opacity: 0, y: 30, duration: 0.5, ease: 'power3.out' }, '-=0.2');
```

**Character-level text splitting (hero):**
Título dividido em `<span class="hero__char">` para stagger granular (`stagger: 0.028`).
Espaços recebem classe `--space` com `width: 0.3em`.

**Counter animado:**
```javascript
ScrollTrigger.create({
  trigger: '.numeros-section', start: 'top 80%', once: true,
  onEnter: () => {
    document.querySelectorAll('.counter').forEach(el => {
      gsap.fromTo(el, { textContent: 0 }, {
        textContent: parseInt(el.dataset.target),
        duration: 2, ease: 'expo.out',
        snap: { textContent: 1 },
        onUpdate() { el.textContent = Math.round(parseFloat(el.textContent)).toLocaleString('pt-BR'); }
      });
    });
  }
});
```
Número em `<strong>` (Cormorant), sufixo em `<span>` (Jakarta) — animação só no `<strong>`.
Entrada com `elastic.out(1, 0.5)` para bounce nos stats.

**Health Score gauge (exclusivo MarryMe):**
```javascript
// Arc SVG com strokeDashoffset animado
// Cor dinâmica por faixa:
// 0–39:   $hs-low     #EF4444
// 40–59:  $hs-mid     #F59E0B
// 60–79:  $hs-good    #10B981
// 80–100: $hs-excellent #6366F1
// ease: 'power2.inOut', duration: 1.5, ativado por ScrollTrigger
```

**SVG stroke draw:**
```javascript
document.querySelectorAll('.draw-path').forEach(path => {
  const len = path.getTotalLength();
  gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
  gsap.to(path, { strokeDashoffset: 0, ease: 'power2.inOut',
                  stagger: 0.35, scrollTrigger: { trigger: path, start: 'top 85%' } });
});
```

**Split reveal (2 colunas):**
Esquerda: `x: -60`, direita: `x: 60`. Overlap `-=0.6`.

**Parallax decorativo:**
```javascript
gsap.to('.hero__deco', { y: 80, ease: 'none',
  scrollTrigger: { trigger: '.hero', scrub: 1.2 } });
```
Nunca aplicar parallax no container de conteúdo — só em decorações.

**Timeline do processo (como-funciona):**
Etapas entram individualmente com `scrub: 1`. Números das etapas como counter em sequência.
Linha conectora com `height` controlada por `ScrollTrigger.scrub`.

---

## 7. COMPONENTES — REFERÊNCIA DE IMPLEMENTAÇÃO

### Navbar
- Topbar sticky (`z-index: 201`), fundo `$primary`, links brancos.
  Instagram e WhatsApp à direita, "Atendemos todo o Brasil" à esquerda.
- Navbar sticky abaixo. Fundo `$bg-white`, `border-bottom: 0.5px solid $border`.
- Logo SVG à esquerda, links centralizados, CTA à direita.
- Dropdown de Categorias: grid 5 itens com bolinha na cor da categoria.
- Menu mobile: drawer full-width com Alpine.js toggle.
- Botão CTA: `btn--pill` com `border-radius: 50px`.

### Hero Homepage
- Gradiente `$bg-dark → $primary`.
- Círculos desfocados: `$secondary` e `$accent` em opacidade 0.06–0.15.
- Parallax nos círculos via ScrollTrigger.
- Stats abaixo dos CTAs com `border-top: 0.5px solid rgba(255,255,255,0.1)`.

### Hero Páginas Internas
- Split-screen: texto esquerda + asset visual direita.
- Fundo `$primary` com overlay gradiente diagonal.
- Eyebrow em `$secondary` para contraste no fundo escuro.
- Split reveal GSAP ao entrar na viewport.

### Cards de Categoria (Para Quem)
- Grid 5 colunas desktop, 3 tablet, 2 mobile.
- Fundo: `$cor-*-light`. Border: `1px solid $border`.
- Hover: border muda para `$cor-*` cheia, `translateY(-4px)`, `$shadow-md`.
- Bolinha 48px na cor da categoria com ícone SVG.
- AOS `fade-up` com delay escalonado por card (0, 100, 200ms...).

### Health Score (Gauge exclusivo)
- Arc SVG com `stroke-dashoffset` animado por ScrollTrigger.
- Cor dinâmica por faixa (`$hs-*`).
- Número central Cormorant Garamond `$text-5xl`.
- Label da faixa abaixo (Crítico / Atenção / Bom / Excelente).
- Breakdown dos 5 componentes com barras de progresso menores.
- Badge "Exclusivo MarryMe" em `$secondary`.

### Números / Stats
- Fundo `$primary` full-width. Grid 4 colunas.
- Número em `<strong>` Cormorant `$text-6xl`, sufixo em `<span>` Jakarta.
- Counter GSAP com `elastic.out(1, 0.5)` ao entrar na viewport.
- Dados reais: 42+ prestadores, 12+ estados, Health Score médio 58.

### Depoimentos (Slider)
- Alpine.js auto-play 5s.
- Card: `max-width: 720px`, centrado, `$shadow-lg`, `$radius-xl`.
- Aspas decorativas: Cormorant `$text-7xl`, cor `$secondary` opacity 0.3.
- Foto circular 56px, nome, categoria + cidade, badge de resultado.
- Dots: 8px → 24px pill quando ativa, cor `$secondary`.
- Nomes reais: Airton Sax, Rony Ribeiro, Padre Beto, Kanirê Musical.

### Filtro de Categorias (Clientes)
- Pills Alpine.js clicáveis.
- Inativa: `border: 1px solid $border`, fundo `$bg-white`.
- Ativa: `background: $cor-*`, texto branco, `$shadow-sm`.
- Cards com `x-show` + `x-transition`.

### CTA Final de Página
- Fundo `$bg-dark` com círculo desfocado `$accent` opacity 0.06.
- Headline Cormorant Garamond `$text-5xl` branca.
- 2 botões: primary (`$cta`) e outline WhatsApp.
- Prova social: "12+ estados brasileiros atendidos".

### Footer
- Fundo `$primary`. Grid 4 colunas.
- Col 1: logo branco, tagline, social icons SVG.
- Col 2: links de navegação.
- Col 3: 5 categorias com bolinha colorida.
- Col 4: contato direto + botão WhatsApp.
- `border-top: 0.5px solid rgba(255,255,255,0.1)`.

### Timeline de Processo
- Barra vertical central: gradiente `$secondary → $accent`.
- Etapas em zig-zag com `scrub: 1` ScrollTrigger.
- Cards com border que ativa `$secondary` quando `.is-active`.
- Badges de duração em `$secondary` opacity 0.15.
- Checkmarks SVG na cor `$accent`.

---

## 8. HEALTH SCORE — CONTEXTO COMPLETO PARA O SITE

O Health Score é a métrica exclusiva da MarryMe e o maior diferencial
competitivo a ser comunicado no site.

**O que o visitante precisa entender:**
- É um número de 0 a 100 calculado automaticamente
- Mede a saúde real da campanha (não só o gasto)
- Calculado com 5 componentes ponderados
- Atualizado toda segunda-feira automaticamente
- Disponível no portal do cliente em tempo real

**Faixas para o site:**
- 80–100: Excelente — campanha otimizada, resultados acima da média
- 60–79: Bom — campanha saudável com espaço para melhorias
- 40–59: Atenção — pontos de melhoria identificados
- 0–39: Crítico — ação imediata necessária

**Como mostrar no site:**
- Arc SVG animado com cor dinâmica
- Breakdown dos 5 componentes (barras menores)
- Exemplo real: "Airton Sax — HS 72 — Bom"
- Badge "Exclusivo MarryMe" — nenhuma outra agência tem isso

---

## 9. PADRÕES DE DADOS (_data/)

### categorias.yml
```yaml
- id: musico
  nome: "Músico e Banda"
  slug: musico
  descricao: "Solos, duetos e bandas que fazem o casamento inesquecível"
  cor: "#C084FC"
  cor_light: "#F3E8FF"
  exemplos: ["Solo de violão", "Banda ao vivo", "Cantor gospel"]

- id: fotografo
  nome: "Fotógrafo e Videomaker"
  slug: fotografo
  descricao: "Registros que contam a história do dia mais especial"
  cor: "#F472B6"
  cor_light: "#FDF2F8"
  exemplos: ["Foto documental", "Drone", "Filme de casamento"]
```

### resultados.yml
```yaml
- label: "prestadores ativos"
  valor: 42
  sufixo: "+"
- label: "estados brasileiros"
  valor: 12
  sufixo: "+"
- label: "health score médio"
  valor: 58
  sufixo: ""
- label: "leads gerados"
  valor: 3200
  sufixo: "+"
```

### processo.yml
```yaml
- numero: 1
  titulo: "Onboarding"
  duracao: "Semana 1"
  descricao: "Entrevista completa, levantamento de materiais e análise estratégica"
  entregaveis:
    - "Checklist de informações preenchido"
    - "Análise estratégica de posicionamento"
    - "Direção criativa inicial"

- numero: 2
  titulo: "Planejamento de Metas"
  duracao: "Semanas 2-3"
  descricao: "Definição de CPL alvo, orçamento e metas de leads mensais"
  entregaveis:
    - "Metas de CPL por nicho"
    - "Orçamento mensal definido"
    - "Calendário de conteúdo"
```

---

## 10. INTEGRAÇÃO COM O BACKEND

O site Jekyll é estático — não consome a API Django diretamente.
O formulário de contato envia para a API via fetch no JavaScript:

```javascript
// assets/js/main.js
document.querySelector('#form-contato').addEventListener('submit', async (e) => {
  e.preventDefault();
  const dados = Object.fromEntries(new FormData(e.target));
  const res = await fetch('https://web-production-62d5c.up.railway.app/contato/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  });
  // mostrar feedback para o usuário
});
```

---

## 11. PERFORMANCE

- Hardware acceleration: só `transform` e `opacity`
- Z-index: topbar 201, navbar 200, dropdown 9999, hero 1, toast 500, WhatsApp 500
- `backdrop-filter` em pseudo-elemento `::before` (não no pai) para não quebrar z-index
- `font-display: swap` + preconnect `fonts.googleapis.com` e `fonts.gstatic.com`
- `loading="lazy"` em todas as imagens (exceto primeira de slideshow)
- SVG para ícones e logos, WebP para fotos
- `will-change` só no dropdown e animações contínuas
- `prefers-reduced-motion` verificado no início de cada script GSAP
- Scripts pesados só nas páginas que precisam via `extra_js` no front matter

---

## 12. PADRÕES PROIBIDOS (Anti-IA)

### Visual
- Sem glows neon (exceção: `$shadow-glow` no CTA hover)
- Sem preto puro — usar `$text-dark` (#1A1A2E)
- Sem gradientes em texto de headers grandes
- Sem sombras decorativas — marca usa bordas 0.5px
- Sem `border-radius` > 8px em cards (50px só em pills, 12px em dropdown)

### Tipografia
- Nunca Inter, Geist, Poppins ou qualquer outra fonte
- Nunca Cormorant Garamond no corpo, nav ou botões

### Layout
- Sem grids genéricos de 3 cards iguais quando DESIGN_VARIANCE > 4
  → usar magazine grid, zig-zag, grid assimétrico ou carrossel
- Padding e margins sempre pela escala `$spacing-*`

### Conteúdo
- Sem nomes genéricos — usar Airton Sax, Rony Ribeiro, Padre Beto,
  Kanirê Musical, Stella Ferreira
- Sem números fake — usar 42 prestadores, 12+ estados, HS 58
- Sem clichês — "Elevate", "Seamless", "Next-Gen", "Unleash" são proibidos
- Sem lorem ipsum — usar textos reais da MarryMe

### Técnico
- ANTI-EMOJI: nunca emojis em código, markup ou conteúdo
- Nunca arquivos `.md` para páginas — apenas `.html`
- Nunca animar `width`, `height`, `top`, `left`
- Nunca `!important` (exceção: `_animations.scss` para `prefers-reduced-motion`)

---

## 13. PRE-FLIGHT CHECK

Antes de entregar qualquer código, verificar:

- [ ] Todas as cores vêm de variáveis SCSS do `_variables.scss`?
- [ ] Cormorant Garamond só em headings e números de destaque?
- [ ] Plus Jakarta Sans em todo o resto?
- [ ] Mobile colapsa corretamente para coluna única?
- [ ] Hero usa `min-height` e nunca `height` fixo?
- [ ] Animações usam só `transform` e `opacity`?
- [ ] `prefers-reduced-motion` verificado no início do script GSAP?
- [ ] Imagens com `loading="lazy"` e `alt` descritivo?
- [ ] Nenhum `!important` (exceto `_animations.scss`)?
- [ ] Bordas `0.5px solid $border`, border-radius máx `8px` em cards?
- [ ] Novo partial SCSS criado e importado no `main.scss`?
- [ ] Script GSAP da página usa `extra_js` no front matter?
- [ ] Sliders usam padrão Alpine (`x-data` + `setInterval` + `is-active`)?
- [ ] Focus-visible em todos os elementos clicáveis?
- [ ] Z-index respeita hierarquia (topbar 201, navbar 200, dropdown 9999)?
- [ ] Health Score usa `$hs-*` corretas por faixa?
- [ ] Cards de categoria usam `$cor-*` e `$cor-*-light`?
- [ ] Nenhum emoji em código ou conteúdo?
- [ ] Dados reais (nomes reais, números reais da MarryMe)?
- [ ] CTA hover usa `$shadow-glow` e não outro shadow?
- [ ] Nenhum valor hardcoded de cor, fonte ou espaçamento?
- [ ] Imagens de prestadores com `object-position: center top`?
