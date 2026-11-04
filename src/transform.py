"""Bronze -> Silver canonical event model -> Gold star schema.

All transformations are deterministic, source IDs and hash lineage preserved.
"""
from __future__ import annotations
import csv
import sqlite3
import shutil
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from .config import (RAW,BRONZE,SILVER,GOLD,WAREHOUSE,COHORT_START,COHORT_END,
                     WINDOW_DAYS,SOURCE_FILES)
from .utils import read_csv,write_csv,save_json,parse_datetime,fmt_ratio,is_true

EVENT_HEADERS=['evento_id','cliente_hash','contrato_id','dt_evento','canal','tipo_evento',
               'categoria','status','resolvido','texto','fonte','id_origem','competidor','produto','mes_ref']
CAUSE_HEADERS=['cancelamento_id','cliente_hash','contrato_id','produto','dt_cancelamento',
               'motivo_declarado','causa_principal','confianca','escore_principal','motivos_contribuintes',
               'num_contatos_180d','num_canais_180d','num_chamadas_180d','qtd_visitas_loja_180d',
               'qtd_visitas_tecnicas_180d','tickets_abertos_180d','faturas_inadimplentes_180d',
               'reclamacoes_180d','portabilidade_confirmada','destino_portabilidade',
               'tempo_primeiro_contato_ate_cancelamento_dias']
EVIDENCE_HEADERS=['cancelamento_id','cliente_hash','motivo','pontuacao','tipo_evidencia',
                  'fonte','id_origem','dt_evidencia','descricao']
BRIDGE_HEADERS=['cancelamento_id','cliente_hash','motivo','escore','papel']


def build_bronze():
    BRONZE.mkdir(parents=True,exist_ok=True)
    for name in SOURCE_FILES:
        source=RAW/f'{name}.csv'
        if not source.exists():
            raise FileNotFoundError(f'Fonte sintética inexistente: {source}; execute --generate')
        shutil.copy2(source,BRONZE/source.name)
    print('[BRONZE] Copias integrais de fontes com cabecalhos preservados')


