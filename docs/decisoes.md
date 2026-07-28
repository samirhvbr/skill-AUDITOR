# AUDITOR — Decisões (ADRs)

Formato ADR. **Não relitigar direção já decidida dentro de um how-to** — linkar o
ADR. Decisão nova entra aqui, com data e status, no mesmo commit da mudança que ela
justifica.

Status possíveis: **Aceito** · **Em revisão** · **Substituído por ADR-NNN** ·
**Rejeitado**.

> Os ADR-001 a ADR-006 **registram** decisões já fechadas na proposta original
> (`README.md`, commits `c66252c` / `ed330a9`). A data de decisão é anterior a este
> arquivo; a data de registro é 2026-07-28.

---

## ADR-001 — Plataformas da primeira versão: Claude e ShvIA

- **Data:** registrada em 2026-07-28 · **Status:** Aceito
- **Contexto:** o AUDITOR precisa de um runtime de agente com subagentes, leitura de
  repositório e escrita de arquivo. Três candidatos naturais: Claude, ShvIA e OpenAI.
- **Decisão:** v1 suporta **Claude** e **ShvIA**. **OpenAI fica fora** do escopo
  inicial.
- **Razão:** Claude é a plataforma de trabalho diária e serve de referência de
  comportamento; ShvIA é da casa e pode ser adaptada ao que o AUDITOR precisar
  (ADR-002). OpenAI adicionaria um terceiro contrato a manter sem trazer capacidade
  nova nesta fase.
- **Consequência:** todo contrato precisa de **adaptador por plataforma**, não de um
  caminho único. Ver pendência P-07.

---

## ADR-002 — ShvIA é plataforma sob autoria do mantenedor e pode ser customizada

- **Data:** registrada em 2026-07-28 · **Status:** Aceito
- **Contexto:** o AUDITOR depende de coisas que uma plataforma de terceiro pode
  simplesmente não oferecer — scheduler, contrato de saída estruturado, gates de
  escrita.
- **Decisão:** no ShvIA (`~/x/SHVIA`, gateway `ai.shvia.org`), o que faltar pode ser
  **implementado do lado da plataforma**: prompt de sistema, contrato de saída,
  scheduler, gates.
- **Consequência:** o adaptador ShvIA tende a ser o mais completo e serve de
  referência do comportamento pretendido; o adaptador Claude mostra o que é possível
  sem controlar a plataforma.
- **Cuidado:** controlar a plataforma **não** é controlar o repositório auditado.
  Ver ADR-004 e o achado A-02.

---

## ADR-003 — Abrir PR/issue é permitido, regido por `open_pr_issue`

- **Data:** registrada em 2026-07-28 · **Status:** Aceito
- **Contexto:** um relatório que ninguém lê não muda nada; PR e issue são os canais
  onde o time já trabalha.
- **Decisão:** o AUDITOR **pode** abrir PR e issue. O comportamento é regido pela
  chave `open_pr_issue`:
  - `off` — nunca abre.
  - `ask` — abre só com confirmação explícita (**default**).
  - `always` — abre sem perguntar (para execução autônoma).
- **Consequência:** PR/issue é um canal de **saída para fora do repositório**,
  frequentemente público. `always` exige, obrigatoriamente, redação de segredos
  ativa (T-01/T-05 do `SECURITY.md`) e deduplicação de findings (T-06 / achado
  A-10). Sem esses dois, `always` não deve ser habilitado.

---

## ADR-004 — Política de scheduler: instalar gatilho quando não houver

- **Data:** registrada em 2026-07-28 · **Status:** ❌ **Substituído pelo ADR-008**
- **Decisão original:** quando não houver scheduler nem spec contrária no projeto
  auditado, o AUDITOR **tenta instalar o gatilho automaticamente**, de forma
  registrada e reversível. Em **ShvIA** isso seria o comportamento padrão; em
  plataformas de terceiros, exigiria confirmação explícita do usuário.
- **Por que caiu — dois problemas:**
  1. **Eixo errado** (achado A-02): quem autoriza persistência é o **dono do
     repositório/máquina alvo**, não o autor da plataforma. O AUDITOR rodando no
     ShvIA pode estar auditando repositório de terceiro.
  2. **Premissa desatualizada** (achado A-13): a premissa de que a plataforma não
     agenda não se sustenta para o Claude Code.
- Mantido aqui como registro. A política vigente é a do ADR-008.

---

## ADR-005 — Sintaxe do comando: forma longa canônica, curta como atalho

- **Data:** registrada em 2026-07-28 · **Status:** Aceito
- **Decisão:**
  - Forma **canônica**: `/auditor every <intervalo> model <modelo>`
  - Forma **curta** (atalho documentado): `/auditor <intervalo> <modelo>`
