# Changelog

## [0.1.0] — 2026-11-04

### Incluído

- 14 fontes CSV 100% sintéticas, 600 clientes, 240 cancelamentos em outubro/2026.
- Pipeline Python puro: Bronze → Silver → Gold → POC01 → POC02 → SQLite/HTML.
- Jornada canônica com 6.905 eventos, origem preservada por `fonte:id_origem`.
- Rastreabilidade dos 180 dias anteriores ao cancelamento com coorte em outubro e seis meses fechados de comparação.
- Etiquetagem de 1.008 ligações sintéticas; 621 delas pertencentes à janela individual dos cancelados.
- Taxonomia e classificação explicável com motivos contribuintes e categorias indeterminadas.
- Análise de 30 dias prévios a cada visita à loja; jornadas entre URA, APP, SITE, suporte, visitas e lojas.
- Datas, dimensões, fatos, SQL e dashboard HTML estático.
- Dados de mercado fictícios sem chave individual de cliente; confirmação de portabilidade somente simulada/autorizada.
- 67 validações de qualidade, 16 testes automatizados, CI GitHub Actions.
- Dicionário de 14 fontes, fluxogramas, ERD, hipóteses e documentação LGPD.
- CLI para rastrear a jornada e evidências de um cliente simulado.

### Pendente

- Cabeçalhos reais, ingestão autorizada, campos dos sistemas de origem, reconciliação operacional e homologação de regras.
- NLP de transcrições reais, matching autorizado de reclamações, dados verificáveis de concorrência e PBIP/TMDL corporativo.
