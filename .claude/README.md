# Perfil de modelo Claude Code — AUDITOR

`.claude/` deste projeto segue o padrão dos repos Blue3/samirhvbr: **perfil de
modelo + postura de permissões**. Hoje o repositório é só documentação — nenhuma
stack de execução foi decidida (ver `docs/decisoes.md` §Pendentes), então a
allow-list é deliberadamente enxuta.

## Arquivos

| Arquivo | Papel |
|---------|-------|
| `settings.json` | Perfil **ativo** (versionado). Opus-only, `defaultMode: plan`, allow-list mínima + deny-list de segurança. |
| `README.md` | Este arquivo. |

Nada de `settings.local.json` versionado — ele está no `.gitignore` de propósito
(padrão da casa desde o sweep de 25/07/2026).

## Perfil ativo

```jsonc
"model": "opus[1m]",        // Opus 5, janela de 1M explícita pelo sufixo
"effortLevel": "xhigh",
"env": {
  "CLAUDE_CODE_SUBAGENT_MODEL": "opus",
  "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-5"
}
```

## Regras que valem lembrar

- **Não adicionar `CLAUDE_CODE_DISABLE_1M_CONTEXT`** aqui — é justamente essa
  variável que derruba a janela para 200K.
- **Effort `max` vai por sessão** (`/effort max` ou `CLAUDE_CODE_EFFORT_LEVEL=max`
  no ambiente). O campo `effortLevel` do JSON só aceita `low`/`medium`/`high`/
  `xhigh`; `max` ali é ignorado.
- `defaultMode: plan` é intencional: neste repo o custo de uma decisão escrita
  errada é alto (documento normativo vira comportamento do agente depois).

## Postura de permissões

**Allow** — só o que é seguro e repetitivo: leitura/escrita de arquivo, git de
inspeção, git de entrega (`add`/`commit`/`push`) e validadores de formato.

**Ask** — tudo que muda a máquina ou fala com o mundo: `sudo`, `crontab`,
`systemctl`, instalação de dependência e `gh pr/issue create`.

> `crontab` e `systemctl` estão em `ask` **de propósito**: o próprio produto que
> este repo especifica instala gatilhos de agendamento (T-04 do `SECURITY.md`).
> Ninguém instala persistência aqui sem o Samir ver.

**Deny** — leitura de segredo, remoção destrutiva, `push --force`, `reset --hard`,
reescrita de histórico e `curl|bash`.

> `git filter-branch` / `filter-repo` estão negados porque o processo automático
> de `~/x` faz `git pull --rebase` e **desfaz** reescrita de histórico no working
> copy vivo — reescrever aqui só quebra o repo.

## Allow-list adicional (quando a stack fechar)

Cole em `permissions.allow` conforme o harness for definido:

```jsonc
// Python
"Bash(python3 -m pytest:*)", "Bash(pytest:*)",
"Bash(ruff check:*)", "Bash(ruff format:*)", "Bash(mypy:*)",

// Node
"Bash(npm run build:*)", "Bash(npm test:*)", "Bash(npx tsc --noEmit:*)",

// Rust
"Bash(cargo check:*)", "Bash(cargo test:*)", "Bash(cargo clippy:*)", "Bash(cargo fmt:*)"
```
