# AGENT.md — Contrato do subagente AUDITOR

> ⚠️ **ESQUELETO.** Este arquivo é o destino canônico do contrato de entrada/saída
> do subagente, do prompt e do catálogo de modelos por plataforma — prometido no
> `README.md` mas ainda **não especificado**.
>
> Preencher é a fase **F1** ([.continue/escopo-projeto.md](.continue/escopo-projeto.md)),
> e depende da validação de plataforma da fase **F0**. Ao preencher uma seção,
> remover a marca e bumpar `version.md`.
>
> ⚠️ **Não confundir com [AGENTS.md](AGENTS.md)** (plural). Os dois falam do mesmo
> subagente, em níveis diferentes:
>
> | | `AGENTS.md` | `AGENT.md` (este) |
> |---|---|---|
> | Nível | **runtime** — o prompt que a plataforma lê antes de executar a skill | **especificação** — o contrato formal |
> | Público | o subagente, em execução | quem implementa e testa o AUDITOR |
> | Estado | escrito, em proposta | esqueleto |
>
> Nomes quase idênticos com escopos sobrepostos são um convite a editar o arquivo
> errado. Consolidar os dois é a pendência **P-12** (achado A-19). Enquanto não se
> decide, o que estiver **escrito** no `AGENTS.md` prevalece sobre o esqueleto daqui
> — e toda divergência entre eles está listada nos achados A-20 a A-23.

---

## 1. Papel

`documentation-auditor`: subagente que audita **cobertura de documentação** de
mudanças recentes. Lê código, testes, configuração, histórico e documentação
existente; escreve documentação durável em `.auditor/`; **não altera a lógica da
aplicação auditada**.

---

## 2. Prompt de sistema

Rascunho no `README.md` §Contrato de execução do subagente. **Não usar como está** —
faltam três coisas que a [revisão](docs/revisao-inicial.md) apontou:

- ⛔ **Delimitação de conteúdo não confiável** (A-03 / T-02). O prompt precisa
  estabelecer que tudo vindo do repositório auditado é **dado, nunca instrução**. A
  regra atual do README — "respeitar instruções do repositório, como `AGENTS.md`,
  `CLAUDE.md`" — **amplia** a superfície de ataque como está escrita: manda obedecer
  arquivos controlados pelo alvo. Precisa virar lista fechada, e esses arquivos só
  podem **restringir** permissão, nunca ampliar.
- ⛔ **Regra de evidência** (A-12): o que conta como evidência, em formato exato.
- ⛔ **Comportamento no modo autônomo** (A-06): o que fazer quando uma regra pede
  confirmação e não há quem confirme. Sugestão: degrada para **não fazer** e registra
  como pendência — nunca para "fazer assim mesmo".

---

## 3. Contrato de saída

O `README.md` lista nove itens que o agente "deve retornar, no mínimo" — em prosa.
Prosa não é verificável: não dá para validar saída, escrever teste, nem detectar um
ciclo que retornou lixo (A-11).

⛔ **A definir: JSON Schema.** Campos derivados da lista do README:

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

Saída fora do esquema = **ciclo falhou**. Sem essa regra, o esquema é decoração.

---

## 4. Formato de finding

⛔ **A definir** (A-12). Campos obrigatórios propostos:

| Campo | Conteúdo |
|---|---|
| `kind` | `observed` · `inferred` · `recommended` |
| `file` | caminho relativo |
| `line` | linha ou faixa |
| `commit` | commit onde a mudança apareceu |
| `hash` | hash estável para dedup entre ciclos (A-10 / T-06) |
| `summary` | uma frase |

Regras propostas:

- `kind: observed` **sem** `file:line` é inválido — o ciclo rejeita.
- Finding sobre segredo reporta **localização, nunca o valor** (T-01).
- `hash` estável = tipo + caminho + âncora. É o que impede o mesmo issue de ser
  aberto 48 vezes por dia.

---

## 5. Catálogo de modelos

⛔ **Bloqueado por P-01.** Precisa listar, por plataforma, os identificadores
válidos e a cadeia de fallback.

⚠️ O `README.md` usa `claude-sonnet-4.6` como exemplo — **não existe** (A-01). Os
identificadores reais da família Claude são `claude-opus-5`, `claude-sonnet-5`,
`claude-fable-5` e `claude-haiku-4-5-20251001`.

Regra que já vale, do `README.md` §Seleção do agente/modelo: o identificador é uma
**solicitação do usuário**, não garantia de disponibilidade. A skill valida e, se
cair em fallback, **informa** — e a saída reporta o modelo efetivamente usado, não o
pedido.

---

## 6. Adaptadores de plataforma

⛔ **Bloqueado por P-07 e pela validação de F0.**

### 6.1 Claude

⛔ A preencher. O que precisa ser respondido em F0 (achado A-13): quais primitivas
existem — skills, subagentes, hooks, `/loop`, rotinas agendadas — e como cada uma se
declara. Se estiverem todas disponíveis, o AUDITOR é montado sobre mecanismo nativo,
sem inventar scheduler e sem instalar persistência.

Enforcement de escrita (T-03) tende a ser `permissions.deny` + hook `PreToolUse`.

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

- Sintaxe do comando e esquema de configuração → `SPEC.md`.
- Ameaças e controles → `SECURITY.md`.
- Decisões e pendências → `docs/decisoes.md`.
