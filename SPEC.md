# SPEC.md — Comando e configuração do AUDITOR

> ⚠️ **PARCIAL.** Este arquivo é o destino canônico da sintaxe do comando e do
> esquema de configuração. As seções estão na ordem final; o que está fechado vem
> sem marca, e cada lacuna restante é marcada com ⛔ e a pendência que a bloqueia.
>
> Completar é a fase **F1** ([.continue/escopo-projeto.md](.continue/escopo-projeto.md)).
> Ao fechar uma seção, remover a marca e bumpar `version.md`.
>
> **Fechado até aqui:** localização e defaults do `config.yml` (§2), esquema do
> `state.json` (§3), estrutura de `.auditor/` (§4), no-op quiescente e modo autônomo
> (§5). **Falta:** gramática do intervalo, JSON Schema, escopo (P-02), retenção
> (P-05) e concorrência.
>
> **Decisões** vivem em [docs/decisoes.md](docs/decisoes.md) — ADR-003 (PR/issue),
> ADR-005 (sintaxe), ADR-006 (unidade), ADR-008 (scheduler) e ADR-009 (conteúdo não
> confiável) são a base deste documento.

---

## 1. Comando

### 1.1 Forma canônica *(base decidida em ADR-005)*

```text
/auditor every <intervalo> model <modelo>
```

### 1.2 Forma curta *(atalho documentado — ADR-005)*

```text
/auditor <intervalo> <modelo>
```

A forma longa é a canônica e aparece primeiro em toda a documentação. A curta
existe para quem já conhece, e não deve ser a única forma ensinada.

### 1.3 Nome do comando

Repositório `AUDITOR` (maiúsculo, padrão da casa) · skill `auditor` · comando
`/auditor`. Ver achado A-18.

### 1.4 Subcomandos

`/auditor uninstall` é **obrigatório** — T-04 do `SECURITY.md` exige que todo gatilho
instalado seja removível em um passo, e o comando reporta o que não conseguiu
remover.

⛔ **A definir:** o resto da lista. Candidatos: `status` (mostra config, estado e
gatilho ativo) e `run` (ciclo avulso, sem mexer no agendamento).

### 1.5 Gramática do intervalo *(base decidida em ADR-006)*

Unidade **obrigatória**: `30` solto é rejeitado.

⛔ **A definir:** conjunto fechado de unidades aceitas (`m`, `h`, `d`?), mínimo e
máximo, e a mensagem de erro exata para intervalo inválido — que deve mostrar as
formas válidas, não só recusar.

### 1.6 Regras de validação e mensagens de erro

⛔ **A definir.** Depende de P-01 (catálogo de modelos): o que acontece quando o
modelo pedido não existe na plataforma — erro ou fallback declarado?

---

## 2. `.auditor/config.yml`

**Localização: `.auditor/config.yml`**, dentro do diretório do AUDITOR no
repositório auditado — não na raiz. Mantém tudo do AUDITOR sob um diretório e evita
que a configuração se confunda com arquivos do projeto auditado (A-21).

### 2.1 Chaves

| Chave | Papel | Default | Situação |
|---|---|---|---|
| `agent` | papel especializado (ex.: `documentation-auditor`) | `documentation-auditor` | conceitual |
| `model` | identificador da plataforma alvo | — | ⛔ catálogo em **P-01** |
| `interval` | duração (`30m`, `1h`) | — | ADR-006; gramática em §1.5 |
| `language` | idioma dos artefatos | `en-US` | fechado |
| `scope` | arquivos e branches | — | ⛔ bloqueado por **P-02** |
| `write_policy` | v1: apenas `.auditor/` | `auditor-only` | ⚠️ **não é enforceable por prompt** — A-04 / T-03 |
| `open_pr_issue` | `off` / `ask` / `always` | **`ask`** | fechado — ADR-003 |
| `state_source` | origem do estado (`git`) | `git` | ⛔ bloqueado por **P-08** |
| `auto_scheduler` | autoriza instalar gatilho | **`false`** | fechado — ADR-008 |
| `retain_days` | retenção de relatórios | — | ⛔ bloqueado por **P-05** |
| `cost_cap` | teto de custo por ciclo/dia | — | ⛔ a definir — T-07 |

Notas normativas:

- `open_pr_issue: always` só é válido com redação de segredos e deduplicação de
  achados ativas. Sem as duas, degrada para `ask`.
- `auto_scheduler: true` **não** depende da plataforma: vale como autorização do dono
  do repositório auditado, e só isso (ADR-008). Rodar em ShvIA não altera o default.
