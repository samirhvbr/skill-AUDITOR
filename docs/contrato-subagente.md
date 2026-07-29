# Contrato do subagente AUDITOR

> ⚠️ **ESQUELETO.** Este arquivo é o destino canônico do contrato de entrada/saída
> do subagente, das regras de prompt e do catálogo de modelos por plataforma.
>
> Preencher é a fase **F1** ([../.continue/escopo-projeto.md](../.continue/escopo-projeto.md)),
> e depende da validação de plataforma da fase **F0**. Ao preencher uma seção,
> remover a marca e bumpar `version.md`.
>
> **Este arquivo é a especificação; o [`prompts/auditor-system.md`](../prompts/auditor-system.md)
> é o runtime** — o prompt que a plataforma carrega ao executar a skill. Os dois
> falam do mesmo subagente em níveis diferentes:
>
> | | `prompts/auditor-system.md` | este arquivo |
> |---|---|---|
> | Nível | **runtime** — o prompt em si | **especificação** — o contrato formal |
> | Público | o subagente, em execução | quem implementa e testa o AUDITOR |
> | Estado | escrito | esqueleto |
>
> Enquanto este arquivo for esqueleto, o que estiver **escrito** no prompt de
> runtime prevalece. Até a `0.1.0` os dois se chamavam `AGENTS.md` e `AGENT.md`,
> separados por uma letra — resolvido no ADR-007.

---

## 1. Papel

`documentation-auditor`: subagente que audita **cobertura de documentação** de
mudanças recentes. Lê código, testes, configuração, histórico e documentação
existente; escreve documentação durável em `.auditor/`; **não altera a lógica da
aplicação auditada**.

---

## 2. Prompt de sistema

O prompt vive em [`prompts/auditor-system.md`](../prompts/auditor-system.md) e é
normativo. As três lacunas que a revisão apontou foram fechadas na `0.2.0`:

| Item | Situação |
|---|---|
| Conteúdo não confiável como **dado, nunca instrução**, com lista fechada de arquivos obedecidos que só podem restringir (A-03 / T-02 / ADR-009) | ✅ escrito |
| Formato obrigatório de evidência (A-12) | ✅ escrito — ver §4 |
| Comportamento em modo autônomo: degrada para **não fazer**, nunca para "fazer assim mesmo" (A-06) | ✅ escrito |

⛔ **Falta:** validar o prompt na prática (fase F2) e adaptá-lo por plataforma
quando §6 fechar. Prompt escrito não é prompt testado.

---

## 3. Contrato de saída

Esquema formal: [`schemas/cycle-report.schema.json`](../schemas/cycle-report.schema.json).

Saída fora do esquema = **ciclo falhou**. Sem essa regra, o esquema é decoração.

Além dos campos, o esquema carrega três regras condicionais que não caberiam em
prosa:

- `kind: observed` **exige** `file` e `line` — é o que torna "não invente"
  verificável (A-12).
- `range.mode: time-window` **exige** `degraded_reason` — degradação silenciosa por
  checkpoint órfão fica impossível de representar.
- `status: no-op` **proíbe** achados e artefatos — o ciclo quiescente não pode
  "acidentalmente" escrever.

E `artifacts_written` só aceita caminho começando em `.auditor/`: escrita fora do
escopo não é representável numa saída válida.

Campos:

| Campo | Conteúdo |
|---|---|
| `cycle_id` | identificador do ciclo |
| `interval` | intervalo configurado |
| `model` | modelo efetivamente usado (não o solicitado — ver §5) |
| `range` | período ou commits analisados |
| `files_inspected` | arquivos inspecionados |
| `changes` | mudanças encontradas |
| `findings[]` | lacunas de documentação (ver §4) |
| `artifacts_written` | arquivos criados/atualizados em `.auditor/` |
| `limitations` | limitações e degradações do ciclo |
| `pending_decisions` | itens que exigem decisão do usuário |
| `next_checkpoint` | próximo ponto de partida |
| `cost` | custo e duração do ciclo (T-07) |
| `status` | `completed` · `no-op` · `partial` · `failed` |

⛔ **Falta o validador em runtime.** A biblioteca `jsonschema` não é dependência do
projeto (**P-09**), então nada valida instância contra o esquema hoje. O critério de
pronto da fase F1 — "um relatório de exemplo valida e um quebrado é rejeitado" —
**não está atendido**. `tests/test_schemas.py` cobre a estrutura do esquema, não a
validação.

