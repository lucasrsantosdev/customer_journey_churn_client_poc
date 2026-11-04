# Dicionário de dados — cabeçalhos fictícios v0.1

> **Esta especificação corresponde exatamente às colunas dos CSVs no ZIP.** Tipos são textuais nos CSVs/SQLite demonstrativo; datas usam ISO 8601, valores decimais ponto. Eventos reais exigirão tipagem, unidades e timezone homologados.

## Fontes RAW/BRONZE (14)

### `clientes.csv`

**Grão:** Cadastro sintético, 1 linha por pessoa na POC.

| Coluna fictícia | Significado / observações |
|---|---|
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `segmento` | Campo demonstrativo de clientes; contrato semântico a validar com a fonte real. |
| `uf` | UF fictícia. |
| `cidade` | Cidade fictícia de referência (sem endereço). |
| `regiao` | Região sintética de agregação. |
| `dt_ativacao` | Campo demonstrativo de clientes; contrato semântico a validar com a fonte real. |
| `perfil_sintetico` | Classe interna usada apenas para gerar cenários de teste; NÃO utilizar como preditor real nem causa analítica. |

### `contratos.csv`

**Grão:** Serviço contratado. Cada cliente simulado possui 1 contrato na v0.1; preparado para evoluir.

| Coluna fictícia | Significado / observações |
|---|---|
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `produto` | MOVEL ou FIXA. |
| `plano` | Campo demonstrativo de contratos; contrato semântico a validar com a fonte real. |
| `mensalidade` | Valor mensal do contrato em BRL; texto decimal com ponto no CSV. |
| `dt_inicio` | Campo demonstrativo de contratos; contrato semântico a validar com a fonte real. |
| `status_atual` | Campo demonstrativo de contratos; contrato semântico a validar com a fonte real. |

### `cancelamentos.csv`

**Grão:** Coorte alvo; 1 evento efetivado de saída por contrato fictício.

| Coluna fictícia | Significado / observações |
|---|---|
| `cancelamento_id` | Campo demonstrativo de cancelamentos; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_cancelamento` | Timestamp ISO 8601 do cancelamento efetivado. |
| `canal_solicitacao` | Campo demonstrativo de cancelamentos; contrato semântico a validar com a fonte real. |
| `motivo_declarado` | Campo demonstrativo de cancelamentos; contrato semântico a validar com a fonte real. |
| `tipo_cancelamento` | Campo demonstrativo de cancelamentos; contrato semântico a validar com a fonte real. |

### `ura_ligacoes.csv`

**Grão:** 1 linha por chamada atendida, independente de inbound/outbound.

| Coluna fictícia | Significado / observações |
|---|---|
| `ligacao_id` | Campo demonstrativo de ura_ligacoes; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `direcao` | INBOUND ou OUTBOUND. |
| `tema_registrado` | Campo demonstrativo de ura_ligacoes; contrato semântico a validar com a fonte real. |
| `protocolo` | Campo demonstrativo de ura_ligacoes; contrato semântico a validar com a fonte real. |
| `duracao_seg` | Campo demonstrativo de ura_ligacoes; contrato semântico a validar com a fonte real. |
| `transferencias` | Campo demonstrativo de ura_ligacoes; contrato semântico a validar com a fonte real. |
| `resolvido_primeiro_contato` | Flag 0/1 de resolução na primeira chamada; não equivale a FCR homologado. |
| `transcricao_ficticia` | Campo demonstrativo de ura_ligacoes; contrato semântico a validar com a fonte real. |

### `loja_atendimentos.csv`

**Grão:** 1 linha por visita ou atendimento em loja própria/PDV.

| Coluna fictícia | Significado / observações |
|---|---|
| `atendimento_loja_id` | Campo demonstrativo de loja_atendimentos; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `loja_id` | Campo demonstrativo de loja_atendimentos; contrato semântico a validar com a fonte real. |
| `tipo_loja` | Campo demonstrativo de loja_atendimentos; contrato semântico a validar com a fonte real. |
| `motivo_visita` | Campo demonstrativo de loja_atendimentos; contrato semântico a validar com a fonte real. |
| `protocolo` | Campo demonstrativo de loja_atendimentos; contrato semântico a validar com a fonte real. |
| `resolvido` | Flag 0/1 de conclusão do atendimento. |

### `digital_interacoes.csv`

**Grão:** 1 linha por ação/solicitação observável no aplicativo ou site.

| Coluna fictícia | Significado / observações |
|---|---|
| `interacao_digital_id` | Campo demonstrativo de digital_interacoes; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `plataforma` | APP ou SITE. |
| `acao` | Campo demonstrativo de digital_interacoes; contrato semântico a validar com a fonte real. |
| `tema` | Campo demonstrativo de digital_interacoes; contrato semântico a validar com a fonte real. |
| `protocolo` | Campo demonstrativo de digital_interacoes; contrato semântico a validar com a fonte real. |
| `resultado` | Campo demonstrativo de digital_interacoes; contrato semântico a validar com a fonte real. |

### `suporte_tickets.csv`

**Grão:** 1 linha por ticket e respectivos marcos de abertura/fechamento.

| Coluna fictícia | Significado / observações |
|---|---|
| `ticket_id` | Campo demonstrativo de suporte_tickets; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_abertura` | Timestamp ISO 8601 da criação do ticket. |
| `dt_fechamento` | Timestamp ISO 8601 do fechamento; branco = pendente. |
| `canal_abertura` | Campo demonstrativo de suporte_tickets; contrato semântico a validar com a fonte real. |
| `categoria` | Campo demonstrativo de suporte_tickets; contrato semântico a validar com a fonte real. |
| `status` | Campo demonstrativo de suporte_tickets; contrato semântico a validar com a fonte real. |
| `resultado` | Campo demonstrativo de suporte_tickets; contrato semântico a validar com a fonte real. |

