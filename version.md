# Versão — AUDITOR

**Versão atual:** `0.3.1`

> Este arquivo é a **fonte da verdade** da versão do projeto. Qualquer lugar que
> precise exibir ou reportar a versão (skill, CLI, relatório de ciclo, pacote de
> distribuição) deve **ler daqui**, extraindo o **primeiro número semver
> (`X.Y.Z`)** encontrado no arquivo. Mantenha a linha **"Versão atual"** sempre
> como a primeira ocorrência de um número de versão.
>
> Mesma mecânica dos projetos-irmãos (SHVIA-WEB, SHVIA-CODE, SSHVTERM-DESKTOP,
> BLUE3-WCUP-2026, MARTHINA-CLASS).

---

## 1. Convenção de Versionamento (`X.Y.Z`)

Padrão semântico simplificado, herdado do guia de projetos do Samir.

| Componente | Significado | Como sobe |
|---|---|---|
| **X** | Release estável — skill distribuível e instalável por terceiros | Manual |
| **Y** | Mudança estrutural — novo adaptador de plataforma, mudança de contrato/esquema, fase concluída | Manual |
| **Z** | Incremento a cada entrega (ver gatilhos) | A cada entrega |

Enquanto `X` for `0`, o projeto é **pré-release**: contratos (`config.yml`,
`state.json`, saída do subagente) podem quebrar entre versões `0.Y`.

### Gatilhos de bump do `Z`

Incremente o `Z` (e registre no changelog abaixo) sempre que:

- Criar ou alterar um documento em `docs/`, `SPEC.md` ou `prompts/` que **muda uma
  regra** (não vale corrigir redação).
- Alterar o **prompt / contrato de execução** do subagente.
- Alterar o **esquema** de `.auditor/config.yml`, `.auditor/state.json` ou do
  relatório de ciclo.
- Alterar a **sintaxe do comando** (`/auditor …`) ou seus defaults.
- Alterar **política de segurança**: `write_policy`, `open_pr_issue`,
  auto-instalação de scheduler, redação de segredos, retenção.
- Alterar `.claude/settings.json` (permissões, perfil de modelo).
- Adicionar ou mudar comportamento do executor/harness, quando existir.
- Adicionar ou alterar testes que definem comportamento esperado.

### Gatilhos de bump do `Y`

- Novo **adaptador de plataforma** (ex.: entrar suporte a uma plataforma além de
  Claude e ShvIA).
- Quebra de compatibilidade em `config.yml` / `state.json` / saída do agente.
- Conclusão de uma **fase** do escopo (ver `.continue/escopo-projeto.md`).
- Novo ADR com status **Aceito** que muda a direção do produto.

> Correções de texto, typo, formatação e reordenação de seções **não** exigem bump.

---

## 2. Formato de Commit Obrigatório

```
X.Y.Z - Descrição curta em português
```

Exemplo:

```bash
git commit -m "0.3.0 - Fecha o JSON Schema da saida do ciclo"
```

**Regras inegociáveis:**

1. A versão **sempre** vem deste `version.md` — bumpe o arquivo **no mesmo
   commit** da mudança, nunca separado.
