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

- **Data:** registrada em 2026-07-28 · **Status:** ⚠️ **Em revisão**
- **Contexto:** a proposta assume que uma skill não executa sozinha em intervalos e
  que, sem um gatilho externo, o AUDITOR vira um comando manual.
- **Decisão original:** quando não houver scheduler nem spec contrária no projeto
  auditado, o AUDITOR **tenta instalar o gatilho automaticamente**, de forma
  registrada e reversível. Em **ShvIA** isso é o comportamento padrão; em
  plataformas de terceiros, exige confirmação explícita do usuário.
- **Por que está em revisão — dois problemas:**
  1. **Eixo errado** (achado A-02): quem autoriza persistência é o **dono do
     repositório/máquina alvo**, não o autor da plataforma. O AUDITOR rodando no
     ShvIA pode estar auditando repositório de terceiro.
  2. **Premissa desatualizada** (achado A-13): o Claude Code já oferece `/loop` e
     rotinas agendadas. Se confirmado, auto-instalação deixa de ser política padrão
     e vira último recurso.
- **Encaminhamento:** validar A-13 e reescrever este ADR. Até lá, tratar
  auto-instalação como **desligada por padrão** em qualquer plataforma.

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

## Decisões pendentes

Numeradas para poder referenciar. As sete primeiras vêm do `README.md`; P-08 a P-11
foram levantadas na [revisão inicial](revisao-inicial.md).

| # | Pendência | Bloqueia | Referência |
|---|---|---|---|
| **P-01** | Catálogo real de modelos por plataforma, com fallbacks | `AGENT.md` | A-01 |
| **P-02** | Escopo: repositório inteiro ou só mudanças versionadas em Git | `SPEC.md` | — |
| **P-03** | Se `.auditor/` é consolidado depois em `docs/`, e em que cadência | Desenho | A-14 |
| **P-04** | Branches, merge commits e arquivos não rastreados na detecção | Estado | A-09 |
| **P-05** | Retenção de relatórios e política de dados sensíveis (`retain_days`) | `SPEC.md` | T-01 |
| **P-06** | Onde o gatilho instalado persiste e como é desinstalado | ADR-004 | A-02, T-04 |
| **P-07** | Contrato exato de entrada/saída por plataforma | `AGENT.md` | A-11 |
| **P-08** | `.auditor/` é versionado, ignorado ou híbrido | Tudo | A-08 |
| **P-09** | Stack do executor/harness (Python, Node, Rust, shell) | Implementação | — |
| **P-10** | Licença e formato de distribuição da skill | Publicação | A-17 |
| **P-11** | Gatilho por relógio, por atividade (hook) ou os dois | Desenho | A-07, A-13 |
| **P-12** | Consolidar `AGENTS.md` e `AGENT.md` (nomes quase idênticos, escopos sobrepostos) | Doc | A-19 |

### Divergências normativas abertas

`AGENTS.md` (commit `1cd405a`) e `README.md` são ambos normativos e **discordam** em
quatro pontos. Enquanto não forem reconciliados, qualquer implementação sai errada em
pelo menos um dos dois:

| Ponto | `AGENTS.md` | `README.md` / ADR | Achado |
|---|---|---|---|
| Tipo de `open_pr_issue` | `true` (booleano) | `off`/`ask`/`always` (ADR-003) | A-20 |
| Local do `config.yml` | raiz do repo auditado | `.auditor/config.yml` | A-21 |
| Resumo cumulativo | `.auditor/summary.md` | `.auditor/index.md` | A-22 |
| Chave `auto_fix` | mencionada | não existe, e contraria o escopo da v1 | A-23 |

Em caso de conflito, **ADR vence** — é onde a decisão foi registrada. Onde não há
ADR, decidir e registrar antes de implementar.

> Fechar uma pendência = escrever o ADR correspondente **aqui**, marcar a linha como
> resolvida apontando para ele, e bumpar `version.md`.