### `visitas_tecnicas.csv`

**Grão:** 1 linha por visita domiciliar: produto FIXA somente.

| Coluna fictícia | Significado / observações |
|---|---|
| `visita_id` | Campo demonstrativo de visitas_tecnicas; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `ordem_servico` | Campo demonstrativo de visitas_tecnicas; contrato semântico a validar com a fonte real. |
| `diagnostico` | Campo demonstrativo de visitas_tecnicas; contrato semântico a validar com a fonte real. |
| `status_visita` | Campo demonstrativo de visitas_tecnicas; contrato semântico a validar com a fonte real. |
| `visita_repetida` | Campo demonstrativo de visitas_tecnicas; contrato semântico a validar com a fonte real. |

### `faturas.csv`

**Grão:** 1 linha por fatura contratual e referência mensal.

| Coluna fictícia | Significado / observações |
|---|---|
| `fatura_id` | Campo demonstrativo de faturas; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `mes_ref` | Mês de referência YYYYMM. |
| `dt_vencimento` | Campo demonstrativo de faturas; contrato semântico a validar com a fonte real. |
| `valor` | Campo demonstrativo de faturas; contrato semântico a validar com a fonte real. |
| `dt_pagamento` | Campo demonstrativo de faturas; contrato semântico a validar com a fonte real. |
| `status_pagamento` | PAGO, PAGO_COM_ATRASO, EM_ATRASO ou INADIMPLENTE. |
| `dias_atraso` | Dias fictícios de atraso da fatura. |

### `acordos_financeiros.csv`

**Grão:** 1 linha por renegociação/acordo.

| Coluna fictícia | Significado / observações |
|---|---|
| `acordo_id` | Campo demonstrativo de acordos_financeiros; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `valor_renegociado` | Campo demonstrativo de acordos_financeiros; contrato semântico a validar com a fonte real. |
| `qtd_parcelas` | Campo demonstrativo de acordos_financeiros; contrato semântico a validar com a fonte real. |
| `status_acordo` | Campo demonstrativo de acordos_financeiros; contrato semântico a validar com a fonte real. |

### `reclamacoes.csv`

**Grão:** 1 linha por reclamação fictícia (RECLAME_AQUI ou OUVIDORIA).

| Coluna fictícia | Significado / observações |
|---|---|
| `reclamacao_id` | Campo demonstrativo de reclamacoes; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `origem` | RECLAME_AQUI ou OUVIDORIA fictícios. |
| `tema` | Campo demonstrativo de reclamacoes; contrato semântico a validar com a fonte real. |
| `status` | Campo demonstrativo de reclamacoes; contrato semântico a validar com a fonte real. |
| `dt_resolucao` | Campo demonstrativo de reclamacoes; contrato semântico a validar com a fonte real. |
| `texto_ficticio` | Campo demonstrativo de reclamacoes; contrato semântico a validar com a fonte real. |

### `portabilidades.csv`

**Grão:** 1 linha por ocorrência fictícia de portabilidade MÓVEL autorizada.

