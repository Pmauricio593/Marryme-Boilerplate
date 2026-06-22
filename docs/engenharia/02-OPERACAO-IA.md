# Operação com IA — Cursor + Claude Code

> Como conduzir as sessões do `00-PLANO-EXECUCAO.md` usando **Cursor** e **Claude Code** sem perder o controle do código. A IA é um par de programação sênior: rápido, mas que precisa de contexto, limites e revisão humana. Este guia padroniza isso.

---

## 1. Princípio: a IA executa o plano, você dirige

- O plano (`00`), os padrões (`01`) e as fontes de verdade (`CURSOR_CONTEXT`, `SKILL`) são o **contrato**. A IA implementa dentro dele.
- Você (humano) decide *o quê* e *quando*; a IA acelera o *como*.
- **Toda mudança passa por revisão humana antes do merge.** A IA nunca dá merge sozinha.
- Sessão = 1 PR. Não deixe a IA "ir embora" fazendo 5 coisas; puxe-a de volta ao escopo da sessão.

---

## 2. Setup inicial (uma vez)

1. Coloque os arquivos de regra na raiz do repo:
   - `CLAUDE.md` (lido automaticamente pelo Claude Code).
   - `.cursorrules` (lido automaticamente pelo Cursor).
   - (Ambos foram gerados junto com este plano — ver pasta de entrega.)
2. Mantenha `CURSOR_CONTEXT_MARRYME.md`, `SKILL_MARRYME.md` e `docs/engenharia/` versionados — são o contexto que a IA lê.
3. No Cursor, fixe (`@`) os arquivos relevantes da sessão no chat: o `00-PLANO` na sessão atual, o `01-PADROES`, e os arquivos que vão mudar.

---

## 3. Divisão de trabalho: quando usar cada um

| Tarefa | Ferramenta recomendada | Por quê |
|--------|------------------------|---------|
| Edição cirúrgica em arquivo aberto, autocomplete | **Cursor** (inline + Cmd-K) | Feedback visual imediato, diff inline. |
| Mudança que cruza vários arquivos (ex.: converter `services.py` em pacote) | **Claude Code** (terminal, agente) | Navega o repo, roda comandos, aplica em lote. |
| Rodar testes/lint e iterar até passar | **Claude Code** | Executa `make test`, lê a saída, corrige. |
| Revisar um diff / explicar código legado | Qualquer um | Ambos leem o contexto. |
| Gerar testes a partir de um service | **Claude Code** com `01-PADROES` fixado | Segue o padrão de testes. |

> Regra prática: **mudança local → Cursor; mudança estrutural → Claude Code.**

---

## 4. Anatomia de um bom prompt de sessão

Sempre inclua, nesta ordem: **objetivo + escopo + restrições + critério de aceite**.

Template:

```text
CONTEXTO: Estamos na Sessão X.Y do docs/engenharia/00-PLANO-EXECUCAO.md.
Leia também docs/engenharia/01-PADROES-CODIGO.md e respeite CURSOR_CONTEXT_MARRYME.md.

OBJETIVO: <copie o "Objetivo" da sessão>

ESCOPO (só isto): <liste os arquivos a tocar>

RESTRIÇÕES:
- Não mude lógica de negócio fora do escopo.
- Não exponha secrets; não vaze stack trace.
- Siga o padrão View->Service->Integration->Model->Task.
- PR pequeno; me mostre o diff antes de aplicar mudanças amplas.

CRITÉRIO DE ACEITE (DoD): <copie o DoD da sessão>

Ao terminar: rode `make lint` e `make test` e me mostre o resultado.
```

---

## 5. Prompts prontos por marco

**Marco 0 — qualidade**
> "Aplique a config de ruff/black/pre-commit da Sessão 0.1. Rode os formatters e me mostre o diff agrupado por tipo. Não altere lógica; se um autofix mudar comportamento, reverta e aponte o trecho."

**Marco 1 — LOGGING (a lacuna mais urgente)**
> "Implemente a Sessão 1.1: adicione o dict LOGGING. Depois faça `grep -rn 'getLogger' backend/` e confirme que todo logger usa o prefixo 'marryme.'. Suba o servidor e me mostre uma linha de log de um login para provar que funciona."