---

## 4. Formato de finding

Campos obrigatórios — fechado em `0.2.0`, espelhado no prompt de runtime e no
esquema:

| Campo | Conteúdo |
|---|---|
| `kind` | `observed` · `inferred` · `recommended` |
| `file` | caminho relativo |
| `line` | linha ou faixa |
| `commit` | commit onde a mudança apareceu |
| `hash` | hash estável para dedup entre ciclos (A-10 / T-06) |
| `summary` | uma frase |

Regras:

- `kind: observed` **sem** `file:line` é inválido — o ciclo rejeita.
- Finding sobre segredo reporta **localização, nunca o valor** (T-01).
- `hash` estável = tipo + caminho + âncora. É o que impede o mesmo issue de ser
  aberto 48 vezes por dia.

Formalizado em `$defs.finding` de
[`schemas/cycle-report.schema.json`](../schemas/cycle-report.schema.json), com a
regra de `observed` como condicional `if/then` — coberta por
`test_observed_finding_requires_file_and_line`.

⛔ **Falta:** a definição exata de "âncora" no cálculo do `hash`. Precisa sobreviver a
mudança de número de linha, senão a dedup quebra a cada edição do arquivo e o mesmo
achado vira issue novo.

---

## 5. Catálogo de modelos

⛔ **Bloqueado por P-01.** Precisa listar, por plataforma, os identificadores
válidos e a cadeia de fallback.

Identificadores da família Claude, para referência: `claude-opus-5`,
`claude-sonnet-5`, `claude-fable-5` e `claude-haiku-4-5-20251001`. Os exemplos do
`README.md` usam `claude-sonnet-5` desde a `0.2.0` — antes traziam
`claude-sonnet-4.6`, que não existe (A-01).

Regra que já vale: o identificador é uma **solicitação do usuário**, não garantia de
disponibilidade. A skill valida e, se cair em fallback, **informa** — e a saída
reporta o modelo efetivamente usado, não o pedido.

---

## 6. Adaptadores de plataforma

⛔ **Bloqueado por P-07 e pela validação de F0.**

### 6.1 Claude — **implementado** em [`skill/auditor/`](../skill/auditor/)

As cinco primitivas de que o AUDITOR precisa **existem** no Claude Code — skills,
subagentes, hooks, execução recorrente por intervalo e rotinas agendadas (ADR-008).
O adaptador monta sobre elas, sem inventar scheduler e sem instalar persistência.

| Peça | Como se declara | Situação |
|---|---|---|
| Skill | `SKILL.md` com frontmatter (`name`, `description`, `allowed-tools`) em `.claude/skills/<nome>/` | ✅ `skill/auditor/SKILL.md` |
| Gate de escrita (T-03) | hook `PreToolUse` no `.claude/settings.json`; nega com **exit 2** e motivo no stderr | ✅ `skill/auditor/hooks/write-gate.py` |
| Redação de segredos (T-01) | biblioteca chamada antes de qualquer escrita | ✅ `skill/auditor/lib/redact.py` |
| Agendamento | rotina agendada / execução recorrente da plataforma | ⛔ falta declarar |
| Subagente | arquivo em `.claude/agents/` | ⛔ falta declarar |

⛔ **Falta:** o formato exato do arquivo de subagente e do registro da rotina
agendada, com evidência (arquivo, comando, saída) — não de memória.

### 6.2 ShvIA

⛔ A preencher. Plataforma da casa (ADR-002): o que faltar pode ser implementado do
lado do servidor — prompt de sistema, contrato de saída, gates de escrita, scheduler.
Gateway `ai.shvia.org`; código em `~/x/SHVIA/SHVIA-WEB`.

⚠️ Controlar a plataforma **não** é controlar o repositório auditado (A-02): o
runner pode ser nosso e o alvo, de terceiro.

### 6.3 Divergências

⛔ A preencher. Diferença entre plataformas é **documentada**, não escondida atrás de
um "deve funcionar igual".

---

## 7. Não pertence a este arquivo

- O prompt em si → [`prompts/auditor-system.md`](../prompts/auditor-system.md).
- Sintaxe do comando e esquema de configuração → [`SPEC.md`](../SPEC.md).
- Ameaças e controles → [`SECURITY.md`](../SECURITY.md).
- Decisões e pendências → [`decisoes.md`](decisoes.md).
