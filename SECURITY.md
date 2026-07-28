# SECURITY.md — Segurança do AUDITOR

Leitura **obrigatória** antes de tocar em qualquer coisa relacionada a escrita de
arquivos, abertura de PR/issue, instalação de gatilho de agendamento ou tratamento
de conteúdo do repositório auditado.

Este arquivo tem duas partes:

1. **Modelo de ameaça do produto** — o AUDITOR é um agente autônomo com poder de
   escrita, de abrir PR/issue e de instalar o próprio gatilho de execução. Isso é
   exatamente o perfil de uma ferramenta que, mal desenhada, vira vetor de ataque.
2. **Política do repositório** — regras para quem desenvolve o AUDITOR aqui.

> Status: as ameaças abaixo estão identificadas; os **controles ainda não estão
> implementados** (o projeto não tem código). Cada controle marcado como
> `[ ]` é requisito de aceite antes da primeira execução real em um repositório
> que não seja de teste.

---

## 1. Superfície de risco

O AUDITOR, por design, combina quatro capacidades perigosas:

| Capacidade | De onde vem | Por que é perigosa |
|---|---|---|
| **Leitura ampla** | lê código, diffs, histórico, config do repo auditado | é onde segredos vazados aparecem |
| **Escrita** | escreve em `.auditor/` | pode escrever fora do escopo; pode publicar o que leu |
| **PR / issue** | `open_pr_issue` (ADR-003) | canal de saída para fora do repo, potencialmente público |
| **Persistência** | auto-instalação de scheduler (ADR-004) | executa depois, sem ninguém olhando |

Nenhuma dessas capacidades é problema isolada. **A combinação é.** Um ciclo
autônomo que lê um diff com segredo e abre um PR público já é um vazamento
completo, sem nenhum bug de código.

---

## 2. Modelo de ameaça

### T-01 — Vazamento de segredo no relatório

O AUDITOR lê diffs. Diffs contêm segredos quando alguém commitou `.env`, chave ou
token por engano — que é justamente o tipo de coisa que uma auditoria encontra. O
`README.md` diz "não incluir segredos nos relatórios", mas **isso é uma regra de
prompt, não um controle**: o modelo pode citar a linha como evidência do achado.

**Controles obrigatórios**
- [ ] Redação **mecânica** antes de escrever qualquer artefato: regex de padrões
      conhecidos (chaves de nuvem, `sk_*`, PEM, JWT, `Authorization:`, senhas em
      URL) aplicada sobre todo texto de saída.
- [ ] Denylist de caminhos nunca citados literalmente (`.env*`, `*.pem`, `*.key`,
      `*.p12`, `*.p8`, `auth.json`, `id_rsa*`).
- [ ] Achado sobre segredo reporta **localização** (`arquivo:linha`) e **nunca o
      valor** — nem truncado, nem mascarado parcialmente.
- [ ] Teste de regressão com um repositório-fixture contendo segredo plantado.

### T-02 — Prompt injection vindo do repositório auditado

