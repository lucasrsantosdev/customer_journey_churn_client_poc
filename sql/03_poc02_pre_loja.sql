-- 1. POC02: denominador correto = clientes-contratos distintos com loja.
WITH ultima_visita AS (
 SELECT p.*,ROW_NUMBER() OVER (PARTITION BY cliente_hash,contrato_id ORDER BY dt_visita DESC) rn
 FROM fct_pre_loja_30d p
)
SELECT produto, COUNT(*) AS clientes_com_loja,
 SUM(CAST(qtd_ura_30d AS INTEGER)>0) AS passaram_pela_ura,
 SUM(CAST(qtd_app_30d AS INTEGER)>0) AS passaram_pelo_app,
 SUM(CAST(qtd_site_30d AS INTEGER)>0) AS passaram_pelo_site,
 SUM(CAST(qtd_suporte_30d AS INTEGER)>0) AS abriram_suporte,
 SUM(CAST(qtd_tecnicos_30d AS INTEGER)>0) AS receberam_visita,
 ROUND(100.0*SUM(CAST(houve_contato_antes_loja AS INTEGER))/COUNT(*),2) pct_contato_previo,
 ROUND(100.0*SUM(CAST(multicanal_antes_loja AS INTEGER))/COUNT(*),2) pct_multicanal
FROM ultima_visita WHERE rn=1 GROUP BY produto;

-- 2. Quantos usaram a central ANTES da loja, por produto e desfecho.
WITH ultima_visita AS (
 SELECT p.*,ROW_NUMBER() OVER (PARTITION BY cliente_hash,contrato_id ORDER BY dt_visita DESC) rn
 FROM fct_pre_loja_30d p
)
SELECT produto,cancelou_outubro,COUNT(*) AS clientes_com_loja,
 SUM(CAST(qtd_ura_30d AS INTEGER)>0) AS ligaram_antes,
 ROUND(100.0*SUM(CAST(qtd_ura_30d AS INTEGER)>0)/COUNT(*),2) AS pct_ura_antes
FROM ultima_visita WHERE rn=1 GROUP BY produto,cancelou_outubro;

-- 3. Transicoes adjacentes por canal (contam eventos, nao clientes unicos).
SELECT produto,canal_origem,canal_destino,quantidade_transicoes
FROM fct_transicoes_canais
ORDER BY CAST(quantidade_transicoes AS INTEGER) DESC LIMIT 30;

-- 4. Reconstruir a jornada anterior a uma visita especifica.
-- Substituir :atendimento_loja_id no cliente SQLite ou Python parametrizado.
SELECT atendimento_loja_id,cliente_hash,dt_visita,produto,
       qtd_ura_30d,qtd_app_30d,qtd_site_30d,qtd_suporte_30d,
       qtd_tecnicos_30d,ultimo_canal_antes_loja,jornada_ordenada_30d
FROM fct_pre_loja_30d ORDER BY dt_visita DESC LIMIT 30;
