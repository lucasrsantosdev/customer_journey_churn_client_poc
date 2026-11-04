# Arquitetura de dados — CLARO Customer Journey & Churn Intelligence

> **POC v0.1 — 100% sintética, não oficial.** Outubro/2026 é a coorte; abril-setembro são meses comparativos fechados. A janela de 180 dias é móvel por evento de cancelamento.

## 1. Diagrama de arquitetura medallion

```mermaid
flowchart TB
    subgraph FONTES[Fontes de origem, simuladas nesta versão]
        CRM[Cliente e contrato]
        CAN[Cancelamento]
        URA[URA inbound/outbound e transcrições]
        LJ[Lojas próprias e pontos de venda]
        DIG[App e site]
        SUP[Tickets e visitas técnicas de Fixa]
        FIN[Faturas e acordos]
        REC[Reclamações e pesquisa de saída]
        EXT[Portabilidade autorizada e ofertas regionais]
    end
    subgraph BR[BRONZE: cópia fiel por fonte]
      B[CSVs de origem + manifesto]
    end
    subgraph SI[SILVER: normalização]
      S[Eventos canônicos + ID de origem + data/hora + cliente_hash + contrato_id]
    end
    subgraph GO[GOLD: modelo analítico]
      D[Dimensões: Cliente, Contrato, Canal, Motivo, Tempo]
      J[Fato Jornada por evento]
      C[Fato Cancelamentos e causa principal]
      E[Evidências e ponte multicausa]
      T[Fato Resolução 30 dias]
      M[Fato Ofertas de Mercado, sem chave cliente]
    end
    subgraph SAIDAS[Consumidores]
      P1[POC 01: causa e oportunidades]
      P2[POC 02: contatos pré-loja]
      SQL[SQLite / SQL / CSV]
      BI[Dashboard HTML / futura integração Power BI]
    end
    CRM & CAN & URA & LJ & DIG & SUP & FIN & REC & EXT --> B
    B -->|normalizar chaves e horários| S
    S --> J
    S --> C
    S --> E
    S --> T
    B --> M
    J --> P1 & P2
    C --> P1 & P2
    E --> P1
    T --> P1
    M -.->|somente contexto regional/mensal| P1
    D --> SQL
    J & C & E & T & M --> SQL
    P1 & P2 --> BI
```

### Por que não unir tudo diretamente?

Cada canal tem **granularidade distinta**: ligação, visita, ticket, fatura, atendimento digital e cancelamento. Juntar as tabelas brutas por `cliente_hash` produziria multiplicação de linhas (ex.: 4 ligações × 2 visitas × 3 faturas = 24 registros) e percentuais errados. Em vez disso:

1. Fontes possuem `cliente_hash` + `contrato_id` + chave de evento de origem.
2. Silver cria **um evento por interação** em `eventos_canonicos`.
3. Gold expõe uma tabela de **uma linha por cancelamento** (`fct_cancelamentos_analitica`).
4. Evidências e motivos contribuintes ficam em tabelas separadas com cardinalidade N:1 para o cancelamento.
5. A dimensão `dim_cliente` não deve conter identificação civil em ambiente de analytics.
6. Mercado externo **não possui** `cliente_hash`; o contexto se conecta por `mes_ref + regiao + produto`. Não é prova individual de mudança.

## 2. Diagrama entidade-relacionamento lógico

```mermaid
erDiagram
    DIM_CLIENTE ||--o{ DIM_CONTRATO : tem
    DIM_CONTRATO ||--o{ FCT_JORNADA_EVENTOS : registra
    DIM_CONTRATO ||--o{ FCT_CANCELAMENTOS_ANALITICA : cancela
    DIM_CANAL ||--o{ FCT_JORNADA_EVENTOS : classifica
    DIM_MOTIVO ||--o{ BRIDGE_CANCELAMENTO_MOTIVO : rotula
    FCT_CANCELAMENTOS_ANALITICA ||--o{ BRIDGE_CANCELAMENTO_MOTIVO : possui
    FCT_CANCELAMENTOS_ANALITICA ||--o{ FCT_EVIDENCIAS_MOTIVO : fundamenta
    FCT_JORNADA_EVENTOS ||--o{ FCT_EVIDENCIAS_MOTIVO : evidencia
    DIM_CONTRATO ||--o{ FCT_RESOLUCAO_30D : acompanha
    DIM_TEMPO ||--o{ FCT_JORNADA_EVENTOS : data
    DIM_TEMPO ||--o{ FCT_CANCELAMENTOS_ANALITICA : data
    DIM_TEMPO ||--o{ FCT_OFERTAS_MERCADO : mes
    DIM_CLIENTE {
      string cliente_hash PK
      string segmento
      string regiao
    }
    DIM_CONTRATO {
      string contrato_id PK
      string cliente_hash FK
      string produto
      number mensalidade
    }
    FCT_JORNADA_EVENTOS {
      string evento_id PK
      string cliente_hash FK
      string contrato_id FK
      datetime dt_evento
      string canal
      string fonte
      string id_origem
    }
    FCT_CANCELAMENTOS_ANALITICA {
      string cancelamento_id PK
      string cliente_hash FK
      string contrato_id FK
      datetime dt_cancelamento
      string causa_principal
      string confianca
    }
    FCT_EVIDENCIAS_MOTIVO {
      string cancelamento_id FK
      string fonte
      string id_origem
      string motivo
      int pontuacao
    }
    BRIDGE_CANCELAMENTO_MOTIVO {
      string cancelamento_id FK
      string motivo FK
      string papel
      int escore
    }
    FCT_RESOLUCAO_30D {
      string ticket_id PK
      string cliente_hash FK
      boolean resolvido_em_30_dias
    }
    FCT_OFERTAS_MERCADO {
      string oferta_id PK
      string mes_ref
      string regiao
      string produto
      string prestadora
    }
    DIM_CANAL {
      string canal PK
      string grupo_canal
    }
    DIM_MOTIVO {
      string motivo PK
      string descricao
    }
    DIM_TEMPO {
      date data PK
      string mes_ref
    }
```

