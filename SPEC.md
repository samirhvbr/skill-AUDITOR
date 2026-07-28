# SPEC.md — Comando e configuração do AUDITOR

> ⚠️ **ESQUELETO.** Este arquivo é o destino canônico da sintaxe do comando e do
> esquema de configuração, prometido cinco vezes no `README.md` — mas o conteúdo
> ainda **não foi especificado**. As seções abaixo estão na ordem final; cada lacuna
> marca a pendência que a bloqueia.
>
> Preencher é a fase **F1** ([.continue/escopo-projeto.md](.continue/escopo-projeto.md)).
> Ao preencher uma seção, remover a marca e bumpar `version.md`.
>
> **O que já está decidido** vive em [docs/decisoes.md](docs/decisoes.md) — ADR-005
> (sintaxe) e ADR-006 (unidade obrigatória) são a base do §1 e §2.

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

⛔ **A definir.** No mínimo é preciso existir um `uninstall` — T-04 do `SECURITY.md`
exige desinstalação do gatilho em um comando. Candidatos: `status`, `run` (ciclo
avulso), `uninstall`.

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

### 2.1 Chaves

Base conceitual do `README.md` §Seleção do agente/modelo:

| Chave | Papel | Situação |
|---|---|---|
| `agent` | papel especializado (ex.: `documentation-auditor`) | conceitual |
| `model` | identificador da plataforma alvo | ⛔ bloqueado por **P-01** (ver A-01) |
| `interval` | duração (`30m`, `1h`) | base em ADR-006, gramática pendente |
| `language` | idioma dos artefatos — `en-US` | ver A-15 |
| `scope` | arquivos e branches | ⛔ bloqueado por **P-02** |
| `write_policy` | v1: apenas `.auditor/` | ⚠️ **não é enforceable por prompt** — A-04 / T-03 |
| `open_pr_issue` | `off` / `ask` / `always` | decidido em ADR-003 |
| `state_source` | origem do estado (`git`) | ⛔ bloqueado por **P-08** |
| `auto_scheduler` | instalar gatilho | ⚠️ ADR-004 **em revisão** — default `false` até A-13 |
| `retain_days` | retenção de relatórios | ⛔ bloqueado por **P-05** |
| `cost_cap` | teto de custo por ciclo/dia | ⛔ a definir — T-07 |

### 2.2 Defaults

⛔ **A definir.** Regra de partida sugerida: **todo default é o mais restritivo** —
`open_pr_issue: ask`, `auto_scheduler: false`, `write_policy: auditor-only`.

### 2.3 Esquema formal

⛔ **A definir.** JSON Schema, para validar o arquivo antes de rodar o ciclo.

---

## 3. `.auditor/state.json`

⛔ **A definir.** Requisitos já levantados que o esquema precisa atender:

- **Checkpoint resistente** (A-09): guardar SHA **e** data. SHA que não existe mais
  (rebase, squash, force-push) degrada para janela temporal, com a degradação
  declarada no relatório.
- **Hash estável de finding** (A-10 / T-06): tipo + caminho + âncora, para dedup
  entre ciclos — sem isso, PR/issue viram flood.
- **`last_checked` separado de `last_audited`** (A-07): ciclo no-op atualiza só o
  primeiro.
- ⛔ **P-08** define se este arquivo é versionado, local ou derivado de fonte
  compartilhada (tag/nota git).

---

## 4. Estrutura de `.auditor/`

Proposta em `README.md` §Estrutura proposta de `.auditor`. Antes de fixar, resolver
o achado **A-14**: `.auditor/docs/` se sobrepõe a `docs/` e `.auditor/index.md` se
sobrepõe a `.continue/estado-atual.md` nos repositórios da casa.

Direção sugerida (não decidida): `.auditor/` guarda **achados e estado** — o que é
do robô — e nunca documentação final. O que for promovido a doc oficial vira
**proposta de diff** para `docs/`, revisada por humano.

---

## 5. Ciclo de vida

Fluxo em 10 passos no `README.md` §Fluxo de um ciclo. Falta especificar:

- ⛔ **No-op quiescente** (A-07): condição exata e o que é atualizado no estado.
- ⛔ **Falha parcial**: o que é registrado, o que continua, o que aborta.
- ⛔ **Concorrência**: dois ciclos disparados juntos — lock, ou o segundo desiste?
- ⛔ **Modo autônomo vs interativo** (A-06): toda regra que diz "pedir confirmação"
  precisa de comportamento definido no modo em que não há quem confirme.

---

## 6. Não pertence a este arquivo

- Contrato do subagente, prompt, catálogo de modelos → `AGENT.md`.
- Ameaças e controles → `SECURITY.md`.
- Decisões e pendências → `docs/decisoes.md`.