| Coluna fictícia | Significado / observações |
|---|---|
| `portabilidade_id` | Campo demonstrativo de portabilidades; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_evento` | Campo demonstrativo de portabilidades; contrato semântico a validar com a fonte real. |
| `prestadora_destino` | Prestadora declarada no evento de portabilidade fictício. |
| `fonte_registro` | Campo demonstrativo de portabilidades; contrato semântico a validar com a fonte real. |
| `verificacao_autorizada` | Flag sintética de evidência autorizada; não representa acesso real. |

### `pesquisas_saida.csv`

**Grão:** 1 linha por resposta voluntária de pesquisa sintética de saída.

| Coluna fictícia | Significado / observações |
|---|---|
| `pesquisa_id` | Campo demonstrativo de pesquisas_saida; contrato semântico a validar com a fonte real. |
| `cliente_hash` | Chave estável HMAC-SHA256 de identificador sintético; não reverte para identidade. |
| `contrato_id` | Identificador estável do contrato/serviço fictício. |
| `dt_hora` | Timestamp local ISO 8601 da interação. |
| `resposta_motivo` | Campo demonstrativo de pesquisas_saida; contrato semântico a validar com a fonte real. |
| `concorrente_declarado` | Campo demonstrativo de pesquisas_saida; contrato semântico a validar com a fonte real. |
| `nota_atendimento` | Nota fictícia 1–10. |
| `autorizado` | Campo demonstrativo de pesquisas_saida; contrato semântico a validar com a fonte real. |

### `ofertas_mercado.csv`

**Grão:** 1 linha por oferta externa de mercado por mês/região/produto/prestadora; SEM pessoa.

| Coluna fictícia | Significado / observações |
|---|---|
| `oferta_id` | Campo demonstrativo de ofertas_mercado; contrato semântico a validar com a fonte real. |
| `mes_ref` | Mês de referência YYYYMM. |
| `regiao` | Região sintética de agregação. |
| `produto` | MOVEL ou FIXA. |
| `prestadora` | Campo demonstrativo de ofertas_mercado; contrato semântico a validar com a fonte real. |
| `valor_mensal` | Preço mensal de mercado fictício; não é referência de mercado real. |
| `tipo_oferta` | Campo demonstrativo de ofertas_mercado; contrato semântico a validar com a fonte real. |
| `fonte_publica` | Fonte ilustrativa; nenhuma consulta a preço externo feita. |
| `validade_inicio` | Campo demonstrativo de ofertas_mercado; contrato semântico a validar com a fonte real. |
| `validade_fim` | Campo demonstrativo de ofertas_mercado; contrato semântico a validar com a fonte real. |

## Camada SILVER

`eventos_canonicos.csv` possui: `evento_id`, `cliente_hash`, `contrato_id`, `dt_evento`, `canal`, `tipo_evento`, `categoria`, `status`, `resolvido`, `texto`, `fonte`, `id_origem`, `competidor`, `produto`, `mes_ref`.

**Grão:** um evento de canal. `evento_id` usa `fonte:id_origem`; o evento de fatura representa vencimento, não interação com cliente.

## Camada GOLD

| Dataset | Grão / propósito |
|---|---|
| `dim_cliente` | Cliente sintético |
| `dim_contrato` | Contrato Móvel/Fixa |
| `dim_canal` | Canal e grupo |
| `dim_motivo` | Taxonomia provisória |
| `dim_tempo` | Dia e mês referência |
| `fct_jornada_eventos` | Eventos canônicos, incluindo o cancelamento terminal |
| `fct_cancelamentos_analitica` | Uma causa principal inferida por cancelamento |
| `fct_evidencias_motivo` | Pontuação/evidência auditável por cancelamento |
| `bridge_cancelamento_motivo` | Relação cancelamento→vários motivos |
| `fct_ligacoes_classificadas` | Tema de toda ligação |
| `fct_resolucao_30d` | Resolução de tickets até 30 dias |
| `fct_pre_loja_30d` | Contatos 30 dias antes de cada loja |
| `fct_transicoes_canais` | Arestas agregadas de transição |
| `fct_ofertas_mercado` | Contexto por mês/região/produto, sem pessoa |

### Atributos críticos do fato de cancelamento

| Coluna | Interpretação |
|---|---|
| `motivo_declarado` | Valor originalmente capturado no registro de saída |
| `causa_principal` | Categoria inferida a partir de evidências explicáveis |
| `confianca` | `SEM_EVIDENCIA`, `BAIXA`, `MEDIA`, `ALTA_CORROBORADA`, `ALTA_CONFIRMADA` |
| `escore_principal` | Soma de pontos de evidência, não probabilidade estatística |
| `motivos_contribuintes` | Outras categorias com evidências suficientes (separadas por `\|`) |
| `num_contatos_180d` | Eventos selecionados antes do cancelamento na janela individual |
| `portabilidade_confirmada` | Marcador sintético com fonte autorizada, **não** busca real |
| `tempo_primeiro_contato_ate_cancelamento_dias` | Intervalo desde primeiro evento selecionado; não representa tempo de resolução |


**Regras de produção a validar:** chaves de múltiplos contratos, histórico de status (SCD), duplicidades, timezone, política de reabertura de ticket, motivos de cancelamento e captura temporal do cliente.

