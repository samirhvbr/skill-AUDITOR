# AUDITOR

Skill para executar um subagente de auditoria de código em ciclos periódicos, identificar mudanças recentes sem documentação suficiente e registrar a documentação produzida no diretório `.auditor`.

> Status: proposta em evolução. Decisões parcialmente fechadas: plataformas-alvo (Claude e ShvIA, com OpenAI descartado da primeira versão), permissão de abrir PR/issue, e política de scheduler (criar o gatilho automaticamente quando não houver spec, ao menos em SHVIA, onde há controle do mantenedor). Sintaxe de comando, identificadores exatos de modelo, escopo, retenção e demais pontos seguem em validação na `SPEC.md`.

## Objetivo

A cada ciclo configurado, o AUDITOR deve:

1. identificar o que mudou desde a última auditoria;
2. analisar código, testes, configuração e histórico de mudanças;
3. verificar se as mudanças estão documentadas de forma suficiente;
4. apontar lacunas, inconsistências e riscos;
5. criar ou atualizar documentação dentro de `.auditor`;
6. produzir um relatório resumido para o usuário;
7. salvar estado do ciclo para evitar auditorias duplicadas.

O AUDITOR deve documentar o sistema sem alterar a lógica da aplicação, salvo se uma futura configuração permitir explicitamente correções automáticas.

## Exemplo de uso (ilustrativo)

> **Atenção:** este bloco é **meramente ilustrativo** e precisa ser validado. A sintaxe, os identificadores de modelo e o mecanismo de agendamento ainda não foram confirmados na plataforma alvo — qualquer ajuste pode ser necessário antes do uso real.

```text
/auditor 30m claude-sonnet-4.6
```

Interpretação pretendida:

- `auditor`: ativa ou configura a skill;
- `30m`: intervalo entre ciclos, com unidade explícita;
- `claude-sonnet-4.6`: identificador do modelo solicitado (placeholder; ver `AGENT.md`).

A unidade do intervalo deve ser explícita para evitar ambiguidade. Recomenda-se aceitar a forma longa como forma canônica:

```text
/auditor every 30m model claude-sonnet-4.6
```

E manter a forma curta apenas como atalho documentado:

```text
/auditor 30m claude-sonnet-4.6
```

`30` sem unidade **não** deve ser aceito na primeira versão para evitar ambiguidade.

> A especificação canônica do comando, dos placeholders e do arquivo de configuração será consolidada em `SPEC.md`.

## Plataformas e idioma

- Plataformas-alvo da primeira versão: **Claude** e **ShvIA**. OpenAI foi descartado do escopo inicial.
- ShvIA é uma plataforma sob autoria e controle do mantenedor; pode ser customizada conforme a necessidade do AUDITOR (prompt, contrato de saída, scheduler, etc.).
- Idioma principal dos artefatos: inglês dos EUA (`en-US`).
- O relatório apresentado ao usuário pode seguir o idioma da conversa.
- O nome da skill é `AUDITOR`.

> O contrato detalhado do agente, o identificador de modelo em cada plataforma, o mapeamento de fallbacks e a integração com ShvIA serão detalhados em `AGENT.md`. A sintaxe canônica do comando ficará em `SPEC.md`.

## Escopo da primeira versão

A primeira versão deve ser somente de auditoria e documentação:

- detectar arquivos modificados no ciclo;
- comparar o estado atual com o último estado registrado;
- consultar diffs e histórico Git quando disponíveis;
- localizar documentação existente;
- avaliar README, comentários, changelog, decisões e instruções de execução;
- escrever artefatos em `.auditor`;
- não apagar documentação existente;
- não modificar arquivos da aplicação;
- pedir confirmação antes de qualquer mudança fora de `.auditor`.

## Estrutura proposta de `.auditor`

```text
.auditor/
├── config.yml              # configuração da skill, intervalo e modelo
├── state.json              # último ciclo processado
├── index.md                # índice dos relatórios e decisões
├── reports/
│   └── YYYY-MM-DD-HHMM.md  # relatório de cada ciclo
├── docs/
│   └── ...                 # documentação criada ou complementada
└── findings/
    └── ...                 # lacunas e recomendações pendentes
```

A estrutura pode ser simplificada se a plataforma não permitir múltiplos arquivos.

## Contrato de execução do subagente

