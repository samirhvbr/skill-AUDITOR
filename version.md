# Versão — AUDITOR

**Versão atual:** `0.1.0`

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

- Criar ou alterar um documento em `docs/`, `SPEC.md` ou `AGENT.md` que **muda
  uma regra** (não vale corrigir redação).
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
git commit -m "0.2.0 - Fecha o contrato de saida do subagente em AGENT.md"
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
