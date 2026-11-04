import json
import re
import sqlite3
import unittest
from pathlib import Path
from src.config import ROOT,RAW,GOLD,WAREHOUSE,REPORTS,QUALITY
from src.utils import read_csv,parse_datetime

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not WAREHOUSE.exists():
            from src.generate_synthetic import generate
            from src.transform import build_bronze,build_silver,build_gold,_write_database
            from src.quality import run
            from src.poc01_cancelamento import run as p1
            from src.poc02_pre_loja import run as p2
            generate();build_bronze();raw,events=build_silver();data=build_gold(raw,events);run(data);p1(data);p2(data);_write_database()

    def test_manifest_14_sources_and_ids(self):
        manifest=json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['datasets']),14)
        self.assertEqual(manifest['cancellations_oct_2026'],240)

    def test_cancelled_only_october(self):
        rows=read_csv(GOLD/'fct_cancelamentos_analitica.csv')
        self.assertEqual(len(rows),240)
        self.assertTrue(all(r['dt_cancelamento'].startswith('2026-10-') for r in rows))

    def test_all_calls_categorized(self):
        raw=read_csv(RAW/'ura_ligacoes.csv')
        gold=read_csv(GOLD/'fct_ligacoes_classificadas.csv')
        self.assertEqual(len(raw),len(gold))
        self.assertTrue(all(r['tema_identificado'] for r in gold))

    def test_no_mobile_residential_tech(self):
        contracts={r['contrato_id']:r['produto'] for r in read_csv(RAW/'contratos.csv')}
        self.assertTrue(all(contracts[r['contrato_id']]=='FIXA' for r in read_csv(RAW/'visitas_tecnicas.csv')))

    def test_unknown_no_competitor_fabricated(self):
        evidences=read_csv(GOLD/'fct_evidencias_motivo.csv')
        direct={r['cancelamento_id'] for r in evidences if r['motivo']=='concorrencia' and r['tipo_evidencia'] in ('portabilidade_autorizada','concorrente_autodeclarado')}
        inferred={r['cancelamento_id'] for r in read_csv(GOLD/'fct_cancelamentos_analitica.csv') if r['causa_principal']=='concorrencia'}
        self.assertTrue(inferred.issubset(direct))

    def test_store_30days_and_last_canal(self):
        rows=read_csv(GOLD/'fct_pre_loja_30d.csv')
        self.assertGreater(len(rows),0)
        self.assertTrue(all(r['jornada_ordenada_30d'].endswith('LOJA') for r in rows))
        self.assertTrue(all(r['produto']=='FIXA' or int(r['qtd_tecnicos_30d'])==0 for r in rows))

    def test_quality_report(self):
        report=json.loads((QUALITY/'quality_report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['status'],'PASS')
        self.assertGreaterEqual(report['total_testes'],60)

    def test_sqlite_materialized_and_relationships(self):
        conn=sqlite3.connect(WAREHOUSE)
        try:
            n=conn.execute('SELECT COUNT(*) FROM fct_jornada_eventos').fetchone()[0]
            self.assertGreater(n,5000)
            missing=conn.execute('SELECT COUNT(*) FROM fct_cancelamentos_analitica f LEFT JOIN dim_cliente c ON f.cliente_hash=c.cliente_hash WHERE c.cliente_hash IS NULL').fetchone()[0]
            self.assertEqual(missing,0)
        finally:conn.close()

    def test_all_documented_sql_queries_execute(self):
        conn=sqlite3.connect(WAREHOUSE)
        try:
            total=0
            for path in sorted((ROOT/'sql').glob('*.sql')):
                text='\n'.join(line for line in path.read_text(encoding='utf-8').splitlines()
                               if not line.lstrip().startswith('--'))
                for statement in text.split(';'):
                    if statement.strip():
                        conn.execute(statement).fetchall()
                        total += 1
            self.assertGreaterEqual(total,10)
        finally:
            conn.close()

    def test_dashboard_exists(self):
        self.assertTrue((REPORTS/'dashboard.html').exists())

if __name__=='__main__':unittest.main()
