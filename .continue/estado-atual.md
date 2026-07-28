# Estado atual — AUDITOR

- **2026-07-28 — nasce o repositório (pré-versionamento).** Commits `c66252c`
  (proposta), `ed330a9` (ajuste do README) e `1cd405a` (`AGENTS.md`, prompt de
  runtime do subagente). Decisões fechadas na proposta: plataformas Claude + ShvIA
  (OpenAI fora), PR/issue permitido, auto-instalação de scheduler, sintaxe do
  comando, intervalo com unidade obrigatória. Remoto privado:
  `github.com/samirhvbr/AUDITOR`, branch `master`.

- **2026-07-28 — `0.1.0`: baseline de documentação + revisão.** Nenhuma
  implementação; documentação, configuração do agente e revisão do que existe.
  - Padrão da casa aplicado: `CLAUDE.md`, `version.md` (fonte de verdade + formato
    de commit), `SECURITY.md`, `.claude/`, `.continue/`, `docs/`, `.gitignore`.
  - **Desvio consciente do padrão:** sem espelhamento `CLAUDE.md` ↔ `AGENTS.md`.
    Aqui o `AGENTS.md` é do **produto** (prompt de runtime), não do repositório.
  - `docs/decisoes.md` — ADR-001 a ADR-006 registram as decisões fechadas; tabela
    com **12 pendências** (P-01 a P-12) + divergências normativas abertas.
  - `docs/revisao-inicial.md` — **23 achados** (A-01 a A-23), 6 de severidade alta.
  - `SPEC.md` e `AGENT.md` criados como **esqueletos** (eram links quebrados no
    README, citados 5 vezes).
  - `.continue/escopo-projeto.md` — fases F0–F6, **proposta**, aguarda aprovação.
  - ⚠️ O `AGENTS.md` do commit `1cd405a` chegou ao `origin` no meio desta entrega,
    foi sobrescrito por engano e **restaurado verbatim**. Nada perdido — e virou o
    achado A-19.

---

## Onde o projeto está

**Proposta madura, zero implementação.** O desenho conceitual está coerente e o
escopo da v1 (auditar e documentar, sem tocar na aplicação) é a escolha certa. O que
falta não é código — é **fechar contrato**: sintaxe, esquema de configuração,
esquema de saída do subagente e modelo de estado.

---

## Primeiro passo (rápido, e já está causando dano)

**Reconciliar `AGENTS.md` com o `README.md`** — A-19 a A-23. Os dois são normativos
e já discordam em quatro pontos: tipo de `open_pr_issue` (booleano vs
`off`/`ask`/`always`), local do `config.yml` (raiz vs `.auditor/`), nome do resumo
cumulativo (`summary.md` vs `index.md`) e a chave `auto_fix` — que não existe no
README e habilita justamente o que a v1 proíbe.

Some-se a isso `AGENTS.md` e `AGENT.md` diferindo por uma letra (P-12). Enquanto os
dois coexistirem assim, cada edição reproduz o problema — foi o que aconteceu nesta
própria entrega.

---

## Passo que desbloqueia o desenho

**Validar o achado A-13** — o Claude Code já oferece as cinco primitivas de que o
AUDITOR precisa (skills, subagentes, hooks, `/loop`, rotinas agendadas)?

A resposta decide o desenho:

- **Se sim** — o AUDITOR é montado sobre mecanismo nativo. Auto-instalação de
  scheduler (ADR-004, hoje **em revisão**) cai de política padrão para último
  recurso, e boa parte do risco de segurança do projeto some junto.
- **Se não** — ADR-004 continua valendo, mas precisa ser reescrito com o eixo
  correto do achado A-02: quem autoriza persistência é o dono do
  repositório/máquina alvo, não o autor da plataforma.

É uma validação empírica, de uma sessão. Tudo em A-13 e A-01 hoje é **inferência**
a partir de documentação — precisa de confirmação antes de virar decisão.

---

## Depois disso, na ordem

0. **A-19 / P-12** — consolidar `AGENTS.md` e `AGENT.md` (ver primeiro passo).
1. **A-03 / A-04 / A-05** — transformar regra de prompt em controle real (conteúdo
   não confiável, enforcement de `write_policy`, redação de segredos). Bloqueiam
   qualquer execução em repositório que não seja de teste.
2. **A-11 / A-12** — JSON Schema da saída do ciclo e formato de evidência
   (`file`/`line`/`commit`/`kind`). É o que torna o resto testável.
3. **P-08 / A-08 / A-09** — modelo de estado: `.auditor/` versionado ou não, e
   checkpoint que sobrevive a rebase/squash/force-push. Barato agora, caro depois.
4. **A-01 / A-15 / A-16 / A-18** — correções de texto no `README.md` (id de modelo
   inválido, ambiguidade de idioma, links, nome da skill).

---

## Decisões que precisam do Samir

Não escolher por conta própria — cada uma muda o produto:

- **P-08** — `.auditor/` versionado, ignorado ou híbrido.
- **P-09** — stack do executor/harness (Python, Node, Rust, shell).
- **P-10** — licença e formato de distribuição (define se o repo vira público).
- **P-11** — gatilho por relógio, por atividade (hook) ou os dois.
- **P-12** — consolidar `AGENTS.md` e `AGENT.md`: renomear o de runtime para
  `prompts/auditor-system.md` (e devolver `AGENTS.md` ao padrão da casa), ou manter
  o `AGENTS.md` e absorver o `AGENT.md` dentro do `SPEC.md`.
- **ADR-004** — depende de A-13; até validar, auto-instalação fica desligada.

---

## Contexto de ambiente

- `~/x` tem processo automático que commita e pusha o working tree
  (`Version X (clean)`). Conferir `git log` antes de assumir entrega registrada.
  **Nunca** reescrever histórico aqui — o `git pull --rebase` do processo desfaz.
- Push por HTTPS usa a ponte do `gh`:
  `git -c credential.helper='!gh auth git-credential' push`. Este repo usa remoto
  SSH, então não precisa.
