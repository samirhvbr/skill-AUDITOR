# Escopo e fases — AUDITOR

> ⚠️ **PROPOSTA — aguarda aprovação do Samir.** Nada aqui é decisão fechada. As
> decisões fechadas estão em [`docs/decisoes.md`](../docs/decisoes.md) (ADR-001 a
> ADR-006). Este arquivo organiza os "Próximos passos sugeridos" do `README.md` em
> fases com critério de pronto, para dar ordem e permitir cobrar entrega.
>
> Ao aprovar (ou alterar) este escopo, registrar como **ADR-007** e bumpar `Y` em
> `version.md`.

---

## Princípio de ordenação

As fases seguem a prioridade da [revisão inicial](../docs/revisao-inicial.md):
**primeiro fechar contrato e controle, depois automatizar.** A tentação natural é
começar pelo scheduler — é a parte visível. Seria o erro: sem contrato de saída e
sem gate de escrita, automatizar só multiplica um comportamento não verificado.

---

## F0 — Validar a plataforma (desbloqueia tudo)

**Objetivo:** trocar inferência por fato antes de desenhar qualquer coisa.

- Validar o achado **A-13** contra o Claude Code instalado: existem skills,
  subagentes, hooks, `/loop` e rotinas agendadas? Como se declara cada um?
- Validar **A-01**: catálogo real de modelos e o formato aceito no seletor.
- Validar o equivalente no ShvIA (gateway `ai.shvia.org`, repo `~/x/SHVIA/SHVIA-WEB`).

**Pronto quando:** um documento em `docs/` lista, por plataforma, quais primitivas
existem e como se declaram — com evidência (comando rodado, arquivo, saída), não
com "deve existir". **ADR-004 reescrito** com base no resultado.

---

## F1 — Fechar os contratos

**Objetivo:** o que hoje é prosa vira esquema verificável.

- **Reconciliar `AGENTS.md` × `README.md`** (A-20 a A-23) e consolidar
  `AGENTS.md` × `AGENT.md` (**P-12** / A-19). Barato e primeiro: enquanto dois
  documentos normativos discordarem, toda especificação escrita em cima deles nasce
  errada em pelo menos um lado.
- `SPEC.md`: sintaxe canônica do comando (ADR-005/006), gramática do intervalo,
  esquema de `.auditor/config.yml`, defaults e regras de validação.
- `AGENT.md`: prompt do subagente, **JSON Schema** da saída do ciclo (A-11),
  formato obrigatório de evidência — `file` / `line` / `commit` / `kind` ∈
  {`observed`, `inferred`, `recommended`} (A-12), catálogo de modelos e fallbacks.
- Esquema do `state.json`, incluindo checkpoint resistente a rebase/squash/
  force-push (A-09) e hash estável de finding para dedup (A-10).
- Fechar **P-08** (`.auditor/` versionado ou não) — muda o esquema de estado.

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
- **T-02** — conteúdo do repositório auditado tratado como **dado, nunca instrução**;
  lista fechada de arquivos obedecidos, que só podem restringir permissão.
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