Cada execução deve receber um contexto semelhante a:

```text
You are AUDITOR, a documentation-focused code auditing sub-agent.

Review only changes since the previous audit checkpoint. Inspect the repository,
its tests, configuration, and existing documentation. Identify undocumented or
inconsistently documented behavior. Write durable documentation in .auditor using
US English. Do not modify application code. Do not claim a task is complete
without evidence. Report files inspected, findings, artifacts written, and items
requiring user decisions.
```

O agente deve retornar, no mínimo:

- intervalo e identificador do ciclo;
- modelo utilizado;
- período ou commit analisado;
- arquivos inspecionados;
- mudanças encontradas;
- lacunas de documentação;
- arquivos criados/atualizados em `.auditor`;
- limitações e decisões pendentes;
- próximo checkpoint.

## Agendamento

A skill não deve presumir que o modelo consiga executar sozinho em segundo plano. O agendamento precisa ser fornecido por uma camada externa, como:

- scheduler nativo da plataforma;
- tarefa recorrente do ambiente;
- cron ou CI/CD;
- processo controlador que invoca a skill;
- comando manual repetido.

**Política quando não houver scheduler disponível:** o AUDITOR deve tentar instalar um gatilho automaticamente, registrando-o de forma explícita e reversível. Em plataformas onde o mantenedor tem controle (caso de **SHVIA**, onde ShvIA é uma plataforma sob sua autoria), a instalação automática do gatilho é parte do comportamento padrão da skill, desde que não haja uma spec contrária no projeto auditado. Em plataformas de terceiros (ex.: Claude), a instalação automática deve ser feita apenas com confirmação explícita do usuário.

O intervalo (ex.: `30m`) deve ser tratado como configuração, não como garantia de execução. Se mesmo assim não houver como instalar scheduler, `/auditor 30m <model>` deve configurar o intervalo e informar claramente como a execução será disparada.

## Seleção do agente/modelo

A configuração deve separar:

- `agent`: papel especializado, por exemplo `documentation-auditor`;
- `model`: identificador compatível com a plataforma alvo (Claude ou ShvIA);
- `interval`: duração, por exemplo `30m`;
- `scope`: escopo de arquivos e branches;
- `write_policy`: permissão de escrita — na primeira versão, apenas `.auditor`; PR/issue são permitidos apenas sob confirmação ou política explícita.

Exemplo conceitual (Claude):

```yaml
agent: documentation-auditor
model: claude-sonnet-4.6
interval: 30m
language: en-US
write_policy: auditor-only
open_pr_issue: ask
state_source: git
```

Exemplo conceitual (ShvIA — sob autoria do mantenedor, customizável):

```yaml
agent: documentation-auditor
model: shvia-v1   # placeholder; ver AGENT.md
interval: 30m
language: en-US
write_policy: auditor-only
open_pr_issue: ask
state_source: git
auto_scheduler: true   # permitido por padrão em ShvIA; ver seção Agendamento
```

O identificador de modelo deve ser considerado uma **solicitação do usuário**, não uma garantia de que a plataforma o oferece. A skill deve validar a disponibilidade e informar claramente quando houver fallback. O catálogo de modelos válidos por plataforma, fallbacks e regras de prompt vivem em `AGENT.md`.

## Regras de segurança e qualidade

- Nunca inventar mudanças, testes ou fontes consultadas.
- Diferenciar fato observado, inferência e recomendação.
- Não incluir segredos, tokens ou dados sensíveis nos relatórios.
- Não sobrescrever documentação manual sem confirmação.
- Manter histórico dos ciclos.
- Tornar a execução idempotente quando possível.
- Registrar falhas parciais e continuar apenas em escopos seguros.
- Respeitar instruções do repositório, como `AGENTS.md`, `CLAUDE.md`, `AGENT.md` ou equivalentes.
- Tratar código não versionado com uma estratégia explícita, caso o Git não esteja disponível.
- **Permissões de escrita:** por padrão, o agente escreve apenas em `.auditor/`. Abrir PR e/ou issue é permitido, preferencialmente sob confirmação do usuário; quando não houver confirmação possível (execução autônoma via scheduler), o agente deve respeitar a política `open_pr_issue` definida na configuração (`off`, `ask`, `always`).

## Fluxo de um ciclo

