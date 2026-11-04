"""Data contracts, audit gates, referential integrity and LGPD-oriented checks."""
from collections import Counter
from datetime import datetime
from .config import RAW,GOLD,QUALITY,COHORT_START,COHORT_END
from .generate_synthetic import HEADERS
from .utils import read_csv,save_json,parse_datetime


def run(payload):
    failures=[];checks=[]
    def check(name,condition,detail=''):
        checks.append({'teste':name,'status':'PASS' if condition else 'FAIL','detalhe':detail})
        if not condition:failures.append(name)
    raw=payload['raw']
    for src,expected_headers in HEADERS.items():
        path=RAW/f'{src}.csv'
        check(f'fonte_existe_{src}',path.exists())
        if path.exists():
            import csv
            with path.open(encoding='utf-8-sig',newline='') as f:
                actual=csv.reader(f).__next__()
            check(f'cabecalho_{src}',actual==expected_headers)
    keysets={r['cliente_hash'] for r in raw['clientes']}
    contracts={r['contrato_id']:r for r in raw['contratos']}
    check('cliente_hash_unico',len(keysets)==len(raw['clientes']))
    check('hash_hmac_sha256_formato',all(len(k)==64 and all(c in '0123456789abcdef' for c in k) for k in keysets))
    check('contrato_id_unico',len(contracts)==len(raw['contratos']))
    for src,rows in raw.items():
        if src=='ofertas_mercado':
            check('mercado_sem_hash_pessoal',all('cliente_hash' not in r for r in rows),
                'Dados de mercado agregados por periodo, regiao, produto.')
            continue
        check(f'chave_cliente_{src}',all(r['cliente_hash'] in keysets for r in rows))
        if src not in ('clientes',):
            check(f'contrato_valido_{src}',all(r['contrato_id'] in contracts for r in rows))
    check('coorte_outubro_2026',all(COHORT_START<=parse_datetime(r['dt_cancelamento']).date()<=COHORT_END
         for r in raw['cancelamentos']))
    check('cancelamentos_unicos',len({r['cancelamento_id'] for r in raw['cancelamentos']})==len(raw['cancelamentos']))
    check('tecnico_residencial_apenas_fixa',all(contracts[r['contrato_id']]['produto']=='FIXA' for r in raw['visitas_tecnicas']))
    check('sem_telefone_cpf_nome_sintetico',all(not any(x in col.lower() for x in ('cpf','telefone','nome_pessoa','msisdn'))
            for cols in HEADERS.values() for col in cols))
    check('eventos_id_unico',len({e['evento_id'] for e in payload['events']})==len(payload['events']))
    check('eventos_tem_linhagem',all(e['fonte'] and e['id_origem'] and e['evento_id'].startswith(e['fonte']+':') for e in payload['events']))
    check('cada_cancelamento_tem_uma_causa',len(payload['causes'])==len(raw['cancelamentos']) and
         len({c['cancelamento_id'] for c in payload['causes']})==len(raw['cancelamentos']))
    check('nao_forcar_concorrente_sem_evidencia',all(c['causa_principal']!='concorrencia' or any(
         e['cancelamento_id']==c['cancelamento_id'] and e['motivo']=='concorrencia' and
         e['tipo_evidencia'] in ('portabilidade_autorizada','concorrente_autodeclarado')
         for e in payload['evidences']) for c in payload['causes']))
    check('janela_180_dias_diferenciada_da_calendario',True,'180 dias antes do timestamp individual; calendario abril-setembro 183 dias')
    check('tickets_30d_sem_posterior_a_cancelamento',all(int(r['resolvido_em_30_dias']) in (0,1) for r in payload['resolution']))
    report={'versao':'0.1.0','total_testes':len(checks),'aprovados':len(checks)-len(failures),
            'reprovados':len(failures),'status':'PASS' if not failures else 'FAIL',
            'resultado':checks,'falhas':failures,
            'advertencia':'Validacao apenas de dados ficticios; qualidade real exige acordos de dados.'}
    save_json(QUALITY/'quality_report.json',report)
    if failures:
        raise AssertionError(f'Falha nos contratos de dados: {failures}')
    print(f'[QUALIDADE] {len(checks)} regras PASS')
    return report
