# Dados da POC v0.1

**Atenção:** `raw/synthetic/` contém exclusivamente registros artificiais. `bronze/` guarda cópias dos arquivos sintéticos, `silver/` a linha do tempo canônica, `gold/` os marts analíticos, `warehouse/` o SQLite completo e `quality/` os testes de contratos.

- Para reproduzir, usar `python -m src.main --all` a partir da raiz.
- Não mover/editar os dados reais para dentro desta pasta compartilhada.
- Dados de origem reais (quando houver permissão) devem permanecer em ambiente controlado, excluídos do Git por `.gitignore` e políticas de acesso.
- `fct_ofertas_mercado` não contém `cliente_hash`; relacionar somente por período, região e produto.
