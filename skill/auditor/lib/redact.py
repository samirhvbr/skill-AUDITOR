#!/usr/bin/env python3
"""Redacao mecanica de segredos (T-01 do SECURITY.md).

Por que isto existe como codigo e nao como regra de prompt: o AUDITOR le diffs, e
diffs contem segredo justamente quando alguem commitou `.env` ou chave por engano —
que e o caso que a auditoria precisa reportar. O comportamento natural do modelo ao
reportar e citar a linha como evidencia. Regra no prompt reduz a chance; nao impede.

Com `.auditor/` versionado (ADR-010), um segredo que escape para um relatorio vira
artefato commitado e pushado — e o historico do git e permanente. Por isso este
filtro roda sobre TODO texto de saida antes de qualquer escrita, PR ou issue.

Uso:
    from redact import redact, is_sensitive_path
    clean, n = redact(text)

Sem dependencias externas: precisa rodar em qualquer ambiente que execute a skill.
"""

from __future__ import annotations

import re
from typing import NamedTuple

PLACEHOLDER = "[REDACTED:{kind}]"

# Cada regra e (nome, regex, grupo-a-preservar).
# O grupo preservado mantem o contexto legivel (ex.: o nome da variavel) para o
# achado continuar util; o valor some inteiro. Nunca mascarar parcialmente: prefixo
# de chave + tamanho ja e informacao suficiente para um ataque, e mascara parcial
# passa a falsa sensacao de seguranca.
_RULES: list[tuple[str, re.Pattern[str], int]] = [
    (
        "pem",
        re.compile(
            r"-----BEGIN[A-Z ]*PRIVATE KEY-----.*?-----END[A-Z ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
        0,
    ),
    (
        "jwt",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
        0,
    ),
    (
        "aws-access-key",
        re.compile(r"\b(?:AKIA|ASIA|AROA|AIDA)[A-Z0-9]{16}\b"),
        0,
    ),
    (
        "github-token",
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        0,
    ),
    (
        "slack-token",
        re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
        0,
    ),
    (
        "google-api-key",
        re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b"),
        0,
    ),
    (
        "stripe-like",
        re.compile(r"\b[sprk]k_(?:live|test)_[A-Za-z0-9]{10,}\b"),
        0,
    ),
    (
        "authorization-header",
        re.compile(
            r"(?i)\b(authorization\s*:\s*)(?:bearer|basic|token)\s+[A-Za-z0-9._~+/=-]{8,}"
        ),
        1,
    ),
    (
        "url-credentials",
        re.compile(r"\b([a-zA-Z][a-zA-Z0-9+.-]*://[^\s:@/]+:)[^\s@/]+(@)"),
        None,  # tratamento especial: preserva grupos 1 e 2
    ),
    (
        "assigned-secret",
        re.compile(
            r"""(?ix)
            \b(
              [A-Z0-9_]*
              (?: SECRET | PASSWD | PASSWORD | TOKEN | API[_-]?KEY | ACCESS[_-]?KEY
                | PRIVATE[_-]?KEY | CLIENT[_-]?SECRET | DSN | CREDENTIAL[S]? )
              [A-Z0-9_]*
            )
            (\s*[:=]\s*)
            (["']?)
            ([^\s"'#,;]{6,})
            \3
            """
        ),
        None,  # tratamento especial: preserva nome + separador
    ),
]

# Caminhos que nunca sao citados literalmente num artefato. O achado reporta que o
# arquivo existe e onde, nunca o conteudo.
_SENSITIVE_PATHS = re.compile(
    r"""(?ix)
    (?:^|/)
    (?:
        \.env(?:\.[A-Za-z0-9_-]+)?
      | auth\.json
      | id_rsa(?:\.[A-Za-z0-9_-]+)?
      | id_ed25519(?:\.[A-Za-z0-9_-]+)?
      | .*\.(?: pem | key | p12 | p8 | pfx | jks | keystore )
    )
    $
    """
)


class Redaction(NamedTuple):
    kind: str
    count: int


def is_sensitive_path(path: str) -> bool:
    """True quando o caminho aponta para um arquivo cujo CONTEUDO nunca deve ser
    citado. O caminho em si pode (e deve) aparecer no achado."""
    return bool(_SENSITIVE_PATHS.search((path or "").replace("\\", "/")))


def redact(text: str) -> tuple[str, list[Redaction]]:
    """Remove segredos de `text`.

    Retorna o texto limpo e a lista do que foi removido, por tipo. A contagem existe
    para o relatorio poder dizer "3 valores redigidos" sem revelar nada — silenciar a
    redacao seria esconder que havia segredo ali.
    """
    if not text:
        return text or "", []

    counts: dict[str, int] = {}

    def bump(kind: str) -> str:
        counts[kind] = counts.get(kind, 0) + 1
        return PLACEHOLDER.format(kind=kind)

    out = text
    for kind, pattern, keep in _RULES:
        if kind == "url-credentials":
            out = pattern.sub(lambda m: m.group(1) + bump(kind) + m.group(2), out)
        elif kind == "assigned-secret":
            out = pattern.sub(
                lambda m: m.group(1) + m.group(2) + m.group(3) + bump(kind) + m.group(3),
                out,
            )
        elif keep:
            out = pattern.sub(lambda m: m.group(keep) + bump(kind), out)
        else:
            out = pattern.sub(lambda m: bump(kind), out)

    return out, [Redaction(k, c) for k, c in sorted(counts.items())]


def assert_clean(text: str, where: str = "output") -> str:
    """Redige e falha se algo foi encontrado onde nao deveria haver segredo nenhum.

    Usado no caminho de PR/issue, onde o custo de vazar e maior: melhor abortar a
    publicacao do que publicar um texto que precisou ser redigido — se precisou, o
    ciclo montou o texto errado.
    """
    clean, found = redact(text)
    if found:
        kinds = ", ".join(f"{r.kind}x{r.count}" for r in found)
        raise ValueError(
            f"segredo detectado em {where} ({kinds}); publicacao abortada. "
            "Reporte a localizacao do achado, nunca o valor."
        )
    return clean


if __name__ == "__main__":  # pragma: no cover - utilitario de linha de comando
    import sys

    data = sys.stdin.read()
    clean, found = redact(data)
    sys.stdout.write(clean)
    if found:
        summary = ", ".join(f"{r.kind}x{r.count}" for r in found)
        sys.stderr.write(f"redigido: {summary}\n")
