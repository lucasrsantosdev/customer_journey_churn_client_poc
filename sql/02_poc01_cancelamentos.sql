-- 1. Causa principal: denominador = contratos cancelados por produto.
SELECT produto, causa_principal, COUNT(*) AS cancelamentos,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY produto),2) AS percentual_no_produto
FROM fct_cancelamentos_analitica
GROUP BY produto, causa_principal ORDER BY produto, cancelamentos DESC;

-- 2. Causas contribuintes: percentuais podem ultrapassar 100% se somados.
SELECT c.produto, b.motivo, COUNT(DISTINCT b.cancelamento_id) AS clientes_com_evidencia,
  ROUND(100.0 * COUNT(DISTINCT b.cancelamento_id) /
    (SELECT COUNT(*) FROM fct_cancelamentos_analitica AS sub WHERE sub.produto=c.produto),2)
    AS percentual_clientes_cancelados
FROM bridge_cancelamento_motivo AS b
JOIN fct_cancelamentos_analitica AS c ON c.cancelamento_id=b.cancelamento_id
GROUP BY c.produto,b.motivo ORDER BY c.produto,clientes_com_evidencia DESC;

-- 3. Comparacao entre motivo capturado no fluxo e inferencia explicavel.
SELECT motivo_declarado,causa_principal,COUNT(*) AS clientes
FROM fct_cancelamentos_analitica
GROUP BY motivo_declarado,causa_principal ORDER BY clientes DESC;

-- 4. Todas as ligacoes: tema identificado, canal, resolucao e produto.
SELECT l.produto,l.direcao,l.tema_identificado,
  COUNT(*) AS ligacoes, COUNT(DISTINCT l.cliente_hash) AS clientes_unicos
FROM fct_ligacoes_classificadas AS l
WHERE l.em_janela_180d_pre_cancelamento='1' -- SOMENTE coorte de outubro e 180d pre-cancelamento
GROUP BY l.produto,l.direcao,l.tema_identificado ORDER BY ligacoes DESC;

-- 5. Resolucao de tickets em 30 dias (nao confundir com resolucao de todas as chamadas).
SELECT COUNT(*) AS tickets, SUM(CAST(resolvido_ate_corte AS INTEGER)) AS resolvidos,
 SUM(CAST(resolvido_em_30_dias AS INTEGER)) AS resolvidos_em_30d,
 ROUND(100.0*SUM(CAST(resolvido_em_30_dias AS INTEGER))/NULLIF(COUNT(*),0),2) AS pct_em_30d
FROM fct_resolucao_30d;

-- 6. Oferta concorrente = contextual (mes, regiao, produto), NAO comprova migracao.
SELECT c.cancelamento_id, c.produto, cl.regiao, c.causa_principal,
  o.prestadora, o.valor_mensal AS oferta_regional,
  ct.mensalidade AS preco_contrato_ficticio,
  ROUND(CAST(ct.mensalidade AS REAL)-CAST(o.valor_mensal AS REAL),2) AS delta_preco
FROM fct_cancelamentos_analitica AS c
JOIN dim_cliente AS cl ON cl.cliente_hash=c.cliente_hash
JOIN dim_contrato AS ct ON ct.contrato_id=c.contrato_id
JOIN fct_ofertas_mercado AS o
 ON o.mes_ref=substr(c.dt_cancelamento,1,4)||substr(c.dt_cancelamento,6,2)
 AND o.regiao=cl.regiao AND o.produto=c.produto
WHERE c.causa_principal IN ('indeterminado','preco_oferta')
LIMIT 30;