**Marco 2 — testes**
> "Implemente a Sessão 2.3: escreva testes de Health Score para o app campanhas seguindo docs/engenharia/01-PADROES-CODIGO.md (seção Testes). Mocke MetaAdsClient e o cliente Claude — zero rede. Teste os limiares 39/40/69/70. Rode `make cov` e me diga a cobertura do app."

**Marco 3 — arquitetura**
> "Implemente a Sessão 3.2 só para o app prestadores: converta services.py em pacote services/ com um arquivo por caso de uso, mantendo a API pública igual (atualize imports). Rode os testes do Marco 2 e prove que continuam verdes. Não mude comportamento."

**Marco 6 — performance**
> "Sessão 6.2: instale django-debug-toolbar em dev, identifique N+1 nas listas de prestadores e sessões, e corrija com select_related/prefetch_related nos selectors. Me mostre nº de queries antes e depois."

**Marco 7 — segurança**
> "Sessão 7.1: escreva testes que provem que um usuário role='prestador' vinculado ao Prestador A recebe 403/404 ao tentar ler campanhas/roteiros/perfil do Prestador B. Se algum endpoint vazar, aponte o get_queryset culpado antes de corrigir."

---

## 6. Revisão do que a IA produziu (não pule)

Antes de aceitar qualquer diff, confira:

1. **Escopo:** mudou só o que a sessão pedia? Arquivo a mais = bandeira vermelha.
2. **Padrão:** segue o `01-PADROES`? (view fina, regra no service, import correto)
3. **Segurança:** nenhum secret, nenhum `prestador_id` confiado do cliente, nenhum stack trace.
4. **Testes:** vieram junto? Cobrem 403/400 além do caso feliz?
5. **Comportamento:** `make test` verde? Se a IA "consertou" um teste afrouxando a asserção, rejeite.
6. **Migrations:** se mexeu em model, gerou migration? Você leu a migration?

> Heurística: se você não entende uma linha que a IA escreveu, **não faça merge** — peça para ela explicar ou simplificar. Código que você não entende é dívida.

---

## 7. Antipadrões (o que NÃO deixar a IA fazer)

- Refatoração ampla "de brinde" fora do escopo da sessão (proibido pelo `CURSOR_CONTEXT`).
- Criar arquivos `.md` novos sem necessidade (regra do `SKILL`).
- Trocar a tipografia/cores fora dos tokens do `SKILL` (Cormorant Garamond + Plus Jakarta Sans).
- Adicionar dependência pesada sem justificar (cada lib nova entra no `requirements` certo e idealmente num ADR).
- Construir prospecção/Apify (fora de foco nesta fase).
- "Consertar" teste removendo a asserção.
- Inventar endpoints/dados que não existem — validar contra o código real.

---

## 8. Ritual de sessão (passo a passo operacional)

1. `git switch -c <tipo>/<sessao>` (ex.: `git switch -c feat/logging`).
2. Abra a sessão no `00-PLANO`. Fixe os arquivos no Cursor/Claude Code.
3. Cole o prompt da seção 4/5, ajustado à sessão.
4. Revise o diff (seção 6).
5. `make lint && make test`.
6. Marque o DoD. Se algo falhar, **a sessão não acabou.**
7. Commit (Conventional Commits) + abra PR + descreva qual lacuna fecha.
8. Atualize o checklist de níveis no `00-PLANO` se concluiu um marco.

---

## 9. Quando a IA travar

- **Erro que não some:** peça o stack completo + a hipótese dela antes da correção ("explique a causa antes de corrigir").
- **Mudança grande demais:** quebre a sessão em duas. PR menor.
- **Ela perdeu o contexto:** recoloque (`@`) o `00`, `01` e `CURSOR_CONTEXT`. Resuma o estado em 3 linhas.
- **Discordância de padrão:** o `01-PADROES` vence. Se o padrão estiver errado, abra um ADR — não improvise no PR.
