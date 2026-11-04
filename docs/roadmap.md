# Roadmap de evolução e critérios de aceite

## Estado atual (v0.1 — novembro de 2026)

| Entrega | Estado | O que foi feito |
|---|---|---|
| Escopo e cohort outubro/2026 | ✅ | Móvel/Fixa; 6 meses fechados + 180 dias exatos |
| Inventário de fontes simuladas | ✅ | 14 cabeçalhos/CSVs e manifesto |
| Chave pseudonimizada | ✅ | HMAC-SHA256 simulado nos dados de cliente |
| Arquitetura medallion | ✅ | Bronze, Silver, Gold, SQLite |
| Reconstrução dos eventos | ✅ | Linha do tempo com linhagem fonte/ID |
| Classificação de todas as ligações fictícias | ✅ | Regras de palavras-chave e tema por ligação |
| Causa e evidências | ✅ | Fato de cancelamento, ponte de causas e evidências |
| POC 02 pré-loja | ✅ | Janela de 30 dias, recontato e transições |
| Pressão competitiva | 🟡 | Oferta regional fictícia; portabilidade autorizada fictícia |
| Reclame Aqui | 🟡 | Fonte simulada, sem integração externa |
| Resolução até 30 dias | ✅ | Medida inicial de ticket; ainda não SLA corporativo homologado |
| Dashboard exploratório | ✅ | HTML estático com CSV e consultas SQL |
| Power BI (PBIP/TMDL) | ⬜ | Não gerado; integração futura via Gold CSV/SQLite |
| Modelo NLP em gravações reais | ⬜ | Não gerado; depende de dados autorizados e benchmark |
| Validação de dicionários reais | ⬜ | Aguardando headers, regras e amostra controlada |

## Fase 1 — Ajustar a primeira fonte real

- Obter dicionário do cancelamento: chaves, datas de solicitação/conclusão, motivos, tipo de churn, status de reativação.
- Mapear contrato/linha/produto/categoria comercial com SCD e histórico de planos.
- Reconciliar o total de cancelamentos de outubro por Móvel/Fixa, status e canal.
- Definir a população elegível e contratos duplicados/múltiplos por cliente.

**Aceite:** zero órfãos de contrato, reconciliação documentada, limites de período corretos, dados de identidade governados.

## Fase 2 — Incorporar cada canal

Sequência proposta: URA e protocolos → lojas/PDV → app/site → tickets/visitas Fixa → faturamento/negociação → ouvidoria/reclamação → pesquisa de saída → enriquecimento externo permitido.

Para cada fonte: entrada real → tabela de mapeamento → testes → comparação com fonte → avaliação de cobertura → dashboard.

## Fase 3 — Melhorar o estudo das hipóteses

- Classificação multirrótulo de áudio/transcrição por categoria e subcategoria, com padrão ouro revisado por humanos.
- Métricas de precisão, recall, F1, concordância interavaliadores, cobertura e confiança calibrada por motivo/produto.
- Grafo de transições entre canais e funis abandono → suporte → reclamação → loja → saída.
- Resolver ambiguidade entre problema técnico, problema de atendimento e evento financeiro antecedente.
- Medir impacto de resolução em 24h, 7d e 30d; distinguir SLAs estabelecidos e janelas de observação.
- Estudo ativo vs cancelado com desenho observacional, pareamento e controle de fatores de confusão.

## Fase 4 — Produto analítico

- Orquestrador incremental e agendamento; novas partições, watermark e idempotência.
- Qualidade observável por fonte/produto/mês e relatório de lacunas com owners.
- Catálogo de dados e definição de indicadores homologados.
- Power BI versionável com filtros de produto, período, canal, jornada e causa, RLS quando necessário.
- Governança das decisões e ciclo de melhoria contínua por squads operacionais.

## Decisões pendentes

- Considerar somente cancelamento efetivado ou também solicitado/revertido?
- Como lidar com contratos Móvel+Fixa no mesmo CPF/cliente?
- Há retenção após solicitação? Qual o momento de churn real?
- Quais campos dão acesso ao protocolo de ponta a ponta?
- Existe atributo confiável de problema de rede ou indicadores técnicos?
- Quais colunas distinguem cobrança indevida, atraso e negociação?
- Existe acesso autorizado a reclamações e portabilidade de forma individual?
- Que janela de 30 dias mede tempo de resolução por tipo de incidente?
