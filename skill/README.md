# `skill/` — o pacote da skill AUDITOR

Implementação da skill para **Claude Code**. É o primeiro adaptador de plataforma
(fase F4); o adaptador ShvIA ainda não existe.

```
skill/auditor/
├── SKILL.md            # a skill (frontmatter + passos do ciclo)
├── config.example.yml  # modelo de .auditor/config.yml
├── hooks/
│   └── write-gate.py   # T-03 — gate de escrita, PreToolUse
└── lib/
    └── redact.py       # T-01 — redação mecânica de segredos
```

O prompt de operação canônico é [`prompts/auditor-system.md`](../prompts/auditor-system.md),
na raiz do repositório (ADR-007). O `SKILL.md` aponta para ele em vez de duplicá-lo.

> ⚠️ **Isto ainda não é um pacote distribuível.** Empacotar exige resolver como o
> prompt canônico viaja junto com a skill instalada, o que é trabalho da fase F6 e
> depende de P-10 (licença e formato de distribuição). Instalar hoje é manual.

---

## Instalar num repositório

### 1. Copiar a skill

```bash
mkdir -p <repo>/.claude/skills
cp -r skill/auditor <repo>/.claude/skills/auditor
cp prompts/auditor-system.md <repo>/.claude/skills/auditor/prompt.md
```

### 2. Preparar o diretório de trabalho

```bash
mkdir -p <repo>/.auditor/reports <repo>/.auditor/findings
cp skill/auditor/config.example.yml <repo>/.auditor/config.yml
```

`.auditor/` é **versionado** (ADR-010) — não adicione ao `.gitignore`. É o que faz o
checkpoint sobreviver a outra máquina e a CI.

### 3. Ativar o gate de escrita

No `.claude/settings.json` do repositório auditado:

```jsonc
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Write|Edit|MultiEdit|NotebookEdit|Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/skills/auditor/hooks/write-gate.py\"",
          "timeout": 5
        }
      ]
    }
  ]
}
```

O gate **só enforça durante um ciclo**, sinalizado por `AUDITOR_CYCLE_ID` no
ambiente. Fora de um ciclo ele é transparente — senão travaria o desenvolvimento
normal do repositório.

---

## O que o gate garante — e o que não garante

**Garante:** durante um ciclo, escrita fora de `.auditor/` é bloqueada antes da
ferramenta rodar, inclusive por `..`, caminho absoluto e symlink plantado dentro de
`.auditor/`. Bash fica restrito a uma allowlist de inspeção, com encadeamento e
redirecionamento recusados. Erro interno **nega** (fail-closed).

**Não garante:** que quem pediu a escrita seja o subagente auditor. A marca é de
ambiente, então prova "estamos num ciclo", não "quem está pedindo". Um hook do Claude
Code não distingue subagentes hoje. A versão estanque depende da plataforma escopar
hooks por subagente, ou do runner enforçar server-side — o que o ShvIA pode fazer
(ADR-002). **Até lá isto é defesa em profundidade, não isolamento.**

---

## Testes

```bash
python3 -m unittest discover -s tests -v
```

36 testes, sem dependência externa. Cobrem os dois sentidos: com o controle ligado
**e** desligado. Um controle testado num sentido só não prova nada — a suíte foi
verificada por mutação (neutralizar `inside()` no gate derruba 7 testes).
