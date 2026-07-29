#!/usr/bin/env python3
"""Testes da redacao de segredos (T-01).

⚠️ **Nenhum valor com formato de credencial real aparece literalmente neste
arquivo.** As amostras sao montadas por concatenacao em tempo de execucao, para o
push protection do GitHub nao barrar o push e para ninguem confundir fixture com
segredo vazado. E a mesma regra que o SECURITY.md impoe: fixture usa valor ficticio,
nunca formato de chave real de provedor.

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skill" / "auditor" / "lib"))

from redact import assert_clean, is_sensitive_path, redact  # noqa: E402

FILLER = "A1b2C3d4E5f6G7h8"


class TestRedactsSecrets(unittest.TestCase):
    def assert_gone(self, text: str, secret: str) -> None:
        clean, found = redact(text)
        self.assertNotIn(secret, clean, "o valor sobreviveu a redacao")
        self.assertTrue(found, "nada foi reportado como redigido")

    def test_aws_access_key(self) -> None:
        secret = "AKIA" + "Q" * 16
        self.assert_gone(f"encontrado {secret} no diff", secret)

    def test_github_token(self) -> None:
        secret = "ghp" + "_" + FILLER + FILLER + "ijkl"
        self.assert_gone(f"token: {secret}", secret)

    def test_jwt(self) -> None:
        secret = "eyJ" + FILLER + "." + FILLER + "abc." + FILLER + "def"
        self.assert_gone(f"Cookie session={secret}", secret)

    def test_pem_block(self) -> None:
        secret = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            + FILLER
            + "\n-----END RSA PRIVATE KEY-----"
        )
        self.assert_gone(f"arquivo continha:\n{secret}\nfim", FILLER)

    def test_url_credentials_keep_host(self) -> None:
        clean, found = redact("DB: postgres://admin:hunter2supersecret@db.local/app")
        self.assertNotIn("hunter2supersecret", clean)
        self.assertIn("db.local", clean, "o host e contexto util e deve sobreviver")
        self.assertIn("postgres://admin:", clean)
        self.assertTrue(found)

    def test_assigned_secret_keeps_variable_name(self) -> None:
        value = "zzz" + "9988776655443322"
        clean, _ = redact(f'API_KEY = "{value}"')
        self.assertIn("API_KEY", clean, "o nome da variavel e o que torna o achado util")
        self.assertNotIn(value, clean)

    def test_authorization_header(self) -> None:
        secret = "Bearer " + FILLER + FILLER
        clean, _ = redact(f"Authorization: {secret}")
        self.assertNotIn(FILLER, clean)
        self.assertIn("Authorization:", clean)

    def test_reports_what_was_removed_without_revealing_it(self) -> None:
        secret = "AKIA" + "Z" * 16
        _, found = redact(f"chave {secret}")
        self.assertEqual([r.kind for r in found], ["aws-access-key"])
        self.assertEqual(found[0].count, 1)
        self.assertNotIn(secret, str(found))

    def test_multiple_occurrences_are_counted(self) -> None:
        a, b = "AKIA" + "W" * 16, "AKIA" + "V" * 16
        _, found = redact(f"{a} e {b}")
        self.assertEqual(found[0].count, 2)


class TestDoesNotOverRedact(unittest.TestCase):
    """Redacao agressiva demais destroi o relatorio: se tudo virar [REDACTED], o
    achado deixa de ser acionavel e alguem desliga o filtro."""

    def test_ordinary_prose_is_untouched(self) -> None:
        text = "O modulo de billing nao tem documentacao desde o commit a1b2c3d."
        clean, found = redact(text)
        self.assertEqual(clean, text)
        self.assertEqual(found, [])

    def test_file_paths_survive(self) -> None:
        text = "config/services.php:42 referencia uma variavel nao documentada"
        self.assertEqual(redact(text)[0], text)

    def test_short_assignments_survive(self) -> None:
        self.assertEqual(redact("timeout = 30")[0], "timeout = 30")

    def test_env_var_name_without_value_survives(self) -> None:
        text = "falta documentar STRIPE_SECRET_KEY no .env.example"
        self.assertEqual(redact(text)[0], text)

    def test_parser_code_with_tokens_variable_survives(self) -> None:
        """Falso positivo real do dogfood do skill-COMMITTER (29/07): variavel
        `tokens` recebendo expressao de codigo. Valor com parenteses e codigo,
        nao segredo — segredo real (AWS, JWT, base64, hex) nao contem ()."""
        for text in (
            'tokens = out.split("\\0")',
            "token = parse_line(raw)",
            "ACCESS_KEYS = load_keys(path)",
        ):
            with self.subTest(text=text):
                self.assertEqual(redact(text)[0], text)


class TestSensitivePaths(unittest.TestCase):
    def test_flags_secret_bearing_files(self) -> None:
        for path in (".env", ".env.production", "storage/oauth.pem", "certs/tls.key",
                     "auth.json", "keys/id_rsa", "app/keystore.p12"):
            with self.subTest(path=path):
                self.assertTrue(is_sensitive_path(path))

    def test_ignores_ordinary_files(self) -> None:
        for path in ("README.md", ".env.example.md", "src/keyboard.py", "docs/pem.md"):
            with self.subTest(path=path):
                self.assertFalse(is_sensitive_path(path))


class TestAssertClean(unittest.TestCase):
    def test_raises_on_secret(self) -> None:
        secret = "AKIA" + "Y" * 16
        with self.assertRaises(ValueError) as ctx:
            assert_clean(f"corpo do PR com {secret}", where="PR")
        self.assertNotIn(secret, str(ctx.exception), "a excecao nao pode vazar o valor")

    def test_passes_clean_text(self) -> None:
        text = "3 arquivos sem documentacao em docs/"
        self.assertEqual(assert_clean(text), text)


class TestControlOff(unittest.TestCase):
    """O outro sentido: sem o filtro, o segredo passa. Prova que os testes acima
    medem o CONTROLE e nao um acaso do texto."""

    def test_secret_survives_without_redaction(self) -> None:
        secret = "AKIA" + "X" * 16
        raw = f"encontrado {secret} no diff"
        self.assertIn(secret, raw)
        self.assertNotIn(secret, redact(raw)[0])


if __name__ == "__main__":
    unittest.main()
