#!/usr/bin/env python3
"""Checagem estrutural dos JSON Schemas em `schemas/`.

⚠️ **Isto NÃO é validação de instância.** Validar um relatório contra o esquema exige
a biblioteca `jsonschema`, que não é dependência do projeto (a stack do executor é a
pendência P-09). Enquanto não houver validador, o critério de pronto da fase F1 —
"um relatório de exemplo valida e um relatório quebrado é rejeitado" — **não está
atendido**.

O que dá para garantir sem dependência, e que pega os erros mais comuns de esquema
escrito à mão: `$ref` apontando para lugar nenhum, campo em `required` que não existe
em `properties`, e `$id` duplicado entre arquivos.

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def load_all() -> dict[str, dict]:
    return {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(SCHEMA_DIR.glob("*.json"))}


def walk(node, path="$"):
    """Percorre o documento inteiro, inclusive dentro de allOf/if/then e $defs."""
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk(value, f"{path}[{i}]")


def resolve_pointer(doc: dict, pointer: str):
    if not pointer.startswith("#/"):
        return None
    node = doc
    for part in pointer[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


class TestSchemasAreWellFormed(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas = load_all()
        self.assertTrue(self.schemas, "nenhum esquema encontrado em schemas/")

    def test_expected_schemas_exist(self) -> None:
        self.assertEqual(
            set(self.schemas),
            {"config.schema.json", "cycle-report.schema.json", "state.schema.json"},
        )

    def test_every_internal_ref_resolves(self) -> None:
        for name, doc in self.schemas.items():
            for path, node in walk(doc):
                ref = node.get("$ref") if isinstance(node, dict) else None
                if isinstance(ref, str) and ref.startswith("#/"):
                    with self.subTest(schema=name, ref=ref):
                        self.assertIsNotNone(
                            resolve_pointer(doc, ref), f"{name}: {path} -> {ref} nao resolve"
                        )

    def test_required_fields_are_declared(self) -> None:
        """Campo em `required` sem entrada em `properties` combinado com
        `additionalProperties: false` produz um esquema impossível de satisfazer."""
        for name, doc in self.schemas.items():
            for path, node in walk(doc):
                if not isinstance(node, dict):
                    continue
                required = node.get("required")
                props = node.get("properties")
                if isinstance(required, list) and isinstance(props, dict):
                    for field in required:
                        with self.subTest(schema=name, field=field):
                            self.assertIn(field, props, f"{name}: {path} exige {field!r} nao declarado")

    def test_ids_are_unique(self) -> None:
        ids = [doc.get("$id") for doc in self.schemas.values()]
        self.assertEqual(len(ids), len(set(ids)), "ha $id duplicado entre esquemas")
        self.assertTrue(all(ids), "todo esquema precisa de $id")

    def test_interval_pattern_rejects_bare_number(self) -> None:
        """ADR-006 em forma de regex: `30` recusado, `30m` aceito."""
        import re

        pattern = self.schemas["config.schema.json"]["$defs"]["interval"]["pattern"]
        rx = re.compile(pattern)
        for good in ("30m", "1h", "7d", "120m"):
            with self.subTest(value=good):
                self.assertTrue(rx.fullmatch(good))
        for bad in ("30", "m", "0m", "30s", "30 m", "-5m", ""):
            with self.subTest(value=bad):
                self.assertIsNone(rx.fullmatch(bad))

    def test_artifact_paths_are_confined_to_auditor(self) -> None:
        """write_policy=auditor-only espelhado no esquema: artefato fora de
        `.auditor/` não é representável numa saída válida."""
        import re

        schema = self.schemas["cycle-report.schema.json"]
        pattern = schema["properties"]["artifacts_written"]["items"]["pattern"]
        rx = re.compile(pattern)
        self.assertTrue(rx.match(".auditor/reports/2026-07-29-1200.md"))
        for bad in ("src/app.py", "README.md", "/etc/passwd", "../.auditor/x.md"):
            with self.subTest(value=bad):
                self.assertIsNone(rx.match(bad))

    def test_observed_finding_requires_file_and_line(self) -> None:
        """A regra de evidência (A-12) precisa estar no esquema, não só no prompt."""
        finding = self.schemas["cycle-report.schema.json"]["$defs"]["finding"]
        rules = finding.get("allOf") or []
        conditions = [
            r for r in rules
            if r.get("if", {}).get("properties", {}).get("kind", {}).get("const") == "observed"
        ]
        self.assertEqual(len(conditions), 1, "falta a regra condicional de 'observed'")
        self.assertEqual(sorted(conditions[0]["then"]["required"]), ["file", "line"])


if __name__ == "__main__":
    unittest.main()
