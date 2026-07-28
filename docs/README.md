# Documentação técnica — AUDITOR

Índice de `docs/`. Documentação **durável** mora aqui; notas de trabalho, escopo e
estado moram em [`.continue/`](../.continue/); contratos normativos moram na raiz
(`SPEC.md`, `AGENT.md`).

> ⚠️ O projeto está em **fase de proposta**. Não há implementação. O que estiver
> marcado como esqueleto ou pendente é exatamente isso — não trate como decidido.

---

## Nesta pasta

| Arquivo | O que é |
|---|---|
| [decisoes.md](decisoes.md) | **ADRs.** ADR-001 a ADR-006 (decisões fechadas) + tabela das 12 pendências abertas + divergências normativas. Decisão nova entra aqui. |
| [revisao-inicial.md](revisao-inicial.md) | **Revisão de 2026-07-28.** 23 achados sobre a proposta, com prioridade sugerida. Leitura recomendada antes de propor arquitetura. |

## Fora desta pasta

| Arquivo | O que é |
|---|---|
| [../README.md](../README.md) | Proposta do produto: objetivo, escopo da v1, estrutura de `.auditor/`, fluxo de ciclo. |
| [../SPEC.md](../SPEC.md) | **Esqueleto.** Sintaxe canônica do comando e esquema de `config.yml` / `state.json`. |
| [../AGENT.md](../AGENT.md) | **Esqueleto.** Especificação do contrato de entrada/saída do subagente, catálogo de modelos e fallbacks. |
| [../SECURITY.md](../SECURITY.md) | Modelo de ameaça (T-01 a T-08) e política do repositório. **Leitura obrigatória.** |
| [../version.md](../version.md) | Fonte de verdade da versão, gatilhos de bump e formato de commit. |
| [../CLAUDE.md](../CLAUDE.md) | Regras para quem **desenvolve** este repositório. |
| [../AGENTS.md](../AGENTS.md) | Prompt de entrada do subagente AUDITOR em **runtime** — é do produto, não do repositório. ⚠️ Não é espelho do `CLAUDE.md` como nos outros repos da casa (achado A-19). |
| [../.continue/escopo-projeto.md](../.continue/escopo-projeto.md) | Fases F0–F6 — **proposta**, aguarda aprovação. |
| [../.continue/estado-atual.md](../.continue/estado-atual.md) | Onde o projeto está e o que vem a seguir. |
| [../.claude/README.md](../.claude/README.md) | Perfil de modelo e postura de permissões. |

---

## Por onde começar

- **Entender o produto** → `../README.md`, depois `decisoes.md`.
- **Vai propor arquitetura** → `revisao-inicial.md` primeiro. Os achados abertos já
  cobrem boa parte das armadilhas, e A-13 pode mudar o desenho inteiro.
- **Vai editar um arquivo de agente** → confira o alvo. São **três** com papéis
  distintos (`CLAUDE.md`, `AGENTS.md`, `../AGENT.md`) e dois deles diferem por uma
  letra. Tabela em `../CLAUDE.md`; consolidação pendente em P-12.
- **Vai mexer em escrita, PR/issue ou scheduler** → `../SECURITY.md`, obrigatório.
- **Vai entregar** → `../version.md` (bump + changelog + formato de commit).

## Convenções

- Documentação deste repositório em **PT-BR**. Artefatos que o AUDITOR produz nos
  repos auditados em **en-US** (ver `../CLAUDE.md`).
- Documento novo aqui entra **neste índice** no mesmo commit.
- Sem link para arquivo inexistente: se é futuro, diga em texto, sem link.
- Distinga **fato observado**, **inferência** e **recomendação** — a mesma regra que
  o AUDITOR impõe aos repositórios que audita.