> O ERD representa as relações **lógicas**. A base SQLite demonstrativa cria colunas do CSV como `TEXT`, não FKs físicas; índices são criados para chaves principais de acesso. Ao homologar dados reais, introduzir tipos estritos, constraints, relacionamento composto quando houver múltiplos contratos e carga incremental.

## 3. Granularidade por camada

| Tabela | Grão | Chaves / junção |
|---|---|---|
| `dim_cliente` | 1 linha/cliente sintético | `cliente_hash` |
| `dim_contrato` | 1 linha/contrato | `contrato_id`, `cliente_hash` |
| `fct_jornada_eventos` | 1 linha/evento do canal | `evento_id`, `cliente_hash`, `contrato_id`, `dt_evento` |
| `fct_cancelamentos_analitica` | 1 linha/cancelamento | `cancelamento_id`, `contrato_id` |
| `bridge_cancelamento_motivo` | 1 linha/cancelamento/motivo sustentado | `cancelamento_id`, `motivo` |
| `fct_evidencias_motivo` | 1 linha/evidência detectada | `cancelamento_id`, `fonte`, `id_origem` (pode ter múltiplos motivos/evidências) |
| `fct_resolucao_30d` | 1 linha/ticket de suporte | `ticket_id`, `contrato_id` |
| `fct_pre_loja_30d` | 1 linha/visita à loja | `atendimento_loja_id` |
| `fct_transicoes_canais` | 1 linha/tipo de transição/produto agregado | `produto`, `canal_origem`, `canal_destino` |
| `fct_ofertas_mercado` | 1 linha/oferta/operadora/região/mês | `mes_ref`, `regiao`, `produto` |

## 4. Produto e canais

- **MÓVEL**: chip/linha/plano; URA, lojas, pontos de venda, app, site, financeiro, reclamações; **não** recebe visita técnica residencial nesta POC.
- **FIXA**: banda larga residencial/equipamentos; todos os canais correspondentes, **mais** suporte técnico e visita residencial.
- Em produção, separar contratos de banda larga de eventual telefonia fixa e outros serviços para evitar extrapolar regras de portabilidade numérica.
- **URA inbound/outbound**: uma ligação por registro; se houver gravação/transcrição real, integrá-la com autorização, minimização de PII e classificação supervisionada.

## 5. Temporalidade e recortes

| Visão | Intervalo | Objetivo |
|---|---|---|
| Coorte de cancelamento | 01/10/2026 a 31/10/2026 | Quem cancelou, produto e data |
| Calendário fechado | 01/04/2026 a 30/09/2026 (183 dias) | Comparar meses anteriores |
| Janela individual | `[timestamp_cancelamento - 180 dias, timestamp_cancelamento)` | Evidências causais e sequência completa, inclusive outubro pré-saída |
| Pré-loja | `[timestamp_visita - 30 dias, timestamp_visita)` | O que aconteceu antes do atendimento presencial |
| Resolução | até 30 dias a partir da abertura do ticket, observando o corte | Resolver até 30 dias não significa necessariamente evitar cancelamento |

## 6. Rastreabilidade

`evento_id = nome_fonte + ':' + id_origem`. Cada evidência grava `cancelamento_id`, `fonte`, `id_origem`, `pontuacao` e `dt_evidencia`. Desse modo é possível responder: **qual evento fundamentou cada hipótese, quando, em qual canal e com qual confiabilidade?**

No cenário produtivo, adicionar `ingested_at`, `source_system`, `source_file`, `source_watermark`, `row_hash`, `run_id`, `taxonomy_version` e manifesto por partição.
