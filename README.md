# AUDITOR

Skill para executar um subagente de auditoria de código em ciclos periódicos, identificar mudanças recentes sem documentação suficiente e registrar a documentação produzida no diretório `.auditor`.

> Status: proposta inicial. A sintaxe, o mecanismo de agendamento e o suporte a modelos ainda precisam ser validados na plataforma de execução.

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

## Exemplo de uso proposto

```text
/auditor 30 m2.7
```

Interpretação pretendida:

- `auditor`: ativa ou configura a skill;
- `30`: intervalo entre ciclos;
- `m2.7`: modelo/agente solicitado, neste exemplo MiniMax 2.7.

A unidade do intervalo deve ser explícita para evitar ambiguidade. Recomenda-se aceitar:

```text
/auditor every 30m model m2.7
```

E, opcionalmente, manter a forma curta como atalho:

```text
/auditor 30m m2.7
```

## Plataformas e idioma

- Plataformas-alvo: Claude, OpenAI e ShvIA.
- Idioma principal dos artefatos: inglês dos EUA (`en-US`).
- O relatório apresentado ao usuário pode seguir o idioma da conversa.
- O nome da skill é `AUDITOR`.

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

O intervalo de 30 minutos deve ser tratado como configuração, não como garantia de execução. Se não houver scheduler disponível, `/auditor 30m m2.7` deve configurar o intervalo e informar como a execução será disparada.

## Seleção do agente/modelo

A configuração deve separar:

- `agent`: papel especializado, por exemplo `documentation-auditor`;
- `model`: identificador compatível com a plataforma, por exemplo `m2.7`;
- `interval`: duração, por exemplo `30m`;
- `scope`: escopo de arquivos e branches;
- `write_policy`: permissão de escrita, inicialmente apenas `.auditor`.

Exemplo conceitual:

```yaml
agent: documentation-auditor
model: m2.7
interval: 30m
language: en-US
write_policy: auditor-only
state_source: git
```

`m2.7` deve ser considerado um identificador solicitado pelo usuário, não uma garantia de que todas as plataformas terão esse modelo. A skill deve validar a disponibilidade e informar claramente quando houver fallback.

## Regras de segurança e qualidade

- Nunca inventar mudanças, testes ou fontes consultadas.
- Diferenciar fato observado, inferência e recomendação.
- Não incluir segredos, tokens ou dados sensíveis nos relatórios.
- Não sobrescrever documentação manual sem confirmação.
- Manter histórico dos ciclos.
- Tornar a execução idempotente quando possível.
- Registrar falhas parciais e continuar apenas em escopos seguros.
- Respeitar instruções do repositório, como `AGENTS.md`, `CLAUDE.md` ou equivalentes.
- Tratar código não versionado com uma estratégia explícita, caso o Git não esteja disponível.

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

## Decisões ainda necessárias

Antes da implementação, definir:

1. O formato oficial do comando: curto, longo ou ambos.
2. Se `30` sem unidade será aceito.
3. O identificador real do modelo MiniMax e os fallbacks.
4. Qual componente dispara a execução a cada 30 minutos.
5. Se o escopo é o repositório inteiro ou somente mudanças versionadas.
6. Se documentação criada em `.auditor` deve ser consolidada depois em `docs/` ou no README.
7. Como lidar com branches, merge commits e arquivos não rastreados.
8. Se o agente pode abrir issues, pull requests ou somente escrever `.auditor`.
9. Retenção dos relatórios e política para dados sensíveis.

## Próximos passos sugeridos

1. Escolher a especificação oficial do comando e do arquivo de configuração.
2. Definir o contrato de entrada/saída do subagente.
3. Escolher um primeiro adaptador de plataforma, em vez de implementar Claude, OpenAI e ShvIA simultaneamente.
4. Criar um executor local que faça um ciclo manual reproduzível.
5. Implementar o estado e a detecção de mudanças.
6. Implementar a escrita segura em `.auditor`.
7. Adicionar testes com um repositório de exemplo contendo mudanças documentadas e não documentadas.
8. Integrar um scheduler externo e testar reinicialização, falhas e execução duplicada.
9. Criar adaptadores para as demais plataformas.
10. Definir versionamento, distribuição e instalação da skill.

## Limitação importante

Uma skill ou prompt, por si só, normalmente não garante execução autônoma a cada 30 minutos. Para isso, é necessário um mecanismo de agendamento autorizado pela plataforma ou pelo ambiente. O projeto deve separar claramente a lógica do AUDITOR do componente responsável por dispará-lo.
