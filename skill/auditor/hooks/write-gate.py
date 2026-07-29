#!/usr/bin/env python3
"""Gate de escrita do AUDITOR — hook PreToolUse (T-03 do SECURITY.md).

`write_policy: auditor-only` e uma string num YAML lido pelo proprio agente que ela
deveria restringir. **Prompt nao e controle de acesso.** Este hook e o controle: roda
fora do modelo, antes da ferramenta executar, e nega o que sair de `.auditor/`.

## Quando enforca

So durante um ciclo de auditoria, sinalizado por `AUDITOR_CYCLE_ID` no ambiente.
Fora de um ciclo o hook e transparente — senao ele travaria o desenvolvimento normal
do proprio repositorio.

⚠️ **Limitacao conhecida, declarada de proposito:** a marca e de ambiente, entao ela
prova "estamos num ciclo", nao "quem esta pedindo a escrita e o subagente auditor".
Um hook do Claude Code nao consegue distinguir subagentes hoje. A versao estanque
depende da plataforma escopar hooks por subagente, ou do runner enforcar (o que o
ShvIA pode fazer server-side, ADR-002). Ate la isto e defesa em profundidade, nao
isolamento — e o `SECURITY.md` diz isso.

## Contrato

Entrada: JSON do evento no stdin (`tool_name`, `tool_input`, `cwd`).
Saida: permitir = exit 0 silencioso. Negar = motivo no stderr e **exit 2**, que e o
codigo que a plataforma le como bloqueio.

**Fail-closed:** qualquer erro interno nega. Um gate de seguranca que abre quando
quebra nao e um gate.
"""

from __future__ import annotations

import json
import os
import shlex
import sys

AUDITOR_DIR = ".auditor"

# Ferramentas que escrevem. Nao ha allowlist de leitura aqui: leitura e livre.
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

# Dentro de um ciclo, Bash so pode inspecionar. Allowlist em vez de denylist porque
# denylist de shell e furada por construcao (`git` com alias, `sh -c`, redirecao,
# encoding). O que nao esta aqui, nao roda.
BASH_ALLOWED = {
    ("git", "status"),
    ("git", "diff"),
    ("git", "log"),
    ("git", "show"),
    ("git", "branch"),
    ("git", "cat-file"),
    ("git", "rev-parse"),
    ("git", "rev-list"),
    ("git", "ls-files"),
    ("git", "blame"),
    ("git", "describe"),
}


def deny(reason: str) -> None:
    sys.stderr.write(f"[auditor:write-gate] BLOQUEADO — {reason}\n")
    sys.exit(2)


def allow() -> None:
    sys.exit(0)


def repo_root(event: dict) -> str:
    raw = (
        os.environ.get("CLAUDE_PROJECT_DIR")
        or event.get("cwd")
        or os.getcwd()
    )
    return os.path.realpath(raw)


def resolve(path: str, root: str) -> str:
    """Caminho absoluto e canonico. `realpath` resolve `..` e symlink — sem isso,
    `.auditor/../../etc/x` ou um symlink plantado dentro de `.auditor/` passariam."""
    candidate = path if os.path.isabs(path) else os.path.join(root, path)
    return os.path.realpath(candidate)


def inside(child: str, parent: str) -> bool:
    try:
        return os.path.commonpath([child, parent]) == parent
    except ValueError:
        # Drives/roots diferentes: nao esta dentro.
        return False


def target_paths(tool: str, tool_input: dict) -> list[str]:
    paths: list[str] = []
    for key in ("file_path", "path", "target_file", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(value)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                value = edit.get("file_path")
                if isinstance(value, str) and value.strip():
                    paths.append(value)
    return paths


def check_bash(command: str) -> None:
    if not command.strip():
        deny("comando bash vazio")

    # Encadeamento esconde o comando real depois do separador. Recusar e mais barato
    # e mais seguro do que tentar analisar cada ramo.
    for sep in ("&&", "||", ";", "|", "\n", "`", "$(", ">", ">>", "<"):
        if sep in command:
            deny(
                f"bash com {sep!r} nao e permitido durante um ciclo; "
                "use um comando de inspecao por vez"
            )

    try:
        parts = shlex.split(command)
    except ValueError as exc:
        deny(f"comando bash nao parseavel ({exc})")
        return

    if not parts:
        deny("comando bash vazio")

    head = tuple(p for p in parts[:2])
    if len(head) < 2 or head not in BASH_ALLOWED:
        allowed = ", ".join(" ".join(c) for c in sorted(BASH_ALLOWED))
        deny(
            f"`{' '.join(parts[:2])}` fora da allowlist de inspecao. "
            f"Permitidos: {allowed}"
        )


def main() -> None:
    # Fora de um ciclo o gate e transparente.
    if not os.environ.get("AUDITOR_CYCLE_ID"):
        allow()

    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    try:
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        deny(f"evento do hook ilegivel ({exc}) — negando por precaucao")
        return

    if not isinstance(event, dict):
        deny("evento do hook em formato inesperado — negando por precaucao")
        return

    tool = event.get("tool_name") or ""
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}

    if tool == "Bash":
        command = tool_input.get("command")
        check_bash(command if isinstance(command, str) else "")
        allow()

    if tool not in WRITE_TOOLS:
        allow()

    root = repo_root(event)
    auditor_root = os.path.realpath(os.path.join(root, AUDITOR_DIR))

    paths = target_paths(tool, tool_input)
    if not paths:
        deny(f"{tool} sem caminho de destino identificavel — negando por precaucao")

    for path in paths:
        resolved = resolve(path, root)
        if not inside(resolved, auditor_root):
            deny(
                f"escrita em {path!r} esta fora de {AUDITOR_DIR}/. "
                "write_policy=auditor-only: o AUDITOR documenta, nao altera o projeto."
            )

    allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - fail-closed e proposital
        deny(f"erro interno do gate ({type(exc).__name__}: {exc})")
