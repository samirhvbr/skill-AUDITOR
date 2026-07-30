# `.auditor/` — diretório de trabalho do AUDITOR

**Versionado de propósito** (ADR-010): o checkpoint precisa sobreviver a outra
máquina e a CI. Consequência direta — relatório aqui é artefato **publicado**, então
a redação de segredos é pré-requisito de qualquer execução, não opcional.

| Arquivo | Papel |
|---|---|
| `config.yml` | opt-in + configuração do ciclo |
| `state.json` | checkpoint (`last_sha`, `last_run`, `last_checked`, `reported[]`) |
| `index.md` | índice cumulativo dos ciclos — atualizado, nunca recriado |
| `reports/` | um relatório por ciclo com mudança (no-op não escreve) |
| `findings/` | lacunas e recomendações pendentes |

Nada aqui é escrito ainda: **não existe executor**. O `~/x/GIT/run.sh` lista quem
optou; o ciclo só roda por `/auditor` numa sessão do Claude Code.
