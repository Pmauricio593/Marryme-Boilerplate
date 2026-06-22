---
name: marryme-sessao-engenharia
description: Conduz sessões do plano MarryMe (docs/engenharia/00-PLANO-EXECUCAO.md). Use ao implementar marcos de engenharia, revisar PRs ou quando o usuário mencionar checklist, sessão, DoD ou make lint.
---

# Skill — Sessão de Engenharia MarryMe

## Antes de codar

1. Leia a sessão em `docs/engenharia/00-PLANO-EXECUCAO.md`
2. Leia `docs/engenharia/01-PADROES-CODIGO.md` se tocar arquitetura
3. Confira `CHECKLIST_PRODUCAO.md` na raiz — marque `[~]` no item em andamento
4. Diagnostique o código real (não assuma)

## Template de prompt

```text
CONTEXTO: Sessão X.Y do 00-PLANO-EXECUCAO.md
OBJETIVO: <copiar da sessão>
ESCOPO: <arquivos exatos>
RESTRIÇÕES: sem lógica fora do escopo; View→Service; sem secrets; portal via VinculoPrestador
DoD: <copiar da sessão>
Ao terminar: make lint && make test
```

## Comandos (em backend/)

```bash
make up
make lint
make format
make test
make cov
make migrate
```

## Revisão humana (não pular)

- [ ] Escopo respeitado?
- [ ] View fina, regra no service?
- [ ] Sem secret / sem stack trace?
- [ ] Testes: feliz + 403 + 400?
- [ ] make lint && make test verdes?
- [ ] Atualizar CHECKLIST_PRODUCAO.md com [x] após validação do usuário

## Antipadrões

- Refatoração ampla fora da sessão
- Prospecção/Apify
- alert() no frontend
- Afrouxar asserção de teste para passar
- Inventar endpoints ou dados

## Divisão de ferramentas

- Mudança local/tela → Cursor
- Estrutural (settings split, CI, migrations) → agente com terminal
- Iterar testes até verde → terminal

## Ao concluir sessão

1. Liste o que mudou
2. Peça validação do usuário no CHECKLIST_PRODUCAO.md
3. Sugira mensagem Conventional Commit (não commitar sem pedido)
