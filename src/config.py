"""Central configuration for CLARO synthetic churn study."""
from pathlib import Path
from datetime import date
import os

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'raw' / 'synthetic'
BRONZE = ROOT / 'data' / 'bronze'
SILVER = ROOT / 'data' / 'silver'
GOLD = ROOT / 'data' / 'gold'
QUALITY = ROOT / 'data' / 'quality'
WAREHOUSE = ROOT / 'data' / 'warehouse' / 'claro_poc.sqlite'
REPORTS = ROOT / 'reports'
COHORT_START = date(2026, 10, 1)
COHORT_END = date(2026, 10, 31)
CALENDAR_START = date(2026, 4, 1)
CALENDAR_END = date(2026, 9, 30)
WINDOW_DAYS = 180
STORE_LOOKBACK_DAYS = 30
RESOLUTION_DAYS = 30
SEED = 202610
# Used ONLY with synthetic identifiers; in a real environment configure a managed secret.
DEMO_HMAC_KEY = os.environ.get('CLARO_HMAC_KEY', 'DEMO_ONLY_CHANGE_ME_NEVER_USE_WITH_REAL_PII')
SOURCE_FILES = [
    'clientes', 'contratos', 'cancelamentos', 'ura_ligacoes', 'loja_atendimentos',
    'digital_interacoes', 'suporte_tickets', 'visitas_tecnicas',
    'faturas', 'acordos_financeiros', 'reclamacoes', 'portabilidades',
    'pesquisas_saida', 'ofertas_mercado'
]
