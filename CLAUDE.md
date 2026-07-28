# AUDITOR — Instruções para Claude Code

> **Leia também:** [README.md](README.md) (proposta e decisões fechadas) ·
> [SECURITY.md](SECURITY.md) (**leitura obrigatória** — modelo de ameaça) ·
> [docs/README.md](docs/README.md) (índice técnico) ·
> [docs/decisoes.md](docs/decisoes.md) (ADRs) ·
> [docs/revisao-inicial.md](docs/revisao-inicial.md) (achados abertos) ·
> [version.md](version.md) (versão + formato de commit).
>
> ⚠️ **Este repo NÃO segue o espelhamento `CLAUDE.md` ↔ `AGENTS.md`** dos demais
> projetos da casa. Aqui o [AGENTS.md](AGENTS.md) é do **produto** — é o prompt de
> entrada que a plataforma lê antes de executar a skill AUDITOR. Quem desenvolve
> este repositório segue **este** arquivo. Ver achado A-19.

---

## 🔄 Antes de começar: `git pull`

**SEMPRE** verifique atualizações remotas antes de escrever ou alterar qualquer
coisa neste repositório:

```bash
git pull          # já está pré-autorizado (allow)
```

Trabalhar sobre uma base desatualizada gera conflitos. Para só inspecionar antes:
`git fetch && git status`.

---

## O que é este repo

**AUDITOR** é uma **skill de auditoria de documentação**: um subagente que roda
em ciclos periódicos sobre um repositório, identifica o que mudou desde o último
checkpoint, avalia se a mudança está documentada e escreve documentação durável
em `.auditor/` — **sem alterar a lógica da aplicação auditada**.

Plataformas-alvo da primeira versão: **Claude** e **ShvIA** (OpenAI fora do
escopo inicial — ADR-001).

---

## Os três arquivos de agente deste repo (não confundir)

| Arquivo | De quem é | Papel |
|---|---|---|
| **`CLAUDE.md`** (este) | do **repositório** | regras para quem **desenvolve** o AUDITOR |
| **`AGENTS.md`** | do **produto** | prompt de entrada que a plataforma lê antes de **executar** a skill (runtime) |
| **`AGENT.md`** | do **produto** | **especificação** do contrato de entrada/saída do subagente (esqueleto) |

`AGENTS.md` e `AGENT.md` têm nomes quase idênticos e escopos que se sobrepõem —
conferir o alvo antes de editar. A consolidação dos dois é a pendência **P-12**.

---

## ⚠️ Estado do projeto: proposta, sem implementação

Hoje o repositório tem **apenas documentação**. Não existe skill, executor, CLI,
teste ou pacote. Ao trabalhar aqui:

- **Não descreva como pronto** o que ainda é proposta. `README.md`, `SPEC.md` e
  `AGENT.md` contêm seções marcadas como esqueleto ou pendentes — respeite as
  marcações.
- **Não feche decisão pendente dentro de um how-to.** Decisão nova vira **ADR**
  em [docs/decisoes.md](docs/decisoes.md), com data e status.
- Antes de propor arquitetura, leia [docs/revisao-inicial.md](docs/revisao-inicial.md):
  os achados abertos já cobrem boa parte das armadilhas.

---

## Padrão de Commits (obrigatório)

Formato: `X.Y.Z - Descrição curta em português`. A versão **sempre** vem de
[`version.md`](version.md) e é bumpada **no mesmo commit** da mudança.

Critério resumido (regra completa em `version.md`):

- **Z** — entrega que muda uma regra, um contrato, um documento normativo, o
  prompt do subagente, permissão do `.claude` ou política de segurança.
- **Y** — novo adaptador de plataforma, quebra de compatibilidade de esquema,
  fase concluída, ADR aceito que muda a direção.
- **X** — release estável distribuível.

**Proibido** `feat:` / `fix:` / `chore:` / `docs:` e mensagens vagas.

