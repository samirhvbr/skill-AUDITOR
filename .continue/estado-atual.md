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

---

## Onde o projeto está

**Proposta consolidada, zero implementação.** O desenho conceitual está fechado e
coerente: 9 ADRs, o prompt de runtime escrito, o esquema de estado e a estrutura de
`.auditor/` definidos.

⚠️ **"Decidido e escrito" não é "implementado".** As três ameaças que bloqueiam uso
real — conteúdo não confiável (T-02), gate de escrita (T-03) e redação de segredos
(T-01) — têm regra escrita e **nenhum** controle mecânico. Regra no prompt reduz a
chance de o modelo errar; não impede.

---

## Próximo passo (bloqueia o desenho)

**Validar as primitivas do ShvIA** — fase F0, achado A-13.

O ADR-008 se apoia em o Claude Code oferecer as cinco primitivas de que o AUDITOR
precisa (skills, subagentes, hooks, execução recorrente, rotinas agendadas), o que
está confirmado. **O equivalente no ShvIA segue como inferência.** Falta também
documentar *como* cada primitiva se declara no Claude Code — com evidência (arquivo,
comando, saída), não de memória.

Sem isso, o adaptador de plataforma (P-07) não fecha e o executor não tem alvo.

---

## Depois disso, na ordem

1. **A-11** — JSON Schema da saída do ciclo. Os campos estão fixados; falta o
   esquema formal, que é o que torna todo o resto testável.
2. **P-08** — `.auditor/` versionado, ignorado ou híbrido. É o que falta para fechar
   o esquema do `state.json`.
3. **P-09** — stack do executor, e então o ciclo manual reproduzível (F2).
4. **F3 — controles de segurança.** Redação de segredos, gate de escrita fora do
   modelo e fixtures de injeção e de segredo plantado. **Bloqueia qualquer execução
   em repositório que não seja de teste.**
5. Definir a "âncora" do `hash` de achado, que precisa sobreviver a mudança de número
   de linha — senão a dedup quebra a cada edição.

---

## Decisões que precisam do Samir

Não escolher por conta própria — cada uma muda o produto:

- **P-08** — `.auditor/` versionado, ignorado ou híbrido.
- **P-09** — stack do executor/harness (Python, Node, Rust, shell).
- **P-10** — licença e formato de distribuição (define se o repo vira público).
- **P-11** — gatilho por relógio, por atividade (hook) ou os dois.
- **P-02** — escopo: repositório inteiro ou só mudanças versionadas em Git.

---

## Contexto de ambiente

- `~/x` tem processo automático que commita e pusha o working tree
  (`Version X (clean)`). Conferir `git log` antes de assumir entrega registrada —
  na `0.1.0` um commit chegou ao `origin` no meio da entrega.
- **Nunca** reescrever histórico aqui: o `git pull --rebase` do processo desfaz.
- Remoto por SSH, então não precisa da ponte `gh` para push.