def build_silver():
    SILVER.mkdir(parents=True,exist_ok=True)
    raw={n:read_csv(BRONZE/f'{n}.csv') for n in SOURCE_FILES}
    products={r['contrato_id']:r['produto'] for r in raw['contratos']}
    events=[]

    def event(table,row,oid,when,channel,topic,status,resolved,etype,text='',competitor=''):
        if not when:
            return
        dt=parse_datetime(when)
        evt={'evento_id':f'{table}:{oid}', 'cliente_hash':row['cliente_hash'],
             'contrato_id':row['contrato_id'],'dt_evento':when,'canal':channel,
             'tipo_evento':etype,'categoria':topic,'status':status,'resolvido':str(int(bool(resolved))),
             'texto':text,'fonte':table,'id_origem':oid,'competidor':competitor,
             'produto':products[row['contrato_id']],'mes_ref':dt.strftime('%Y%m')}
        events.append(evt)

    for r in raw['ura_ligacoes']:
        channel='URA_INBOUND' if r['direcao']=='INBOUND' else 'URA_OUTBOUND'
        event('ura_ligacoes',r,r['ligacao_id'],r['dt_hora'],channel,r['tema_registrado'],
              'CONCLUIDO' if is_true(r['resolvido_primeiro_contato']) else 'NAO_RESOLVIDO',
              is_true(r['resolvido_primeiro_contato']),'LIGACAO',r['transcricao_ficticia'])
    for r in raw['loja_atendimentos']:
        ch='LOJA_PROPRIA' if r['tipo_loja']=='PROPRIA' else 'PONTO_VENDA'
        event('loja_atendimentos',r,r['atendimento_loja_id'],r['dt_hora'],ch,r['motivo_visita'],
              'RESOLVIDO' if is_true(r['resolvido']) else 'NAO_RESOLVIDO',is_true(r['resolvido']),
              'ATENDIMENTO_LOJA')
    for r in raw['digital_interacoes']:
        event('digital_interacoes',r,r['interacao_digital_id'],r['dt_hora'],r['plataforma'],
              r['tema'],r['resultado'],r['resultado']=='CONCLUIDO',r['acao'])
    for r in raw['suporte_tickets']:
        event('suporte_tickets',r,r['ticket_id'],r['dt_abertura'],'SUPORTE',r['categoria'],
              r['status'],r['status']=='FECHADO','TICKET_ABERTO')
        # One event per ticket; lifecycle is carried by source columns.
    for r in raw['visitas_tecnicas']:
        event('visitas_tecnicas',r,r['visita_id'],r['dt_hora'],'TECNICO_RESIDENCIAL',
              'tecnico',r['status_visita'],r['status_visita']=='RESOLVIDO','VISITA_TECNICA')
    for r in raw['faturas']:
        event('faturas',r,r['fatura_id'],r['dt_vencimento'],'FINANCEIRO','financeiro' if r['status_pagamento'] in ('INADIMPLENTE','EM_ATRASO') else 'informacao',
              r['status_pagamento'],r['status_pagamento'] in ('PAGO','PAGO_COM_ATRASO'),'FATURA')
    for r in raw['acordos_financeiros']:
        event('acordos_financeiros',r,r['acordo_id'],r['dt_hora'],'FINANCEIRO',
              'financeiro',r['status_acordo'],r['status_acordo']=='EM_DIA','ACORDO_FINANCEIRO')
    for r in raw['reclamacoes']:
        event('reclamacoes',r,r['reclamacao_id'],r['dt_hora'],'RECLAMACAO',
              r['tema'],r['status'],r['status']=='RESOLVIDA','RECLAMACAO',r['texto_ficticio'])
    for r in raw['portabilidades']:
        event('portabilidades',r,r['portabilidade_id'],r['dt_evento'],'PORTABILIDADE',
              'concorrencia','CONFIRMADA' if is_true(r['verificacao_autorizada']) else 'NAO_CONFIRMADA',
              is_true(r['verificacao_autorizada']),'PORTABILIDADE',competitor=r['prestadora_destino'])
    for r in raw['pesquisas_saida']:
        event('pesquisas_saida',r,r['pesquisa_id'],r['dt_hora'],'PESQUISA_SAIDA',
              r['resposta_motivo'],'REGISTRADA',False,'PESQUISA_SAIDA',competitor=r['concorrente_declarado'])
    for r in raw['cancelamentos']:
        event('cancelamentos',r,r['cancelamento_id'],r['dt_cancelamento'],'CANCELAMENTO',
              r['motivo_declarado'],r['tipo_cancelamento'],False,'CANCELAMENTO')
    events.sort(key=lambda r:(r['cliente_hash'],r['dt_evento'],r['evento_id']))
    write_csv(SILVER/'eventos_canonicos.csv',events,EVENT_HEADERS)
    save_json(SILVER/'lineage.json',{'source_count':len(SOURCE_FILES),'event_count':len(events),
               'source_lineage':'evento_id=fonte:id_origem',
               'note':'ofertas_mercado relaciona por mes_ref, regiao e produto, NAO por cliente_hash.'})
    print(f'[SILVER] {len(events)} eventos com chave de cliente e origem identificavel')
    return raw,events


