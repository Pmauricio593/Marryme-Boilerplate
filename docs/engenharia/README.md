# docs/engenharia — Plano para o nível Sábio (MarryMe Backend)

Conjunto de documentos para levar o backend MarryMe ao nível profissional sênior, executável ao longo dos dias com Cursor e Claude Code.

## Onde colocar no repo
Copie para `backend/docs/engenharia/` (ou `docs/engenharia/` na raiz do monorepo). Os arquivos de regra de IA vão na **raiz**:
- `CLAUDE.md` → raiz do repo (lido pelo Claude Code)
- `.cursorrules` → raiz do repo (lido pelo Cursor)

## Arquivos
| Arquivo | O que é |
|---------|---------|
| `00-PLANO-EXECUCAO.md` | **Plano mestre.** Modelo de níveis (Aprendiz→Sábio), diagnóstico, 8 marcos, sessões passo a passo com comandos, DoD e commits. Comece por aqui. |
| `01-PADROES-CODIGO.md` | Padrões de arquitetura, imports, services/selectors, models, testes, git. O "como" do código. |
| `02-OPERACAO-IA.md` | Como conduzir as sessões com Cursor + Claude Code: divisão de trabalho, prompts prontos, revisão, antipadrões. |
| `03-REFERENCIAS.md` | Bibliografia que fundamenta cada decisão, com mapa lacuna→leitura. |
| `CLAUDE.md` | Regras funcionais para o Claude Code (vai na raiz). |
| `.cursorrules` | Regras funcionais para o Cursor (vai na raiz). |

## Como usar
1. Leia `00` e o diagnóstico (lacunas L1–L11).
2. Execute uma sessão por vez (= 1 PR). Marque o DoD.
3. Apoie-se em `01` (padrões) e `02` (prompts) durante a sessão.
4. Avance os níveis: Praticante → Profissional → Especialista → Sábio.

> Estes docs respeitam `CURSOR_CONTEXT_MARRYME.md` e `SKILL_MARRYME.md` como fontes de verdade e não as contradizem.
