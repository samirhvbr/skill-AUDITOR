# Estado atual — AUDITOR

- **2026-07-28 — nasce o repositório (pré-versionamento).** Commits `c66252c`
  (proposta), `ed330a9` (ajuste do README) e `1cd405a` (`AGENTS.md`, prompt de
  runtime do subagente). Remoto privado: `github.com/samirhvbr/AUDITOR`, branch
  `master`.

- **2026-07-28 — `0.1.0`: baseline de documentação + revisão.** Padrão da casa
  aplicado (`CLAUDE.md`, `version.md`, `SECURITY.md`, `.claude/`, `.continue/`,
  `docs/`, `.gitignore`), ADR-001 a ADR-006 registrando as decisões já fechadas, e a
  revisão inicial com **23 achados**.

- **2026-07-28 — `0.2.0`: correções aplicadas.** Fecha 18 dos 23 achados. Ainda sem
  implementação — tudo documentação.
  - **ADR-007** — arquivos de agente reorganizados: `AGENTS.md` (raiz) virou
    `prompts/auditor-system.md`, `AGENT.md` virou `docs/contrato-subagente.md`, e
    `CLAUDE.md` + `AGENTS.md` voltaram a ser espelhados como nos outros repos.
  - **ADR-008** — política de scheduler reescrita (substitui o ADR-004): mecanismo
    nativo primeiro, auto-instalação como último recurso, autorização do dono do
    repositório auditado.
  - **ADR-009** — conteúdo do repositório auditado é dado, nunca instrução.
  - Prompt de runtime reescrito com defesa contra conteúdo não confiável, formato de
    achado, regras de segredo, modo autônomo e no-op quiescente.
  - Divergências normativas reconciliadas: `open_pr_issue` como enum de três valores,
    `config.yml` em `.auditor/`, `index.md` em vez de `summary.md`, `auto_fix`
    removida.
  - `SPEC.md` e `docs/contrato-subagente.md` saíram de esqueleto para **parcial**.
  - `README.md` corrigido: id de modelo, eixo do scheduler, prompt injection,
    idioma, nomes.

- **2026-07-29 — `0.3.0`: primeiro código.** Sai da documentação pura.
  - **ADR-010** — `.auditor/` é **versionado** (decisão do Samir, resolve P-08), com
    as consequências propagadas: relatório vira artefato publicado, o AUDITOR não
    commita por padrão, e `state.json` precisa ser merge-friendly.
  - **Gate de escrita (T-03)** e **redação de segredos (T-01)** implementados e
    testados — os dois controles que transformam regra de prompt em controle real.
  - **JSON Schemas** de config, estado e saída do ciclo.
  - **43 testes**, sem dependência externa, cobrindo os dois sentidos.
  - Primeiro adaptador de plataforma: a skill para Claude Code em `skill/auditor/`.

---

## Onde o projeto está

**Desenho fechado, implementação parcial.** 10 ADRs, prompt de runtime escrito, três
esquemas, dois controles de segurança funcionando e testados.

⚠️ **Não existe executor. Nenhum ciclo completo já rodou de ponta a ponta.** O que
existe são as peças que o ciclo vai usar.

⚠️ **T-02 (prompt injection) continua sendo só regra escrita.** É a ameaça mais séria
do projeto e a única do trio que ainda não tem teste — falta o fixture com injeção
plantada. Enquanto ele não existir, a defesa é afirmação, não medição.

---

## Próximo passo

**O executor de um ciclo** (F2) — é o que falta para as peças virarem produto. Ele
depende de **P-09** (stack), a decisão que sobrou. Os controles já estão em Python 3
sem dependência externa, o que torna Python o caminho de menor atrito, mas isso não
decide a stack do executor.

Com o executor:

1. Rodar um ciclo real num repositório-fixture e ver o esquema reprovar uma saída
   quebrada — é o critério de pronto da F1, hoje não atendido por falta de validador.
2. Escrever o **fixture de injeção plantada** (T-02) e o de **segredo plantado** num
   ciclo de verdade, não só na função.
3. Dogfooding: rodar o AUDITOR neste próprio repositório.

---

## Também em aberto

- **A-13 / F0** — as primitivas do **ShvIA** seguem como inferência. O Claude Code
  está confirmado e a skill foi construída sobre ele.
- **Âncora do `hash`** de achado: precisa sobreviver a mudança de número de linha,
  senão a dedup quebra a cada edição e o mesmo achado vira issue novo.
- **P-02** (escopo), **P-05** (retenção — pesa mais agora que o relatório é
  versionado), **P-10** (licença), **P-11** (gatilho por relógio ou por atividade).

---

## Contexto de ambiente

- `~/x` tem processo automático que commita e pusha o working tree
  (`Version X (clean)`). Conferir `git log` antes de assumir entrega registrada —
  na `0.1.0` um commit chegou ao `origin` no meio da entrega.
- **Nunca** reescrever histórico aqui: o `git pull --rebase` do processo desfaz.
- Remoto por SSH, então não precisa da ponte `gh` para push.