---

## Regras do produto (não relitigar sem ADR)

Fechadas na proposta e registradas em [docs/decisoes.md](docs/decisoes.md):

1. **Plataformas v1:** Claude e ShvIA. OpenAI descartado (ADR-001).
2. **ShvIA é customizável** — plataforma sob autoria do mantenedor (ADR-002).
3. **PR/issue permitido**, regido por `open_pr_issue`: `off` / `ask` / `always`
   (ADR-003).
4. **Scheduler:** quando não houver, o AUDITOR tenta instalar o gatilho, de forma
   **registrada e reversível**. Padrão em ShvIA; em plataformas de terceiros só
   com confirmação explícita (ADR-004). Ver o achado **A-02** da revisão — o
   critério correto é o dono do **repositório/máquina**, não a plataforma.
5. **Comando:** forma canônica longa `/auditor every <intervalo> model <modelo>`;
   forma curta `/auditor <intervalo> <modelo>` só como atalho (ADR-005).
6. **Intervalo exige unidade** — `30` solto não é aceito; use `30m`, `1h` (ADR-006).

E o que o AUDITOR **nunca** faz na v1:

- Alterar arquivos da aplicação auditada.
- Apagar ou sobrescrever documentação manual sem confirmação.
- Emitir finding sem evidência (`arquivo:linha` + commit).
- Incluir segredo, token ou PII em relatório, PR ou issue.

---

## Regras de escrita da documentação

- **Idioma do repositório: PT-BR.** Todo `.md` deste projeto é em português.
- **Idioma dos artefatos produzidos pelo AUDITOR: en-US.** O que o subagente
  escreve em `.auditor/` do repositório auditado é em inglês dos EUA. O relatório
  apresentado ao usuário pode seguir o idioma da conversa.
- Documentação técnica durável → `docs/`. Notas de trabalho, escopo, estado e
  handoff → `.continue/`. Contratos normativos → `SPEC.md` (comando/config) e
  `AGENT.md` (contrato do subagente por plataforma).
- Distinga sempre **fato observado**, **inferência** e **recomendação** — é a
  regra que o AUDITOR impõe aos outros; vale aqui dentro também.
- Nunca crie um link para arquivo que não existe. Se o arquivo é futuro, diga que
  é futuro em texto, sem link.

---

## Como o Claude Code deve operar aqui

- **Planeje antes de editar.** `defaultMode` é `plan`. Em tarefa não trivial,
  apresente o plano e a lista de arquivos antes de escrever.
- Faça **mudanças pequenas e atômicas**, um objetivo por commit.
- Ao concluir algo relevante, **atualize `version.md`** (bump + entrada no
  changelog) e o `.continue/estado-atual.md`.
- Se uma decisão pendente bloquear a tarefa: faça tudo que não depende dela,
  registre a pendência explicitamente e pergunte — não escolha por conta própria.
- **Não invente identificador de modelo.** Os ids reais da família Claude são
  `claude-opus-5`, `claude-sonnet-5`, `claude-fable-5` e
  `claude-haiku-4-5-20251001`. O `claude-sonnet-4.6` que aparece no `README.md` é
  placeholder inválido — ver achado **A-01**.

---

## Referências rápidas

- Versão e commits: [version.md](version.md)
- Segurança / modelo de ameaça: [SECURITY.md](SECURITY.md)
- Decisões (ADRs): [docs/decisoes.md](docs/decisoes.md)
- Achados abertos: [docs/revisao-inicial.md](docs/revisao-inicial.md)
- Escopo e fases (proposta): [.continue/escopo-projeto.md](.continue/escopo-projeto.md)
- Estado atual: [.continue/estado-atual.md](.continue/estado-atual.md)
- Perfil do agente: [.claude/README.md](.claude/README.md)
- Remoto: `github.com/samirhvbr/AUDITOR` (privado) · branch padrão `master`