- **Razão:** a forma longa é auto-explicativa e não depende de posição; a curta é
  conveniente para quem já conhece. Documentar as duas evita que a curta vire a
  única conhecida e a ordem dos argumentos vire adivinhação.
- **Consequência:** o parser precisa aceitar as duas e a documentação sempre mostra
  a longa primeiro. Ver A-18 sobre o nome (`/auditor` minúsculo).

---

## ADR-006 — Intervalo exige unidade explícita

- **Data:** registrada em 2026-07-28 · **Status:** Aceito
- **Decisão:** `30` solto **não** é aceito. A unidade é obrigatória: `30m`, `1h`, `7d`.
- **Razão:** número sem unidade é ambíguo (minutos? horas?) e o erro só aparece
  depois, num agendamento errado difícil de perceber.
- **Consequência:** o parser rejeita intervalo sem unidade com mensagem acionável,
  mostrando as formas válidas. As unidades aceitas precisam ser fechadas no `SPEC.md`.

---

## ADR-007 — Arquivo de agente: produto em `prompts/` e `docs/`, repositório na raiz

- **Data:** 2026-07-28 · **Status:** Aceito
- **Contexto:** este repositório desenvolve um agente **e** é desenvolvido por
  agentes. Os dois papéis colidiram no nome dos arquivos: `AGENTS.md` (raiz) era o
  prompt de runtime do produto e `AGENT.md` (raiz) era a especificação desse mesmo
  prompt — dois arquivos separados por uma letra, mais o `CLAUDE.md` do repositório.
- **O problema não era estético.** `AGENTS.md` na raiz é carregado
  **automaticamente** por ferramentas de agente. Como o conteúdo dizia "Você é o
  AUDITOR, execute UM ciclo de auditoria", qualquer sessão aberta neste repositório
  passava a se comportar como se fosse o produto em execução, em vez de trabalhar no
  repositório. Além disso, um agente seguindo a convenção da casa (`AGENTS.md` =
  espelho do `CLAUDE.md`) sobrescrevia o arquivo — o que de fato aconteceu durante a
  revisão inicial.
- **Decisão:**
  - `prompts/auditor-system.md` — prompt de runtime (era `AGENTS.md`).
  - `docs/contrato-subagente.md` — especificação do contrato (era `AGENT.md`).
  - `CLAUDE.md` + `AGENTS.md` na raiz voltam a ser **espelhados**, do repositório,
    como nos demais projetos da casa.
- **Regra geral:** artefato que descreve o **produto** nunca mora na raiz com nome
  que uma ferramenta carrega sozinha.
- **Consequência:** o pacote de distribuição da skill precisa levar
  `prompts/auditor-system.md` para onde a plataforma alvo espera o arquivo de
  entrada — o mapeamento entra no adaptador de cada plataforma (P-07).
- **Reversível:** os dois arquivos foram movidos com `git mv`; o histórico segue.

---

## ADR-008 — Scheduler: mecanismo nativo primeiro, auto-instalação como último recurso

- **Data:** 2026-07-28 · **Status:** Aceito · **Substitui:** ADR-004
- **Contexto:** o ADR-004 tratava auto-instalação de gatilho como comportamento
  padrão em ShvIA, com o argumento de que a plataforma é do mantenedor. Dois furos:
  o eixo da autorização estava errado (A-02) e a premissa de que a plataforma não
  agenda estava desatualizada (A-13).
- **Fato observado:** o Claude Code expõe hoje as cinco primitivas de que o AUDITOR
  precisa — **skills**, **subagentes**, **hooks**, **execução recorrente por
  intervalo** e **rotinas agendadas** (cron). Constatado a partir das capacidades
  disponíveis na sessão de 2026-07-28. O equivalente no ShvIA **ainda não foi
  validado** — é trabalho de F0.
- **Decisão:**
  1. **Usar sempre o mecanismo nativo e visível da plataforma.** Auto-instalação é
     **último recurso**, não política padrão. `auto_scheduler` tem default `false`
     em **qualquer** plataforma, ShvIA inclusive.
  2. **Quem autoriza é o dono do repositório e da máquina auditada** — não quem
     escreveu a plataforma. Controlar o runner não dá permissão sobre o alvo.
  3. Instalado o gatilho, registrar em `.auditor/scheduler.json` com o comando exato
     de remoção; desinstalação em **um passo** (`/auditor uninstall`).
  4. Nunca usar mecanismo invisível: shell rc, systemd de usuário, `~/.profile`.
