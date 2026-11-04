"""POC 02 — preceding touchpoints and channel transitions before a store visit."""
from collections import Counter,defaultdict
from datetime import timedelta
from .config import GOLD,REPORTS,STORE_LOOKBACK_DAYS,WINDOW_DAYS
from .utils import read_csv,write_csv,save_json,parse_datetime,fmt_ratio

VISIT_FIELDS=['atendimento_loja_id','cliente_hash','contrato_id','dt_visita','produto',
    'cancelou_outubro','qtd_ura_30d','qtd_app_30d','qtd_site_30d','qtd_suporte_30d',
    'qtd_tecnicos_30d','houve_contato_antes_loja','multicanal_antes_loja',
    'primeiro_canal_30d','ultimo_canal_antes_loja','horas_desde_ultimo_contato',
    'jornada_ordenada_30d']
TRANS_FIELDS=['produto','canal_origem','canal_destino','quantidade_transicoes']


def run(payload):
    events=payload['events']; raw=payload['raw']; REPORTS.mkdir(parents=True,exist_ok=True)
    cancels={(r['cliente_hash'],r['contrato_id']) for r in raw['cancelamentos']}
    by_key=defaultdict(list)
    for e in events:
        if e['canal'] not in ('FINANCEIRO','PESQUISA_SAIDA','PORTABILIDADE','CANCELAMENTO'):
            by_key[(e['cliente_hash'],e['contrato_id'])].append(e)
    stores=[e for e in events if e['fonte']=='loja_atendimentos']
    visits=[]
    for s in stores:
        dt=parse_datetime(s['dt_evento'])
        previous=[e for e in by_key[(s['cliente_hash'],s['contrato_id'])] if
                  dt-timedelta(days=STORE_LOOKBACK_DAYS)<=parse_datetime(e['dt_evento'])<dt]
        previous.sort(key=lambda e:(e['dt_evento'],e['evento_id']))
        channels=[e['canal'] for e in previous]
        v={'atendimento_loja_id':s['id_origem'],'cliente_hash':s['cliente_hash'],
          'contrato_id':s['contrato_id'],'dt_visita':s['dt_evento'],'produto':s['produto'],
          'cancelou_outubro':int((s['cliente_hash'],s['contrato_id']) in cancels),
          'qtd_ura_30d':sum(x.startswith('URA_') for x in channels),
          'qtd_app_30d':channels.count('APP'),'qtd_site_30d':channels.count('SITE'),
          'qtd_suporte_30d':channels.count('SUPORTE'),
          'qtd_tecnicos_30d':channels.count('TECNICO_RESIDENCIAL'),
          'houve_contato_antes_loja':int(bool(channels)),
          'multicanal_antes_loja':int(len(set(channels))>=2),
          'primeiro_canal_30d':channels[0] if channels else '',
          'ultimo_canal_antes_loja':channels[-1] if channels else '',
          'horas_desde_ultimo_contato':round((dt-parse_datetime(previous[-1]['dt_evento'])).total_seconds()/3600,1) if previous else '',
          'jornada_ordenada_30d': ' > '.join(channels+['LOJA']) if channels else 'LOJA'}
        visits.append(v)
    write_csv(GOLD/'fct_pre_loja_30d.csv',visits,VISIT_FIELDS)
    # One row per client-contract with the last store attendance for denominator control.
    unique={}
    for v in sorted(visits,key=lambda r:r['dt_visita']):
        unique[(v['cliente_hash'],v['contrato_id'])]=v
    client_rows=list(unique.values())
    write_csv(REPORTS/'poc02_clientes_pre_loja.csv',client_rows,VISIT_FIELDS)
    # Every adjacent channel transition in the last 180 days preceding cancellation;
    # active customers use 2026-10-31 end and are a descriptive comparator only.
    from datetime import datetime
    cutoff={(r['cliente_hash'],r['contrato_id']):parse_datetime(r['dt_cancelamento']) for r in raw['cancelamentos']}
    transitions=Counter()
    for key,evs in by_key.items():
        end=cutoff.get(key,datetime(2026,10,31,23,59,59))
        before=sorted((e for e in evs if end-timedelta(days=WINDOW_DAYS)<=parse_datetime(e['dt_evento'])<end),
                      key=lambda e:(e['dt_evento'],e['evento_id']))
        for current,next_ in zip(before,before[1:]):
            if current['canal']!=next_['canal']:
                transitions[(current['produto'],current['canal'],next_['canal'])]+=1
    trans_rows=[{'produto':p,'canal_origem':a,'canal_destino':b,'quantidade_transicoes':n}
                for (p,a,b),n in sorted(transitions.items())]
    write_csv(GOLD/'fct_transicoes_canais.csv',trans_rows,TRANS_FIELDS)
    n=len(client_rows)
    summary={'visitas_loja':len(visits),'clientes_unicos_com_loja':n,
       'clientes_que_usaram_ura_30d':sum(int(v['qtd_ura_30d'])>0 for v in client_rows),
       'clientes_que_usaram_app_30d':sum(int(v['qtd_app_30d'])>0 for v in client_rows),
       'clientes_que_usaram_site_30d':sum(int(v['qtd_site_30d'])>0 for v in client_rows),
       'clientes_com_suporte_30d':sum(int(v['qtd_suporte_30d'])>0 for v in client_rows),
       'clientes_com_tecnico_30d':sum(int(v['qtd_tecnicos_30d'])>0 for v in client_rows),
       'clientes_multicanal_30d':sum(int(v['multicanal_antes_loja']) for v in client_rows),
       'percentual_ura_pre_loja':fmt_ratio(sum(int(v['qtd_ura_30d'])>0 for v in client_rows),n),
       'percentual_multicanal_pre_loja':fmt_ratio(sum(int(v['multicanal_antes_loja']) for v in client_rows),n),
       'observacao':'Denominador: contratos/clientes unicos com ao menos uma visita; ultima visita na janela. Valores sinteticos.'}
    save_json(REPORTS/'poc02_kpis.json',summary)
    print(f'[POC02] {len(visits)} visitas a loja, {n} clientes unicos e {len(trans_rows)} arestas de transicao')
    return {'kpis':summary,'transitions':trans_rows,'visits':visits}