- Nenhuma chave deste arquivo pode **ampliar** o que a invocação concedeu — só
  restringir (ADR-009). Configuração que pede mais é ignorada e vira achado.

### 2.2 Defaults

**Todo default é o mais restritivo**: `open_pr_issue: ask`, `auto_scheduler: false`,
`write_policy: auditor-only`, `language: en-US`. Ausência do arquivo não é erro — a
skill roda nos defaults e **registra a ausência** no relatório.

### 2.3 Esquema formal

⛔ **A definir.** JSON Schema, para validar o arquivo antes de rodar o ciclo.
Configuração inválida aborta o ciclo com mensagem acionável; não cai em default
silenciosamente.

---

## 3. `.auditor/state.json`

Campos obrigatórios — fechados em `0.2.0`:

| Campo | Papel |
|---|---|
| `last_sha` | commit do último ciclo **auditado** |
| `last_run` | data/hora do último ciclo auditado — base do fallback temporal |
| `last_checked` | data/hora da última verificação, inclusive ciclos no-op |
| `reported[]` | `hash` dos achados já reportados, para dedup entre ciclos |

Regras:

- **Checkpoint resistente** (A-09): validar `last_sha` antes de usar
  (`git cat-file -e`). Se não existir mais — rebase, squash, force-push — usar a
  janela desde `last_run` e **declarar a degradação** no relatório.
- **No-op não move o checkpoint** (A-07): ciclo sem mudança atualiza só
  `last_checked`.
- **Falha parcial não move o checkpoint** do escopo que não foi auditado.
- `reported[]` é o que impede o mesmo achado de virar issue novo a cada ciclo
  (A-10 / T-06). Cresce indefinidamente — a política de poda entra junto com
  `retain_days` (P-05).

⛔ **P-08** define se este arquivo é versionado, local ou derivado de fonte
compartilhada (tag/nota git). É a decisão que falta para fechar o esquema.

---

## 4. Estrutura de `.auditor/`

```text
.auditor/
├── config.yml       # §2
├── state.json       # §3
├── scheduler.json   # gatilho instalado, com o comando de remoção (T-04)
├── index.md         # índice cumulativo dos ciclos, achados e decisões
├── reports/         # YYYY-MM-DD-HHMM.md, um por ciclo com mudança
└── findings/        # lacunas e recomendações pendentes
```

Decisões desta seção:

- **`index.md`, não `summary.md`** — um único arquivo cumulativo, atualizado e nunca
  recriado (A-22).
- **Sem `.auditor/docs/`** — `.auditor/` guarda **achados e estado**, o que é do
  robô, e nunca documentação final. Nos repositórios da casa já existem `docs/`,
  `.continue/` e `version.md`; um quarto autor escrevendo sobre os mesmos assuntos
  diverge (A-14). O que for promovido a documentação oficial vira **proposta de diff
  para `docs/`**, revisada por humano.

⛔ **A definir:** a cadência e o formato dessa promoção (**P-03**).

---

## 5. Ciclo de vida

Fluxo em 10 passos no `README.md` §Fluxo de um ciclo.

**No-op quiescente** (A-07) — fechado: se não há mudança entre o checkpoint e `HEAD`,
o ciclo não escreve relatório, não abre PR/issue, não toca `last_sha` e atualiza só
`last_checked`. Encerra com resumo de uma linha.

**Modo autônomo** (A-06) — fechado: sem ninguém para confirmar, toda regra que
pediria confirmação degrada para **não fazer**, e o item vai para
`pending_decisions`. Nunca degrada para "fazer assim mesmo". Escrita autônoma nunca
sobrescreve arquivo pré-existente.

⛔ **A definir:**

- **Falha parcial**: o que é registrado, o que continua, o que aborta. Regra já
  fixada: não mover o checkpoint de escopo não auditado.
- **Concorrência**: dois ciclos disparados juntos — lock, ou o segundo desiste?
- **Tetos de custo** (T-07): valores default e comportamento exato do kill-switch.

---

## 6. Não pertence a este arquivo

- Contrato do subagente e catálogo de modelos →
  [`docs/contrato-subagente.md`](docs/contrato-subagente.md).
- O prompt de runtime → [`prompts/auditor-system.md`](prompts/auditor-system.md).
- Ameaças e controles → [`SECURITY.md`](SECURITY.md).
- Decisões e pendências → [`docs/decisoes.md`](docs/decisoes.md).