- **Razão:** instalar execução recorrente é criar **persistência** na máquina do
  alvo — legítimo aqui, mas mecanicamente indistinguível do que um malware faz. Se a
  plataforma já oferece um mecanismo visível, usá-lo elimina o risco em vez de
  administrá-lo.
- **Consequência:** boa parte do risco de segurança do projeto deixa de existir por
  construção. O que resta é o mapeamento das primitivas por plataforma (F0).

---

## ADR-009 — Conteúdo do repositório auditado é dado, nunca instrução

- **Data:** 2026-07-28 · **Status:** Aceito
- **Contexto:** o AUDITOR lê conteúdo controlado por terceiros — código, comentários,
  README, mensagens de commit, nomes de branch, descrições de PR — e tem escrita e,
  sob configuração, poder de abrir PR. A proposta original não tratava disso e
  chegava a **piorar**: mandava "respeitar instruções do repositório, como
  `AGENTS.md`, `CLAUDE.md`", ou seja, obedecer arquivos do alvo (achado A-03).
- **Decisão:**
  1. Todo conteúdo do repositório auditado é **dado a ser analisado**, nunca
     instrução a ser obedecida. Texto endereçado ao agente vira **achado**, não ação.
  2. Os arquivos do alvo que podem alterar o comportamento do AUDITOR formam **lista
     fechada** — `.auditor/config.yml`, `AGENTS.md`, `CLAUDE.md`, `AGENT.md` — e só
     podem **restringir** permissão, **nunca ampliar**. Pedido de ampliação é
     ignorado e registrado como achado.
  3. Nenhuma ação de escrita, PR/issue ou instalação de gatilho pode ser originada
     por texto lido do repositório. Vem da configuração, sempre.
- **Consequência:** exige fixtures de regressão com injeção plantada em README,
  comentário e mensagem de commit — e o teste precisa falhar quando o controle for
  desligado (F3).

---

## Decisões pendentes

Numeradas para poder referenciar. As sete primeiras vêm do `README.md`; P-08 a P-11
foram levantadas na [revisão inicial](revisao-inicial.md).

| # | Pendência | Bloqueia | Referência |
|---|---|---|---|
| **P-01** | Catálogo real de modelos por plataforma, com fallbacks | `contrato-subagente.md` | A-01 |
| **P-02** | Escopo: repositório inteiro ou só mudanças versionadas em Git | `SPEC.md` | — |
| **P-03** | Cadência e formato da promoção de `.auditor/` para `docs/` | Desenho | A-14 |
| **P-04** | Branches, merge commits e arquivos não rastreados na detecção | Estado | A-09 |
| **P-05** | Retenção de relatórios e política de dados sensíveis (`retain_days`) | `SPEC.md` | T-01 |
| **P-06** | Onde o gatilho instalado persiste, por plataforma | ADR-008 | T-04 |
| **P-07** | Contrato exato de entrada/saída por plataforma | `contrato-subagente.md` | A-11 |
| **P-08** | `.auditor/` é versionado, ignorado ou híbrido | Tudo | A-08 |
| **P-09** | Stack do executor/harness (Python, Node, Rust, shell) | Implementação | — |
| **P-10** | Licença e formato de distribuição da skill | Publicação | A-17 |
| **P-11** | Gatilho por relógio, por atividade (hook) ou os dois | Desenho | A-07 |

**P-12 — resolvida** em 2026-07-28 pelo ADR-007 (`AGENTS.md` × `AGENT.md`).

### Divergências normativas — reconciliadas em `0.2.0`

O prompt de runtime e o `README.md` são ambos normativos e discordavam em quatro
pontos. Resolvidos:

| Ponto | Era, no prompt | Ficou | Achado |
|---|---|---|---|
| Tipo de `open_pr_issue` | `true` (booleano) | `off`/`ask`/`always`, default `ask` (ADR-003) | A-20 |
| Local do `config.yml` | raiz do repo auditado | `.auditor/config.yml` | A-21 |
| Resumo cumulativo | `.auditor/summary.md` | `.auditor/index.md` | A-22 |
| Chave `auto_fix` | mencionada como flag desligado | **removida** — habilitar exige ADR próprio | A-23 |

O booleano não conseguia expressar `ask`, que é o default seguro; e `auto_fix`
habilitaria justamente o que o escopo da v1 proíbe (o agente editar código sozinho,
em ciclo). Em caso de conflito futuro, **ADR vence** — é onde a decisão foi
registrada. Onde não há ADR, decidir e registrar antes de implementar.

> Fechar uma pendência = escrever o ADR correspondente **aqui**, marcar a linha como
> resolvida apontando para ele, e bumpar `version.md`.
