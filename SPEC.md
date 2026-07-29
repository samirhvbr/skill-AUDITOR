# SPEC.md — Comando e configuração do AUDITOR

> ⚠️ **PARCIAL.** Este arquivo é o destino canônico da sintaxe do comando e do
> esquema de configuração. As seções estão na ordem final; o que está fechado vem
> sem marca, e cada lacuna restante é marcada com ⛔ e a pendência que a bloqueia.
>
> Completar é a fase **F1** ([.continue/escopo-projeto.md](.continue/escopo-projeto.md)).
> Ao fechar uma seção, remover a marca e bumpar `version.md`.
>
> **Fechado até aqui:** gramática do intervalo (§1.5), localização e defaults do
> `config.yml` (§2), **JSON Schemas** em [`schemas/`](schemas/), esquema do
> `state.json` (§3), estrutura de `.auditor/` (§4), no-op quiescente e modo autônomo
> (§5). **Falta:** validador em runtime (P-09), escopo (P-02), retenção (P-05),
> concorrência e a definição de "âncora" no `hash` de achado.
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

Gramática fechada, expressa em `schemas/config.schema.json` (`$defs.interval`):

```
^[1-9][0-9]*[mhd]$      m = minutos · h = horas · d = dias
```

Rejeita `30` (sem unidade), `0m` (zero), `30s` (unidade fora do conjunto), `30 m`
(espaço) e negativos. O teste `test_interval_pattern_rejects_bare_number` cobre os
dois sentidos.

⛔ **A definir:** mínimo e máximo práticos, e a mensagem de erro exata — que deve
mostrar as formas válidas, não só recusar.

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

[`schemas/config.schema.json`](schemas/config.schema.json) — `additionalProperties:
false`, para chave desconhecida virar erro em vez de ser ignorada em silêncio.

Configuração inválida **aborta o ciclo** com mensagem acionável; não cai em default
silenciosamente.

⛔ **Falta o validador.** A biblioteca `jsonschema` não é dependência do projeto
(**P-09**), então hoje nada valida instância contra o esquema em tempo de execução.
Os testes cobrem a estrutura do esquema, não a validação — ver
`tests/test_schemas.py`.

---

## 3. `.auditor/state.json`

Esquema: [`schemas/state.schema.json`](schemas/state.schema.json).

| Campo | Papel |
|---|---|
| `version` | versão do esquema — incompatibilidade é erro explícito, não migração silenciosa |
| `last_sha` | commit do último ciclo **auditado** |
| `last_run` | data/hora do último ciclo auditado — base do fallback temporal |
| `last_checked` | data/hora da última verificação, inclusive ciclos no-op |
| `reported[]` | achados já reportados (`hash`, `first_seen`, `last_seen`, `ref`, `status`) |

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

**É versionado** (ADR-010), logo é **campo de merge**. Formato precisa ser
merge-friendly: chaves ordenadas, uma entrada por linha em `reported[]`, sem
reformatação gratuita. Conflito resolve pela **união** de `reported[]` e pelo
`last_run` mais recente — nunca escolhendo um lado inteiro, o que perderia achados já
reportados e reabriria issues fechados.

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

- **`.auditor/` é versionado** (ADR-010) — não entra no `.gitignore`. É o que faz o
  checkpoint sobreviver a outra máquina e a CI. Consequência direta: relatório é
  artefato **publicado**, então a redação de segredos vira pré-requisito de qualquer
  execução, e não só das que rodam em repositório público.
- **O AUDITOR não commita por padrão.** Em modo interativo o commit é do usuário; em
  modo autônomo com `auto_commit: true`, o ciclo commita em `auditor/<cycle_id>` —
  **nunca** em `master`.
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
