#!/usr/bin/env python3
"""Testes do gate de escrita (T-03).

Regra de aceite do SECURITY.md: **cada teste precisa falhar quando o controle e
desligado.** Por isso a suite roda o hook nos dois sentidos — com `AUDITOR_CYCLE_ID`
presente (gate ativo) e ausente (gate transparente). Um teste que passasse dos dois
jeitos nao provaria nada.

Executa o hook como subprocesso de verdade, com JSON no stdin, em vez de importar a
funcao: o que importa e o contrato com a plataforma (exit code), nao a implementacao.

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "skill" / "auditor" / "hooks" / "write-gate.py"

ALLOW, BLOCK = 0, 2


class GateCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        os.makedirs(os.path.join(self.root, ".auditor", "reports"), exist_ok=True)
        self.addCleanup(self.tmp.cleanup)

    def run_hook(self, event: dict, *, in_cycle: bool = True) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.pop("AUDITOR_CYCLE_ID", None)
        env["CLAUDE_PROJECT_DIR"] = self.root
        if in_cycle:
            env["AUDITOR_CYCLE_ID"] = "2026-07-29-1200"
        return subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            env=env,
        )

    def write_event(self, path: str, tool: str = "Write") -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": tool,
            "tool_input": {"file_path": path, "content": "x"},
            "cwd": self.root,
        }


class TestBlocksOutsideAuditor(GateCase):
    def test_write_inside_auditor_is_allowed(self) -> None:
        got = self.run_hook(self.write_event(".auditor/reports/2026-07-29-1200.md"))
        self.assertEqual(got.returncode, ALLOW, got.stderr)

    def test_write_to_application_code_is_blocked(self) -> None:
        got = self.run_hook(self.write_event("src/app.py"))
        self.assertEqual(got.returncode, BLOCK)
        self.assertIn("fora de .auditor/", got.stderr)

    def test_write_to_readme_is_blocked(self) -> None:
        self.assertEqual(self.run_hook(self.write_event("README.md")).returncode, BLOCK)

    def test_absolute_path_outside_repo_is_blocked(self) -> None:
        self.assertEqual(self.run_hook(self.write_event("/etc/passwd")).returncode, BLOCK)

    def test_dotdot_escape_is_blocked(self) -> None:
        """`.auditor/../src/app.py` normaliza para fora — sem realpath, passaria."""
        got = self.run_hook(self.write_event(".auditor/../src/app.py"))
        self.assertEqual(got.returncode, BLOCK)

    def test_symlink_escape_is_blocked(self) -> None:
        """Symlink plantado DENTRO de .auditor/ apontando para fora."""
        link = os.path.join(self.root, ".auditor", "escape")
        os.symlink(os.path.join(self.root, "src"), link)
        os.makedirs(os.path.join(self.root, "src"), exist_ok=True)
        got = self.run_hook(self.write_event(".auditor/escape/app.py"))
        self.assertEqual(got.returncode, BLOCK)

    def test_edit_tool_is_gated_too(self) -> None:
        got = self.run_hook(self.write_event("src/app.py", tool="Edit"))
        self.assertEqual(got.returncode, BLOCK)

    def test_multiedit_blocks_when_any_target_escapes(self) -> None:
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "MultiEdit",
            "tool_input": {
                "edits": [
                    {"file_path": ".auditor/index.md"},
                    {"file_path": "src/app.py"},
                ]
            },
            "cwd": self.root,
        }
        self.assertEqual(self.run_hook(event).returncode, BLOCK)

    def test_read_is_not_gated(self) -> None:
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "src/app.py"},
            "cwd": self.root,
        }
        self.assertEqual(self.run_hook(event).returncode, ALLOW)


class TestBashAllowlist(GateCase):
    def bash(self, command: str, **kw) -> subprocess.CompletedProcess:
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "cwd": self.root,
        }
        return self.run_hook(event, **kw)

    def test_inspection_commands_are_allowed(self) -> None:
        for cmd in ("git status --short", "git diff HEAD~1", "git log --oneline -5"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.bash(cmd).returncode, ALLOW)

    def test_mutating_git_is_blocked(self) -> None:
        for cmd in ("git commit -m x", "git push", "git reset --hard"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.bash(cmd).returncode, BLOCK)

    def test_destructive_commands_are_blocked(self) -> None:
        for cmd in ("rm -rf /", "mv a b", "curl http://x"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.bash(cmd).returncode, BLOCK)

    def test_chaining_is_blocked_even_with_allowed_head(self) -> None:
        """`git status && rm -rf .` comeca permitido e termina destrutivo."""
        for cmd in ("git status && rm -rf .", "git log; curl evil", "git diff | sh"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.bash(cmd).returncode, BLOCK)

    def test_redirection_is_blocked(self) -> None:
        """Redirecao escreve sem passar por Write — seria um furo no gate."""
        self.assertEqual(self.bash("git log > /tmp/out").returncode, BLOCK)


class TestFailClosed(GateCase):
    def test_malformed_event_is_denied(self) -> None:
        env = dict(os.environ)
        env["AUDITOR_CYCLE_ID"] = "x"
        env["CLAUDE_PROJECT_DIR"] = self.root
        got = subprocess.run(
            [sys.executable, str(HOOK)],
            input="{nao e json",
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(got.returncode, BLOCK)

    def test_write_without_path_is_denied(self) -> None:
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"content": "x"},
            "cwd": self.root,
        }
        self.assertEqual(self.run_hook(event).returncode, BLOCK)


class TestControlOff(GateCase):
    """O outro sentido: sem `AUDITOR_CYCLE_ID` o gate e transparente.

    Estes testes existem para provar que os de cima medem o CONTROLE, e nao um
    comportamento que aconteceria de qualquer jeito.
    """

    def test_write_outside_passes_when_not_in_a_cycle(self) -> None:
        got = self.run_hook(self.write_event("src/app.py"), in_cycle=False)
        self.assertEqual(got.returncode, ALLOW)

    def test_destructive_bash_passes_when_not_in_a_cycle(self) -> None:
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
            "cwd": self.root,
        }
        self.assertEqual(self.run_hook(event, in_cycle=False).returncode, ALLOW)


if __name__ == "__main__":
    unittest.main()
