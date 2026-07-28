# Escopo e fases — AUDITOR

> ⚠️ **PROPOSTA — aguarda aprovação do Samir.** As fases em si não são decisão
> fechada; as decisões estão em [`docs/decisoes.md`](../docs/decisoes.md) (ADR-001 a
> ADR-009). Este arquivo organiza os "Próximos passos sugeridos" do `README.md` em
> fases com critério de pronto, para dar ordem e permitir cobrar entrega.
>
> Ao aprovar (ou alterar) este escopo, registrar como **ADR-010** e bumpar `Y` em
> `version.md`.
>
> **Situação:** F0 e F1 estão parcialmente feitas — o que já fechou está marcado com
> ✅, o que falta com ⛔.

---

## Princípio de ordenação

As fases seguem a prioridade da [revisão inicial](../docs/revisao-inicial.md):
**primeiro fechar contrato e controle, depois automatizar.** A tentação natural é
começar pelo scheduler — é a parte visível. Seria o erro: sem contrato de saída e
sem gate de escrita, automatizar só multiplica um comportamento não verificado.

---

## F0 — Validar a plataforma (desbloqueia tudo)

**Objetivo:** trocar inferência por fato antes de desenhar qualquer coisa.

- ✅ **Claude Code — as cinco primitivas existem** (skills, subagentes, hooks,
  execução recorrente, rotinas agendadas). Base do ADR-008.
- ⛔ **Falta:** documentar **como cada uma se declara** no Claude Code — formato do
  arquivo de skill, do subagente, do hook, registro da rotina.
- ⛔ **Falta:** validar o equivalente no **ShvIA** (gateway `ai.shvia.org`, repo
  `~/x/SHVIA/SHVIA-WEB`). Hoje é inferência.
- ⛔ **Falta:** catálogo real de modelos por plataforma e o formato aceito (**P-01**).

**Pronto quando:** um documento em `docs/` lista, por plataforma, quais primitivas
existem e como se declaram — com evidência (comando rodado, arquivo, saída), não
com "deve existir".

---

## F1 — Fechar os contratos

**Objetivo:** o que hoje é prosa vira esquema verificável.

- ✅ **Reconciliar as divergências normativas** (A-19 a A-23) — feito em `0.2.0`
  pelos ADR-007/008/009.
- ✅ `SPEC.md`: localização e defaults do `config.yml`, estrutura de `.auditor/`,
  no-op quiescente, modo autônomo.
- ✅ `docs/contrato-subagente.md`: formato obrigatório de achado — `file` / `line` /
  `commit` / `hash` / `kind` ∈ {`observed`, `inferred`, `recommended`} (A-12).
- ✅ Esquema do `state.json`: checkpoint resistente a rebase/squash/force-push (A-09)
  e `reported[]` para dedup (A-10).
- ⛔ **Falta:** o **JSON Schema** da saída do ciclo e do `config.yml` (A-11) — é o
  item que trava o "pronto quando" abaixo.
- ⛔ **Falta:** gramática do intervalo, escopo (**P-02**), retenção (**P-05**),
  concorrência e a definição de "âncora" no `hash`.
- ⛔ **Falta:** fechar **P-08** (`.auditor/` versionado ou não) — muda o esquema de
  estado.

**Pronto quando:** um relatório de exemplo valida contra o schema, e um relatório
propositalmente quebrado é **rejeitado**.

---

## F2 — Executor local de um ciclo

**Objetivo:** rodar um ciclo à mão, de forma reproduzível — a base de todo teste.

- Decidir a stack (**P-09**).
- Carregar config + estado → detectar mudanças via Git → montar contexto → chamar o
  agente → validar a saída contra o schema → escrever `.auditor/` → atualizar estado.
- **No-op quiescente** (A-07): ciclo sem mudança não escreve relatório, não abre
  nada, não bumpa estado.
- Degradação declarada: checkpoint órfão cai para janela temporal e **diz isso** no
  relatório (A-09).

**Pronto quando:** dois ciclos seguidos num repositório-fixture produzem o resultado
esperado, e o segundo ciclo sem mudança é no-op.

---

## F3 — Controles de segurança (bloqueia uso real)

**Objetivo:** sair de "regra no prompt" para controle mecânico. Ver
[`SECURITY.md`](../SECURITY.md).

- **T-01/T-05** — redação mecânica de segredos na saída (regex + denylist de
  caminhos); achado sobre segredo reporta `arquivo:linha`, nunca o valor.
- **T-02** — a **regra** já está escrita no prompt (ADR-009); falta o **teste**:
  fixture com injeção plantada, que falhe com a defesa desligada.
- **T-03** — enforcement de `write_policy` fora do modelo (deny + hook `PreToolUse`
  no Claude; gate no runner do ShvIA), com caminho normalizado.
- **T-08** — em modo autônomo, nunca sobrescrever arquivo pré-existente.
- Fixtures de regressão para segredo plantado e para injeção plantada (README,
  comentário e mensagem de commit).

**Pronto quando:** os testes de regressão passam **e** falham quando o controle é
desligado — controle que não é testado nos dois sentidos não é controle.

---

## F4 — Adaptadores de plataforma

**Objetivo:** o mesmo ciclo rodando em Claude e em ShvIA.

- Adaptador **ShvIA** primeiro (controle total, ADR-002) — serve de referência do
  comportamento pretendido.
- Adaptador **Claude** em paralelo — mostra o que dá para fazer sem controlar a
  plataforma.
- Divergência entre plataformas é **documentada**, não escondida atrás de um "deve
  funcionar igual".

**Pronto quando:** o mesmo repositório-fixture produz relatórios equivalentes nas
duas plataformas, com as diferenças documentadas.

---

## F5 — Agendamento

**Objetivo:** o ciclo dispara sozinho — pelo mecanismo que F0 confirmou existir.

- Gatilho por relógio, por atividade (hook) ou os dois (**P-11**).
- Registro do que foi instalado + **desinstalação em um comando** (T-04).
- Teto de custo por ciclo e por dia, com kill-switch (T-07).
- Dedup de findings e teto de PR/issue por ciclo (T-06, A-10).

**Pronto quando:** um ciclo dispara sozinho, é desinstalado por um comando, e o
kill-switch de custo funciona.

---

## F6 — Distribuição

**Objetivo:** instalável em qualquer repositório.

- Licença e formato de pacote (**P-10**).
- Instruções de instalação por plataforma.
- Integração com o padrão da casa: **como o `.auditor/` convive com `docs/`,
  `.continue/` e `version.md`** (A-14, P-03) — nos nossos repos isso já vale hoje.

**Pronto quando:** um repositório limpo instala e roda o AUDITOR seguindo só a doc.

---

## Fora de escopo na v1 (não relitigar sem ADR)

- Alterar código da aplicação auditada. O AUDITOR **documenta**, não corrige.
- Plataforma OpenAI (ADR-001).
- Consolidar automaticamente `.auditor/` em `docs/` sem revisão humana (A-14).
- Modo "yolo" sem gate de escrita.
