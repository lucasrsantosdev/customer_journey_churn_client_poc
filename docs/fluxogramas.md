# Fluxogramas funcionais e jornadas

## POC 01 — Investigação da raiz do cancelamento

```mermaid
flowchart TD
    A[Selecionar cancelamentos de outubro/2026] --> B{Produto?}
    B -->|Móvel| C[Carregar URA, loja, digital, financeiro e reclamações]
    B -->|Fixa| D[Somar suporte técnico e visitas residenciais]
    C --> E[Recuperar eventos anteriores em 180 dias exatos]
    D --> E
    E --> F[Ordenar por data/hora e unir ao contrato]
    F --> G[Classificar temas de TODAS as ligações]
    G --> H[Detectar reincidência, atrasos, falhas de resolução e reclamações]
    H --> I{Há portabilidade autorizada ou concorrente autodeclarado?}
    I -->|Sim| J[Registrar evidência direta de concorrência]
    I -->|Não| K[Ofertas públicas somente como contexto externo]
    J --> L[Somar evidências por motivo]
    K --> L
    L --> M{Evidência individual suficiente?}
    M -->|Não| N[Indeterminado; não inventar causa]
    M -->|Sim| O[Definir causa principal + motivos contribuintes]
    N --> P[Gerar fatos, percentuais e amostra de auditoria]
    O --> P
    P --> Q[Hipóteses e oportunidades por produto / canal]
```

### Exemplo sintético de encadeamento

| Data ilustrativa | Canal | Evento | Evidência |
|---|---|---|---|
| 18/08 | APP | Registro de instabilidade | Sinal inicial |
| 22/08 | URA inbound | Reclamação de queda | Reincidência |
| 26/08 | Técnico residencial (Fixa) | Visita sem solução | Falha técnica |
| 10/09 | Técnico residencial (Fixa) | Segunda visita | Problema persistente |
| 24/09 | Loja própria | Cliente volta a pedir ajuda | Escalada entre canais |
| 15/10 | Cancelamento | Motivo declarado: preço | **Possível divergência** entre motivo declarado e histórico técnico |

O exemplo acima é didático; o pipeline possui casos sintéticos gerados de forma aleatória e determinística. A causa é **hipótese baseada em evidências**, não diagnóstico com validade jurídica ou causalidade comprovada.

## POC 02 — O que aconteceu antes de chegar à loja?

```mermaid
flowchart TD
  A[Selecionar cada atendimento de loja / PDV] --> B[Identificar cliente_hash + contrato_id]
  B --> C[Buscar 30 dias ANTERIORES à visita]
  C --> D[Ordenar linha do tempo por timestamp]
  D --> E{Houve contato anterior?}
  E -->|Não| F[Primeira interação observada: LOJA]
  E -->|Sim| G[Contar URA inbound/outbound, APP, SITE, SUPORTE, TÉCNICO]
  G --> H[Capturar primeiro canal, último canal e tempo entre contatos]
  H --> I{Usou múltiplos canais?}
  I -->|Sim| J[Marcar jornada multicanal]
  I -->|Não| K[Marcar jornada canal único]
  F --> L[Consolidar métricas por produto e visita]
  J --> L
  K --> L
  L --> M[Reduzir a última visita por cliente/contrato para taxa por cliente]
  M --> N[Comparar cancelados e ativos: descrição, não causalidade]
  N --> O[Hipóteses de falha de resolução e repasse de contexto]
```

## Jornadas comuns a investigar

```mermaid
flowchart LR
  A[APP] --> B[URA inbound]
  B --> C[LOJA]
  C --> D[CANCELAMENTO]
  E[SITE] --> F[SUPORTE]
  F --> G[TÉCNICO FIXA]
  G --> H[LOJA]
  H --> D
  I[FATURA EM ATRASO] --> J[RENEGOCIAÇÃO]
  J --> K[ACORDO QUEBRADO]
  K --> D
  L[OFERTA EXTERNA REGIONAL] -.-> M[VARIÁVEL CONTEXTUAL]
  N[PORTABILIDADE AUTORIZADA] --> O[EVIDÊNCIA INDIVIDUAL]
  M -.-> D
  O --> D
```

## Gatilhos candidatos

| Gatilho observável | Critério de estudo inicial | Exemplo de ação futura (não automática) |
|---|---|---|
| URA → loja | URA até 30 dias antes da visita | Verificar se o atendente de loja recebeu histórico |
| App/site → loja | Uso digital com retorno `SEM_SOLUCAO` | Investigar falha de autosserviço |
| Visitas repetidas | 2+ visitas técnicas em Fixa | Avaliar qualidade da solução técnica |
| Ticket pendente | Ticket sem fechamento no instante do cancelamento | Investigar fila e prazo |
| Alto esforço | 3+ ligações não resolvidas em 180 dias | Propor caso único no CRM |
| Financeiro | Inadimplência + acordo quebrado | Analisar recuperação e comunicação |
| Reclamação aberta | Reclamação pública/OUVIDORIA não resolvida | Revisar resposta e escalada |
| Oferta externa | Oferta abaixo da mensalidade contratual na região/mês | Hipótese de pressão competitiva **agregada**, sem classificar cliente |
| Saída não explicada | Nenhuma evidência robusta | Melhorar pesquisa de saída e integração de fontes |