def _collect_causes(c:dict, customer_events:list, raw:dict, product:str):
    """Explainable evidence scoring; intentionally no prediction/ML claims."""
    cancel_at=parse_datetime(c['dt_cancelamento'])
    start=cancel_at-timedelta(days=WINDOW_DAYS)
    prior=[e for e in customer_events if start<=parse_datetime(e['dt_evento'])<cancel_at and e['tipo_evento']!='CANCELAMENTO']
    ids={e['evento_id']:e for e in prior}
    evs=[]
    def add(reason,score,kind,source,origin,when,detail):
        evs.append({'cancelamento_id':c['cancelamento_id'],'cliente_hash':c['cliente_hash'],
                    'motivo':reason,'pontuacao':score,'tipo_evidencia':kind,'fonte':source,
                    'id_origem':origin,'dt_evidencia':when,'descricao':detail})
    complaints=[e for e in prior if e['fonte']=='reclamacoes' and e['status']!='RESOLVIDA']
    for e in complaints:
        reason=e['categoria']
        if reason not in ('tecnico','financeiro','atendimento','preco_oferta','comercial'):
            continue
        add(reason,2,'reclamacao_nao_resolvida',e['fonte'],e['id_origem'],e['dt_evento'],'Reclamacao vinculada, status nao resolvida')
    technical_tickets=[e for e in prior if e['fonte']=='suporte_tickets' and e['status']!='FECHADO']
    for e in technical_tickets:
        add('tecnico',3,'ticket_aberto',e['fonte'],e['id_origem'],e['dt_evento'],'Solicitacao de suporte ainda aberta')
    technical_visits=[e for e in prior if e['fonte']=='visitas_tecnicas']
    for e in technical_visits:
        if not is_true(e['resolvido']):
            add('tecnico',2,'visita_sem_solucao',e['fonte'],e['id_origem'],e['dt_evento'],'Visita tecnica sem resolucao')
    unpaid=[e for e in prior if e['fonte']=='faturas' and e['status']=='INADIMPLENTE']
    for e in unpaid:
        add('financeiro',2,'fatura_inadimplente',e['fonte'],e['id_origem'],e['dt_evento'],'Fatura com status inadimplente')
    broken=[e for e in prior if e['fonte']=='acordos_financeiros' and e['status']=='QUEBRADO']
    for e in broken:
        add('financeiro',3,'acordo_quebrado',e['fonte'],e['id_origem'],e['dt_evento'],'Renegociacao com acordo quebrado')
    calls=[e for e in prior if e['fonte']=='ura_ligacoes']
    unresolved_calls=[e for e in calls if e['status']=='NAO_RESOLVIDO']
    if len(unresolved_calls)>=3:
        first=unresolved_calls[0]
        add('atendimento',3,'reincidencia_ura','ura_ligacoes',first['id_origem'],first['dt_evento'],
            f'{len(unresolved_calls)} chamadas sem resolucao no intervalo')
    for e in calls:
        if e['categoria'] in ('preco_oferta','comercial'):
            add(e['categoria'],2,'relato_chamada',e['fonte'],e['id_origem'],e['dt_evento'],'Relato tematico em chamada sintetica')
        elif e['categoria']=='tecnico' and e['status']=='NAO_RESOLVIDO':
            add('tecnico',1,'falha_relatada','ura_ligacoes',e['id_origem'],e['dt_evento'],'Chamada com problema tecnico nao resolvido')
        elif e['categoria']=='atendimento' and e['status']=='NAO_RESOLVIDO':
            add('atendimento',1,'falha_atendimento','ura_ligacoes',e['id_origem'],e['dt_evento'],'Insatisfacao no atendimento')
    for e in prior:
        if e['fonte']=='loja_atendimentos' and e['status']=='NAO_RESOLVIDO':
            if e['categoria'] in ('atendimento','comercial','tecnico','preco_oferta','financeiro'):
                add(e['categoria'],1,'loja_sem_solucao',e['fonte'],e['id_origem'],e['dt_evento'],'Atendimento presencial sem resolucao')
        if e['fonte']=='digital_interacoes' and e['status']=='SEM_SOLUCAO' and e['categoria'] in ('atendimento','preco_oferta','comercial','tecnico'):
            add(e['categoria'],1,'digital_sem_solucao',e['fonte'],e['id_origem'],e['dt_evento'],'Tentativa digital nao resolvida')
    ports=[e for e in prior if e['fonte']=='portabilidades' and e['status']=='CONFIRMADA']
    # Portability on same date but after cancel timestamp is intentionally not a pre-cancel event.
    for p in ports:
        add('concorrencia',8,'portabilidade_autorizada','portabilidades',p['id_origem'],p['dt_evento'],
            f'Evento sintetico confirmado para {p["competidor"]}')
    # Exit survey is retrospective, not a pre-cancellation contact. No unlicensed external match.
    surveys=[s for s in raw['pesquisas_saida']
             if s['cliente_hash']==c['cliente_hash'] and s['contrato_id']==c['contrato_id'] and is_true(s['autorizado'])]
    for s in surveys:
        reason=s['resposta_motivo']
        if reason in ('tecnico','financeiro','atendimento','preco_oferta','comercial'):
            add(reason,2,'declaracao_pesquisa_saida','pesquisas_saida',s['pesquisa_id'],s['dt_hora'],'Declaracao retrospectiva voluntaria')
        if reason=='concorrencia' and s['concorrente_declarado']:
            add('concorrencia',5,'concorrente_autodeclarado','pesquisas_saida',s['pesquisa_id'],s['dt_hora'],
                f'Cliente declarou mudanca para {s["concorrente_declarado"]}')
    totals=defaultdict(int)
    for e in evs:
        totals[e['motivo']]+=e['pontuacao']
    # Requirement: indeterminate stays indeterminate, not force-fit to a competitor.
    best=max(totals, key=lambda x:(totals[x], x)) if totals else 'indeterminado'
    score=totals[best] if totals else 0
    if score<2:
        best='indeterminado'
    unique_sources={e['fonte'] for e in evs if e['motivo']==best}
    if best=='indeterminado':
        confidence='SEM_EVIDENCIA'
    elif any(e['motivo']==best and e['tipo_evidencia']=='portabilidade_autorizada' for e in evs):
        confidence='ALTA_CONFIRMADA'
    elif score>=5 and len(unique_sources)>=2:
        confidence='ALTA_CORROBORADA'
    elif score>=3:
        confidence='MEDIA'
    else:
        confidence='BAIXA'
    contributing=sorted(m for m,points in totals.items() if m!=best and points>=2)
    bridge=[]
    for reason,points in sorted(totals.items()):
        if points>=2:
            bridge.append({'cancelamento_id':c['cancelamento_id'],'cliente_hash':c['cliente_hash'],
                           'motivo':reason,'escore':points,'papel':'PRINCIPAL' if reason==best else 'CONTRIBUINTE'})
    if not bridge:
        bridge.append({'cancelamento_id':c['cancelamento_id'],'cliente_hash':c['cliente_hash'],
                       'motivo':'indeterminado','escore':0,'papel':'PRINCIPAL'})
    first=min((parse_datetime(e['dt_evento']) for e in prior if e['canal'] not in ('FINANCEIRO','PESQUISA_SAIDA')),default=None)
    out={'cancelamento_id':c['cancelamento_id'],'cliente_hash':c['cliente_hash'],
         'contrato_id':c['contrato_id'],'produto':product,'dt_cancelamento':c['dt_cancelamento'],
         'motivo_declarado':c['motivo_declarado'],'causa_principal':best,'confianca':confidence,
         'escore_principal':score if best!='indeterminado' else 0,
         'motivos_contribuintes':'|'.join(contributing),
         'num_contatos_180d':sum(e['canal'] not in ('FINANCEIRO','PESQUISA_SAIDA') for e in prior),
         'num_canais_180d':len({e['canal'] for e in prior if e['canal'] not in ('FINANCEIRO','PESQUISA_SAIDA')}),
         'num_chamadas_180d':len(calls),'qtd_visitas_loja_180d':sum(e['fonte']=='loja_atendimentos' for e in prior),
         'qtd_visitas_tecnicas_180d':len(technical_visits),'tickets_abertos_180d':len(technical_tickets),
         'faturas_inadimplentes_180d':len(unpaid),'reclamacoes_180d':len(complaints),
         'portabilidade_confirmada':int(len(ports)>0),
         'destino_portabilidade':ports[0]['competidor'] if ports else '',
         'tempo_primeiro_contato_ate_cancelamento_dias':(cancel_at-first).days if first else ''}
    return out,evs,bridge


