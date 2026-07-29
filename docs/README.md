# Documentação técnica — AUDITOR

Índice de `docs/`. Documentação **durável** mora aqui; notas de trabalho, escopo e
estado moram em [`.continue/`](../.continue/); o contrato do comando/configuração
mora em [`SPEC.md`](../SPEC.md) na raiz; o prompt de runtime do produto mora em
[`prompts/`](../prompts/).

> ⚠️ O projeto está em **fase de proposta**. Não há implementação. O que estiver
> marcado como esqueleto ou pendente é exatamente isso — não trate como decidido.

---

## Nesta pasta

| Arquivo | O que é |
|---|---|
| [decisoes.md](decisoes.md) | **ADRs.** ADR-001 a ADR-009 (decisões fechadas) + tabela das 11 pendências abertas. Decisão nova entra aqui. |
| [revisao-inicial.md](revisao-inicial.md) | **Revisão de 2026-07-28.** 23 achados sobre a proposta, com a situação de cada um. Leitura recomendada antes de propor arquitetura. |
| [contrato-subagente.md](contrato-subagente.md) | **Parcial.** Especificação do contrato de entrada/saída do subagente, formato de achado, catálogo de modelos e adaptadores. |

## Fora desta pasta

| Arquivo | O que é |
|---|---|
| [../README.md](../README.md) | Proposta do produto: objetivo, escopo da v1, estrutura de `.auditor/`, fluxo de ciclo. |
| [../SPEC.md](../SPEC.md) | **Parcial.** Sintaxe canônica do comando e esquema de `config.yml` / `state.json`. |
| [../prompts/auditor-system.md](../prompts/auditor-system.md) | **Prompt de runtime** do subagente — o que a plataforma carrega ao executar a skill. Artefato do produto. |
| [../SECURITY.md](../SECURITY.md) | Modelo de ameaça (T-01 a T-08) e política do repositório. **Leitura obrigatória.** |
| [../version.md](../version.md) | Fonte de verdade da versão, gatilhos de bump e formato de commit. |
| [../CLAUDE.md](../CLAUDE.md) / [../AGENTS.md](../AGENTS.md) | Regras para quem **desenvolve** este repositório. Espelhados — editar os dois. |
| [../skill/README.md](../skill/README.md) | A skill para Claude Code: instalação, o que o gate garante e o que não garante. |
| [../schemas/](../schemas/) | JSON Schema de `config.yml`, `state.json` e da saída do ciclo. |
| [../tests/](../tests/) | 43 testes, sem dependência externa. `python3 -m unittest discover -s tests` |
| [../.continue/escopo-projeto.md](../.continue/escopo-projeto.md) | Fases F0–F6 — **proposta**, aguarda aprovação. |
| [../.continue/estado-atual.md](../.continue/estado-atual.md) | Onde o projeto está e o que vem a seguir. |
| [../.claude/README.md](../.claude/README.md) | Perfil de modelo e postura de permissões. |

---

## Por onde começar

- **Entender o produto** → `../README.md`, depois `decisoes.md`.
- **Vai propor arquitetura** → `revisao-inicial.md` primeiro. Os achados abertos já
  cobrem boa parte das armadilhas, e A-13 pode mudar o desenho inteiro.
- **Vai editar um arquivo de agente** → confira o alvo. `CLAUDE.md` + `AGENTS.md`
  (raiz, espelhados) são do **repositório**; `prompts/auditor-system.md` e
  `contrato-subagente.md` são do **produto**. Tabela em `../CLAUDE.md` (ADR-007).
- **Vai mexer em escrita, PR/issue ou scheduler** → `../SECURITY.md`, obrigatório.
- **Vai entregar** → `../version.md` (bump + changelog + formato de commit).

## Convenções

- Documentação deste repositório em **PT-BR**. Artefatos que o AUDITOR produz nos
  repos auditados em **en-US** (ver `../CLAUDE.md`).
- Documento novo aqui entra **neste índice** no mesmo commit.
- Sem link para arquivo inexistente: se é futuro, diga em texto, sem link.
- Distinga **fato observado**, **inferência** e **recomendação** — a mesma regra que
  o AUDITOR impõe aos repositórios que audita.