1. Carregar configuração e `state.json`.
2. Validar intervalo, agente e modelo.
3. Identificar o checkpoint anterior.
4. Coletar mudanças desde o checkpoint.
5. Ler documentação relacionada às mudanças.
6. Avaliar a cobertura documental.
7. Escrever ou atualizar artefatos em `.auditor`.
8. Atualizar o estado somente após concluir o ciclo.
9. Emitir o relatório ao usuário.
10. Agendar ou aguardar o próximo disparo pela camada externa.

## Critérios de aceite da primeira versão

- A sintaxe de configuração é documentada e validada.
- O agente identifica corretamente o intervalo analisado.
- O relatório lista evidências, não apenas conclusões.
- O agente consegue criar documentação em `.auditor` sem alterar o código da aplicação.
- O estado permite continuar do último checkpoint.
- Falhas de modelo, scheduler ou Git são comunicadas de forma acionável.
- O comportamento é consistente nas plataformas suportadas ou possui adaptadores explícitos.

## Decisões já fechadas

1. **Plataformas da primeira versão:** Claude e ShvIA (OpenAI descartado).
2. **ShvIA:** plataforma sob autoria do mantenedor, customizável.
3. **Abertura de PR/issue:** permitida, regida por `open_pr_issue` (`off` / `ask` / `always`).
4. **Política de scheduler:** quando não houver spec/scheduler, o AUDITOR deve tentar instalar o gatilho automaticamente, com registro explícito e reversível. Em **ShvIA** isso é o comportamento padrão; em outras plataformas exige confirmação do usuário.
5. **Formato do comando:** aceitar forma canônica longa (`/auditor every <interval> model <model>`) e forma curta apenas como atalho (`/auditor <interval> <model>`).
6. **Intervalo sem unidade:** não aceitar `30` solto; exigir unidade explícita (ex.: `30m`, `1h`).

## Decisões ainda necessárias

1. Identificador real e catálogo de modelos válidos para Claude e para ShvIA (com fallbacks).
2. Se o escopo é o repositório inteiro ou somente mudanças versionadas (Git) na primeira versão.
3. Se documentação criada em `.auditor` deve ser consolidada depois em `docs/` ou no README, e em qual cadência.
4. Como lidar com branches, merge commits e arquivos não rastreados na detecção de mudanças.
5. Retenção dos relatórios e política para dados sensíveis (ex.: `retain_days`, redação de segredos).
6. Onde o scheduler/hook instalado pelo AUDITOR deve persistir e como ele é desinstalado.
7. Contrato exato de entrada/saída entre o AUDITOR e cada plataforma (Claude vs. ShvIA).

## Próximos passos sugeridos

1. Consolidar a sintaxe canônica do comando e o esquema do arquivo de configuração em `SPEC.md`.
2. Definir o contrato de entrada/saída do subagente por plataforma em `AGENT.md` (Claude e ShvIA).
3. Implementar o adaptador ShvIA primeiro (controle total do mantenedor) e o adaptador Claude em paralelo como referência.
4. Criar um executor local que faça um ciclo manual reproduzível (CLI ou script), útil para testes e CI.
5. Implementar o estado (`state.json`) e a detecção de mudanças com base em Git.
6. Implementar a escrita segura em `.auditor`, respeitando `write_policy` e `open_pr_issue`.
7. Implementar a política de scheduler: instalar gatilho automaticamente quando ausente, com registro e reversibilidade (especialmente em ShvIA).
8. Adicionar testes com um repositório de exemplo contendo mudanças documentadas e não documentadas.
9. Definir versionamento, distribuição e instalação da skill (registro em `AGENTS.md` / `CLAUDE.md` / `AGENT.md` da plataforma).
10. Documentar retenção, redação de segredos e política de dados sensíveis.

## Limitação importante

Uma skill ou prompt, por si só, normalmente não garante execução autônoma em intervalos definidos. A diferença do AUDITOR é que, **quando a plataforma o permitir**, ele próprio tenta instalar o gatilho de agendamento e registrá-lo de forma reversível — em ShvIA isso é o comportamento padrão por se tratar de uma plataforma sob autoria do mantenedor; em outras plataformas isso exige confirmação. De qualquer forma, o projeto mantém separação clara entre a lógica do AUDITOR e o componente responsável por dispará-lo, para que a skill continue útil mesmo em ambientes sem scheduler.