def build_gold(raw,events):
    GOLD.mkdir(parents=True,exist_ok=True)
    products={r['contrato_id']:r['produto'] for r in raw['contratos']}
    by_customer=defaultdict(list)
    for e in events:
        by_customer[(e['cliente_hash'],e['contrato_id'])].append(e)
    causes=[]; evidences=[]; bridges=[]
    for c in raw['cancelamentos']:
        c_row,ev,bridge=_collect_causes(c,by_customer[(c['cliente_hash'],c['contrato_id'])],raw,products[c['contrato_id']])
        causes.append(c_row);evidences+=ev;bridges+=bridge
    write_csv(GOLD/'dim_cliente.csv',raw['clientes'],list(raw['clientes'][0]))
    write_csv(GOLD/'dim_contrato.csv',raw['contratos'],list(raw['contratos'][0]))
    dim_canal=[{'canal':c,'grupo_canal':group} for c,group in [
        ('URA_INBOUND','VOZ'),('URA_OUTBOUND','VOZ'),('LOJA_PROPRIA','PRESENCIAL'),('PONTO_VENDA','PRESENCIAL'),
        ('APP','DIGITAL'),('SITE','DIGITAL'),('SUPORTE','SUPORTE'),('TECNICO_RESIDENCIAL','TECNICO'),
        ('FINANCEIRO','FINANCEIRO'),('RECLAMACAO','OUVIDORIA'),('PESQUISA_SAIDA','PESQUISA'),
        ('PORTABILIDADE','EXTERNO'),('CANCELAMENTO','CANCELAMENTO')]]
    write_csv(GOLD/'dim_canal.csv',dim_canal,['canal','grupo_canal'])
    dim_reason=[{'motivo':r,'descricao':d} for r,d in [
        ('tecnico','Falha tecnica/qualidade do servico'),('financeiro','Inadimplencia/renegociacao'),
        ('atendimento','Friccao, transferencias, repeticao'),('preco_oferta','Preco/valor percebido'),
        ('concorrencia','Portabilidade ou concorrente explicitamente informado'),
        ('comercial','Venda, contratacao e plano'),('indeterminado','Sem evidencia suficiente')]]
    write_csv(GOLD/'dim_motivo.csv',dim_reason,['motivo','descricao'])
    dim_time=[]
    dt=datetime(2026,4,1)
    while dt.date()<=datetime(2026,10,31).date():
        dim_time.append({'data':dt.strftime('%Y-%m-%d'),'ano':dt.year,'mes':dt.month,
                         'mes_ref':dt.strftime('%Y%m'),'dia':dt.day,'dia_semana':dt.weekday()})
        dt+=timedelta(days=1)
    write_csv(GOLD/'dim_tempo.csv',dim_time,list(dim_time[0]))
    write_csv(GOLD/'fct_jornada_eventos.csv',events,EVENT_HEADERS)
    write_csv(GOLD/'fct_cancelamentos_analitica.csv',causes,CAUSE_HEADERS)
    write_csv(GOLD/'fct_evidencias_motivo.csv',evidences,EVIDENCE_HEADERS)
    write_csv(GOLD/'bridge_cancelamento_motivo.csv',bridges,BRIDGE_HEADERS)
    write_csv(GOLD/'fct_ofertas_mercado.csv',raw['ofertas_mercado'],list(raw['ofertas_mercado'][0]))
    # 30-day support resolution as of cutoff: no events after cancellation treated as solved pre-churn.
    cancels={(r['cliente_hash'],r['contrato_id']):parse_datetime(r['dt_cancelamento']) for r in raw['cancelamentos']}
    resolution=[]
    for r in raw['suporte_tickets']:
        opened=parse_datetime(r['dt_abertura']); closed=parse_datetime(r['dt_fechamento']) if r['dt_fechamento'] else None
        cutoff=cancels.get((r['cliente_hash'],r['contrato_id']),datetime(2026,10,31,23,59,59))
        eligible=closed is not None and closed <= cutoff and closed >= opened
        days=round((closed-opened).total_seconds()/86400,2) if eligible else ''
        resolution.append({'ticket_id':r['ticket_id'],'cliente_hash':r['cliente_hash'],'contrato_id':r['contrato_id'],
          'dt_abertura':r['dt_abertura'],'dt_fechamento':r['dt_fechamento'],
          'resolvido_ate_corte':int(eligible),'resolvido_em_30_dias':int(eligible and days<=30),
          'tempo_resolucao_dias':days,'status_orig':r['status']})
    write_csv(GOLD/'fct_resolucao_30d.csv',resolution,list(resolution[0]) if resolution else [
        'ticket_id','cliente_hash','contrato_id','dt_abertura','dt_fechamento','resolvido_ate_corte',
        'resolvido_em_30_dias','tempo_resolucao_dias','status_orig'])
    print(f'[GOLD] {len(causes)} cancelamentos; {len(evidences)} evidencias; {len(events)} eventos')
    return {'causes':causes,'events':events,'evidences':evidences,'bridge':bridges,'resolution':resolution,'raw':raw}


def _write_database():
    """SQLite portable local warehouse; tables in CSV also directly loadable in DuckDB/Power BI."""
    WAREHOUSE.parent.mkdir(parents=True,exist_ok=True)
    if WAREHOUSE.exists():
        WAREHOUSE.unlink()
    db=sqlite3.connect(WAREHOUSE)
    try:
        for path in sorted(GOLD.glob('*.csv')):
            with path.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f)
                cols=reader.fieldnames
                if not cols: continue
                safe_table=path.stem
                quoted=', '.join(f'"{col}" TEXT' for col in cols)
                db.execute(f'CREATE TABLE "{safe_table}" ({quoted})')
                insert_sql=f'INSERT INTO "{safe_table}" VALUES ({", ".join("?" for _ in cols)})'
                db.executemany(insert_sql, ([r[col] for col in cols] for r in reader))
        db.execute('CREATE INDEX idx_jornada_chave_tempo ON fct_jornada_eventos(cliente_hash,dt_evento)')
        db.execute('CREATE INDEX idx_cancelamento_chave ON fct_cancelamentos_analitica(cliente_hash)')
        db.execute('CREATE INDEX idx_ponte_motivo ON bridge_cancelamento_motivo(motivo)')
        db.commit()
    finally:
        db.close()