2. Mensagem em **português**, descritiva o suficiente para `git log --grep`.
3. **Proibido** `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `style:`,
   `test:` (Conventional Commits) ou mensagens vagas ("ajuste", "fix", "update").
4. Um objetivo por commit; mudanças pequenas e atômicas.

O bump do `version.md` entra em **um único commit** por entrega (o primeiro da
entrega). Commits adicionais da mesma entrega repetem a versão sem novo bump.

> **Nota de ambiente:** o diretório `~/x` tem um processo automático que commita
> e pusha o working tree com mensagens do tipo `Version X (clean)`. Isso **não
> substitui** o commit versionado acima — confira `git log` antes de assumir que
> uma entrega foi registrada corretamente.

---

## 3. Changelog

> Ordem decrescente (mais recente no topo). Cada entrada lista as mudanças e os
> gatilhos que justificaram o bump.

### `0.3.1` — 2026-07-29 — Redação: fim do falso positivo em código de parser; P-12 registrada

O dogfood do **skill-COMMITTER** (que vendoriza os padrões daqui) achou um falso
positivo de classe no `assigned-secret`: `tokens = out.split("\0")` — variável
`tokens` recebendo expressão de código — casava o padrão, e lá isso **bloquearia o
próprio arquivo do ciclo para sempre** (ADR-005 de lá exclui o arquivo inteiro).

**Correção** (`skill/auditor/lib/redact.py`, fonte da verdade dos padrões)
- Valor do `assigned-secret` não aceita `()` **e** ganha lookahead de fronteira:
  expressão de código tem parêntese, segredo real (AWS/JWT/base64/hex/DSN) não.
  Só excluir da classe não bastava — o motor casava um **prefixo** do valor
  (`out.spl`). Teste de regressão novo (3 variantes de linha de parser); suíte em
  **44**. Sincronizado com `skill-COMMITTER/skill/committer/secret_scan.py`.

**Decisões**
- **P-12** registrada: auth da execução headless (`subscription` / `api-key` /
  gateway ShvIA) — espelho do ADR-008 do skill-COMMITTER; aqui afeta o ciclo
  inteiro. Da pergunta do Samir sobre rodar as skills por API key.

_Gatilhos:_ mudança de comportamento da redação (política de segurança) + pendência
nova de direção.

---

### `0.3.0` — 2026-07-29 — Primeiro código: `.auditor/` versionado, esquemas e os dois controles

Sai da documentação pura. Bump de **`Y`** por ADR aceito que muda a direção
(ADR-010), esquema novo e primeiro adaptador de plataforma.

**Decisão**
- **ADR-010 — `.auditor/` é versionado** (resolve P-08). O checkpoint compartilhado
  vale mais que o ruído, e o ruído já tem contenção no no-op quiescente. Consequências
  que a decisão obriga e que estão propagadas: relatório vira **artefato publicado**
  (T-01/T-05 sobem para pré-requisito de qualquer execução, não só em repo público);
  o AUDITOR **não commita por padrão** e, em modo autônomo, commita em
  `auditor/<cycle_id>` — nunca em `master`; `state.json` vira campo de merge, com
  conflito resolvido pela **união** de `reported[]`.

**Código**
- `skill/auditor/hooks/write-gate.py` — **gate de escrita (T-03)**, hook `PreToolUse`.
  Bloqueia escrita fora de `.auditor/` com `realpath` (barra `..`, caminho absoluto e
  symlink plantado dentro de `.auditor/`), restringe Bash a allowlist de inspeção com
  encadeamento e redirecionamento recusados, e é **fail-closed**: erro interno nega.
  Só enforça durante um ciclo (`AUDITOR_CYCLE_ID`), senão travaria o desenvolvimento.
- `skill/auditor/lib/redact.py` — **redação mecânica de segredos (T-01)**. Chaves de
  nuvem, tokens de provedor, PEM, JWT, `Authorization:`, credencial em URL e
  atribuição a variável de nome sensível. `assert_clean()` aborta publicação de
  PR/issue que precisou ser redigida. Testada também contra **excesso**: prosa,
  caminho de arquivo e nome de variável sem valor passam intactos.
- `skill/auditor/SKILL.md` + `config.example.yml` + `skill/README.md` — primeiro
  adaptador de plataforma (Claude Code), com instalação e limites declarados.

**Esquemas** — fecham a maior parte de A-11
- `schemas/config.schema.json`, `schemas/state.schema.json`,
  `schemas/cycle-report.schema.json`. Três regras condicionais que não cabiam em
  prosa: `observed` exige `file`+`line`; `time-window` exige `degraded_reason`;
  `no-op` proíbe achado e artefato. `artifacts_written` só aceita caminho em
  `.auditor/`. Gramática do intervalo fechada: `^[1-9][0-9]*[mhd]$`.

**Testes** — 43, sem dependência externa
- `tests/test_write_gate.py` (20), `tests/test_redact.py` (16),
  `tests/test_schemas.py` (7). Cobrem os **dois sentidos**: com o controle ligado e
  desligado. Verificado por mutação — neutralizar `inside()` no gate derruba 7 testes.

**O que continua faltando, dito sem eufemismo**
- **Não existe executor.** Nenhum ciclo completo rodou de ponta a ponta.
- **Sem validador em runtime** (`jsonschema` não é dependência — P-09), então "saída
  fora do esquema reprova o ciclo" ainda não acontece de fato.
- **A-03 (prompt injection) segue sem teste:** falta o fixture com injeção plantada.
  Enquanto isso, a defesa é afirmação, não medição.
- Adaptador ShvIA, licença (P-10) e empacotamento não existem.

_Gatilhos:_ ADR aceito que muda a direção, esquemas novos, primeiro adaptador de
plataforma e alteração de política de segurança.

---

### `0.2.0` — 2026-07-28 — Correções da revisão: 18 dos 23 achados fechados

Aplica as correções e as recomendações da
[revisão inicial](docs/revisao-inicial.md). Continua sem implementação — só
documentação. Bump de **`Y`** por dois ADRs aceitos que mudam a direção do produto
(ADR-007 e ADR-008) e por mudança de estrutura de arquivos.

**Decisões novas**
- **ADR-007** — arquivos de agente: artefato do **produto** mora em `prompts/` e
  `docs/`; a raiz fica para os arquivos do **repositório**. `AGENTS.md` virou
  `prompts/auditor-system.md` e `AGENT.md` virou `docs/contrato-subagente.md`, os
  dois com `git mv`. `CLAUDE.md` + `AGENTS.md` voltam a ser espelhados, como nos
  outros repos da casa. Motivo concreto: `AGENTS.md` na raiz é carregado
  automaticamente, e o conteúdo ("Você é o AUDITOR, execute UM ciclo") fazia
  qualquer sessão aberta no repo se comportar como o produto em execução.
- **ADR-008** — scheduler (substitui o ADR-004): mecanismo nativo da plataforma
  primeiro; auto-instalação é **último recurso**, com `auto_scheduler` default
  `false` em qualquer plataforma, ShvIA inclusive. Quem autoriza é o **dono do
  repositório/máquina auditada**, não quem escreveu a plataforma.
- **ADR-009** — conteúdo do repositório auditado é **dado, nunca instrução**; a
  lista de arquivos que o AUDITOR obedece é fechada e só pode restringir permissão.

**Prompt de runtime** (`prompts/auditor-system.md`)
- Nova seção **Conteúdo não confiável**, logo após a identidade.
- Formato obrigatório de achado: `kind` / `file` / `line` / `commit` / `hash` /
  `summary`; `observed` sem `file:line` é inválido.
- Seção de segredos: reporta localização, nunca o valor; nada de diff bruto.
- Modo autônomo: regra que pediria confirmação degrada para **não fazer**; escrita
  nunca sobrescreve arquivo pré-existente.
- No-op quiescente e checkpoint resistente a rebase/squash/force-push.
- Scheduler reescrito conforme ADR-008.

**Divergências normativas reconciliadas**
- `open_pr_issue`: booleano → enum `off`/`ask`/`always`, default `ask` (o booleano
  não conseguia expressar `ask`, que é o default seguro).
- `config.yml`: raiz → `.auditor/config.yml`.
- Resumo cumulativo: `summary.md` → `index.md`.
- Chave `auto_fix` **removida** — habilitaria o que o escopo da v1 proíbe.

**Documentação**
- `README.md`: id de modelo (`claude-sonnet-5`), §Agendamento reescrita, prompt
  injection nas regras de segurança, idioma desambiguado, nomes (repo `AUDITOR` ·
  skill `auditor` · comando `/auditor`), decisões e pendências realinhadas aos ADRs.
- `SPEC.md` e `docs/contrato-subagente.md`: de **esqueleto** para **parcial**.
- `SECURITY.md`: controles marcados `[x]` quando decididos e escritos, `[ ]` quando
  exigem código e teste — com o aviso de que escrito **não** é implementado.
- `docs/revisao-inicial.md`: tabela de situação dos 23 achados.
- `.continue/`: estado atual e fases atualizados.

_Gatilhos:_ ADRs aceitos que mudam a direção, mudança de estrutura de arquivos,
alteração do prompt do subagente e de política de segurança.

---

### `0.1.0` — 2026-07-28 — Baseline de documentação, versionamento e segurança

Primeira versão numerada. Os três commits anteriores (`c66252c` proposta,
`ed330a9` ajuste do README, `1cd405a` `AGENTS.md`) são **pré-versionamento** e não
seguem o formato de commit acima. Nenhuma implementação — só documentação,
configuração do agente e revisão.

**Documentação**
- `CLAUDE.md` — regras operacionais de quem **desenvolve** este repo: formato de
  commit, o que não relitigar, idioma, e a tabela dos três arquivos de agente.
  ⚠️ **Sem espelhamento `CLAUDE.md` ↔ `AGENTS.md`** aqui: neste projeto o
  `AGENTS.md` é do produto (prompt de runtime do subagente), não do repositório.
- `version.md` (este arquivo) — fonte de verdade da versão, gatilhos de bump e
  formato de commit obrigatório.
- `SECURITY.md` — modelo de ameaça do produto (o AUDITOR é um agente com escrita,
  PR/issue e auto-instalação de scheduler) e política do repositório.
- `docs/README.md` — índice da documentação técnica.
- `docs/decisoes.md` — ADR-001 a ADR-006 registrando as decisões já fechadas;
  12 pendências (P-01 a P-12) e a tabela das divergências normativas abertas.
- `docs/revisao-inicial.md` — revisão do estado atual: **23 achados** (6 altos,
  12 médios, 5 baixos), contradições e lacunas da proposta.
- `SPEC.md` e `AGENT.md` — **esqueletos**, com as seções definidas e cada decisão
  pendente marcada. Existiam como links quebrados no README.
- `.continue/escopo-projeto.md` (fases F0–F6, **proposta**, aguarda aprovação) e
  `.continue/estado-atual.md`.

**Nota sobre o `AGENTS.md`**
O commit `1cd405a` chegou ao `origin` durante esta entrega. O arquivo foi
sobrescrito por engano (assumindo o espelhamento padrão da casa) e **restaurado
verbatim** de `1cd405a` — nenhum conteúdo perdido. O episódio virou o achado A-19:
`AGENTS.md` e `AGENT.md` diferem por uma letra e descrevem o mesmo subagente em
níveis diferentes. Consolidação pendente em P-12.

**Configuração**
- `.claude/settings.json` — perfil Opus-only (`opus[1m]`, `effortLevel: xhigh`),
  `defaultMode: plan`, deny-list de segurança.
- `.claude/README.md` — explica o perfil e a allow-list recomendada.
- `.gitignore`.

_Gatilhos:_ baseline de documentação/versionamento + política de segurança +
configuração do agente.
