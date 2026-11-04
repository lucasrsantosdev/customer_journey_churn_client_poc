-- CLARO Customer Journey & Churn POC v0.1
-- SQLite local warehouse: data/warehouse/claro_poc.sqlite
-- As tabelas Gold sao importadas automaticamente por src/transform.py com colunas TEXT.
-- Exemplos para consultar o modelo e os relacionamentos (nao sao DDL produtivo).

SELECT
  c.cancelamento_id, c.cliente_hash, c.contrato_id,
  ct.produto, ct.plano, cli.uf, cli.regiao, c.dt_cancelamento,
  c.motivo_declarado, c.causa_principal, c.confianca
FROM fct_cancelamentos_analitica AS c
JOIN dim_cliente AS cli ON cli.cliente_hash = c.cliente_hash
JOIN dim_contrato AS ct ON ct.contrato_id = c.contrato_id AND ct.cliente_hash = c.cliente_hash
ORDER BY c.dt_cancelamento LIMIT 20;

-- Fonte da evidencia e o evento originario (join auditavel).
SELECT c.cancelamento_id, e.motivo, e.tipo_evidencia, e.pontuacao,
       e.fonte, e.id_origem, j.dt_evento, j.canal, j.status
FROM fct_cancelamentos_analitica AS c
JOIN fct_evidencias_motivo AS e ON e.cancelamento_id = c.cancelamento_id
LEFT JOIN fct_jornada_eventos AS j
 ON j.fonte = e.fonte AND j.id_origem = e.id_origem
 AND j.cliente_hash = e.cliente_hash
ORDER BY c.cancelamento_id, e.pontuacao DESC LIMIT 50;