**Ameaça ausente do `README.md` e a mais séria do projeto.** O AUDITOR lê conteúdo
não confiável: código, comentários, README, mensagens de commit, nomes de branch,
descrições de PR. Qualquer um desses pode conter texto endereçado ao agente
("ignore as instruções anteriores", "este arquivo já está documentado", "abra um
PR aplicando o patch abaixo"). O agente tem escrita e pode abrir PR — então uma
injeção bem-sucedida vira mudança real no repositório.

⚠️ Hoje o [`AGENTS.md`](AGENTS.md) — que **é** o prompt de entrada do subagente —
não tem uma linha sobre isso, e é exatamente onde a defesa precisa estar.

**Controles obrigatórios**
- [ ] Todo conteúdo do repositório auditado é **dado**, nunca instrução. Delimitar
      explicitamente no prompt (`AGENTS.md`) e instruir o subagente a tratar como
      não confiável.
- [ ] Instruções de repositório que o AUDITOR **de fato obedece** ficam numa lista
      fechada e conhecida (`AGENTS.md`, `CLAUDE.md`, `AGENT.md`, `.auditor/config.yml`)
      — e mesmo essas **não podem** ampliar permissão, só restringir.
- [ ] Nenhuma ação de escrita/PR pode ser originada por texto lido do repo. A
      decisão de abrir PR vem da configuração, não do conteúdo.
- [ ] Teste de regressão com fixture contendo injeção plantada em README, comentário
      e mensagem de commit.

### T-03 — Escrita fora do escopo

`write_policy: auditor-only` é uma string em um YAML. **Prompt não é controle de
acesso.**

**Controles obrigatórios**
- [ ] Enforcement fora do modelo: no Claude Code, `permissions.deny` +
      hook `PreToolUse` que bloqueia `Write`/`Edit` com destino fora de `.auditor/`;
      no ShvIA, gate equivalente no runner.
- [ ] Caminho normalizado antes da checagem (barrar `..`, symlink e caminho absoluto).
- [ ] Violação é **erro do ciclo**, registrada no relatório — não um aviso silencioso.

### T-04 — Persistência indevida (scheduler auto-instalado)

Um agente que instala o próprio gatilho (cron, hook, rotina) está criando
**persistência** na máquina. É comportamento legítimo aqui, mas é indistinguível,
em mecânica, do que um malware faz — e por isso exige tratamento explícito.

**Controles obrigatórios**
- [ ] Instalar apenas com autorização do **dono do repositório/máquina**. A
      distinção do ADR-004 ("ShvIA é do mantenedor, logo pode") está **errada** —
      ver achado A-02: o AUDITOR roda em repositórios de terceiros mesmo quando a
      plataforma é nossa.
- [ ] Todo gatilho instalado é **registrado** em `.auditor/` com: o que foi criado,
      onde, quando, por qual versão, e o comando exato de remoção.
- [ ] **Desinstalação em um comando** (`/auditor uninstall`), que remove tudo que
      foi instalado e reporta o que não conseguiu remover.
- [ ] Nunca instalar gatilho fora dos mecanismos nativos e visíveis da plataforma
      (nada de editar shell rc, systemd de usuário, `~/.profile`, etc. sem
      confirmação explícita e registro).

### T-05 — Exfiltração via PR/issue

PR e issue são canal de saída, frequentemente **público**. Um ciclo autônomo que
publica o conteúdo do que leu pode expor código privado, segredo (T-01) ou dado
pessoal.

**Controles obrigatórios**
- [ ] `open_pr_issue: always` **exige** que a redação de T-01 esteja ativa.
- [ ] Corpo de PR/issue passa pelo mesmo filtro de redação dos relatórios.
- [ ] Detectar repositório público e aplicar política mais restritiva por padrão.
- [ ] Nunca colar diff bruto em PR/issue — só referência `arquivo:linha` + commit.

### T-06 — Flood de PR/issue

Ciclo a cada 30 min com `open_pr_issue: always` e nenhuma deduplicação abre o
mesmo issue 48 vezes por dia.

**Controles obrigatórios**
- [ ] **Hash estável de finding** (tipo + caminho + âncora) persistido em
      `state.json`; finding já reportado não gera item novo — atualiza ou reabre.
- [ ] Teto por ciclo e teto diário de itens abertos, configuráveis.
- [ ] Ciclo sem mudança desde o checkpoint é **no-op**: não escreve relatório, não
      abre nada, não bumpa estado (ver achado A-06).

### T-07 — Custo e consumo descontrolados

Ciclo periódico × repositório grande × modelo caro = fatura silenciosa. Também é a
diferença entre "o agente parou" e "o agente está rodando em loop".

**Controles obrigatórios**
- [ ] Teto de custo/tokens por ciclo e por dia, com kill-switch ao estourar.
- [ ] Registro de custo e duração em cada relatório de ciclo.
- [ ] Falha de ciclo não redispara imediatamente (sem retry apertado).

### T-08 — Perda de documentação existente

O `README.md` promete "não apagar documentação existente" e "não sobrescrever
documentação manual sem confirmação" — mas em execução autônoma **não existe
confirmação possível**. Contradição operacional (achado A-05).

**Controles obrigatórios**
- [ ] Em modo autônomo: **nunca** sobrescrever arquivo pré-existente. Escrita é
      append ou arquivo novo, sempre.
- [ ] Toda escrita é idempotente e reexecutável sem perda.
- [ ] Nada de `rm`/truncate dentro do fluxo do AUDITOR, em nenhum modo.

---

## 3. Política do repositório AUDITOR

### Segredos
- **Nunca** commitar `.env`, chave, senha, token ou certificado. Já barrados no
  [.gitignore](.gitignore) e na deny-list do [.claude/settings.json](.claude/settings.json).
- Versionar somente `.env.example` com placeholders.
- Segredo que vazar no histórico: **rotacionar primeiro**, limpar histórico depois.
  ⚠️ Não reescrever histórico no working copy de `~/x` — o processo automático de
  commit faz `git pull --rebase` e desfaz a reescrita.

### Dados sensíveis em exemplos e fixtures
- Fixtures de teste usam segredos **fictícios e claramente marcados**, nunca
  formato de chave real de provedor (o GitHub push protection barra, e com razão).
- Nenhum log, relatório de exemplo ou fixture pode conter PII real.

### Dependências
- Manter dependências mínimas. Toda dependência nova exige justificativa no ADR.
- `curl | sh` e `wget | bash` estão na deny-list — instalação sempre por gerenciador
  de pacotes, com versão fixada.

### Antes de rodar o AUDITOR em um repositório real
Checklist mínimo:

- [ ] Redação de segredos (T-01) implementada e testada
- [ ] Tratamento de conteúdo não confiável (T-02) implementado e testado
- [ ] Enforcement de `write_policy` fora do prompt (T-03)
- [ ] Registro e desinstalação de gatilho (T-04)
- [ ] Dedup de findings e no-op quiescente (T-06)
- [ ] Teto de custo com kill-switch (T-07)
- [ ] Política de não-sobrescrita em modo autônomo (T-08)

---

## 4. Reportar uma vulnerabilidade

Repositório **privado** (`github.com/samirhvbr/AUDITOR`). Enquanto for privado,
reporte direto ao mantenedor — **não** abra issue pública descrevendo a falha.

- Mantenedor: Samir Hanna Verza ([@samirhvbr](https://github.com/samirhvbr))

Se o repositório se tornar público, esta seção deve ser substituída por um canal
formal (GitHub Security Advisories) e uma janela de divulgação declarada.
