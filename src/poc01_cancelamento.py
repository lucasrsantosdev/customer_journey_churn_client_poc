"""POC 01 — auditable churn classification, call tags and retention opportunities."""
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from .config import GOLD,REPORTS,WINDOW_DAYS
from .utils import read_csv,write_csv,save_json,fmt_ratio,parse_datetime

CALL_FIELDS=['ligacao_id','cliente_hash','contrato_id','dt_hora','direcao','produto',
             'tema_origem','tema_identificado','confianca_rotulagem','metodo','cancelou_outubro',
             'em_janela_180d_pre_cancelamento','texto_ficticio']
OPPORTUNITY_FIELDS=['cancelamento_id','cliente_hash','produto','causa_principal',
                    'gatilho','oportunidade','prioridade','hipotese_medicao']

TAGS={
    'tecnico':['sem sinal','queda','instabilidade','falha tecnica','lento','roteador'],
    'financeiro':['fatura','renegociar','atraso','parcelamento','inadimplencia'],
    'atendimento':['atendimento','nao resolveu','transferido','repetir'],
    'preco_oferta':['preco','caro','desconto','promocao','valor mensal'],
    'concorrencia':['portabilidade','outra operadora','vivo','tim','algar'],
    'comercial':['plano errado','contratacao','venda']}
ACTIONS={
 'tecnico':('ticket_aberto_ou_visita_recorrente','priorizar diagnostico definitivo e retorno proativo','ALTA','Reducao de reincidencia e tempo ate resolucao'),
 'financeiro':('inadimplencia_ou_acordo_quebrado','oferecer jornada de negociacao proporcional e transparente','ALTA','Taxa de acordos mantidos e recuperacao'),
 'atendimento':('multiplos_contatos_nao_resolvidos','repassar historico entre canais e resolver no primeiro contato','ALTA','FCR e contatos por solicitacao'),
 'preco_oferta':('relato_preco_e_valor','avaliar adequacao de plano e ofertas conforme elegibilidade','MEDIA','Aceite de oferta e permanencia'),
 'concorrencia':('autodeclaracao_ou_portabilidade_autorizada','investigar competitividade antes do cancelamento sem presumir motivo','MEDIA','Variacao de churn por oferta e segmento'),
 'comercial':('plano_ou_venda_divergente','corrigir divergencia entre promessa de venda e contrato','ALTA','Reclamacoes e retrabalho comercial'),
 'indeterminado':('ausencia_de_evidencia','aperfeicoar coleta de motivo de saida e cobertura dos canais','ALTA','Reducao de motivos sem evidencia')
}

def _classify_call(text):
    value=text.casefold()
    matches={cat:sum(p in value for p in words) for cat,words in TAGS.items()}
    best=max(matches,key=matches.get)
    if matches[best]==0:
        return 'informacao','BAIXA'
    return best,'MEDIA' if matches[best]==1 else 'ALTA'


def run(payload):
    REPORTS.mkdir(parents=True,exist_ok=True)
    raw=payload['raw']; causes=payload['causes']
    contracts={r['contrato_id']:r['produto'] for r in raw['contratos']}
    cancel_dates={(r['cliente_hash'],r['contrato_id']):parse_datetime(r['dt_cancelamento']) for r in raw['cancelamentos']}
    labeled=[]
    for r in raw['ura_ligacoes']:
        label,confidence=_classify_call(r['transcricao_ficticia'])
        end=cancel_dates.get((r['cliente_hash'],r['contrato_id']))
        at=parse_datetime(r['dt_hora'])
        in_window=bool(end and end-timedelta(days=WINDOW_DAYS)<=at<end)
        labeled.append({'ligacao_id':r['ligacao_id'],'cliente_hash':r['cliente_hash'],
         'contrato_id':r['contrato_id'],'dt_hora':r['dt_hora'],'direcao':r['direcao'],
         'produto':contracts[r['contrato_id']],'tema_origem':r['tema_registrado'],
         'tema_identificado':label,'confianca_rotulagem':confidence,'metodo':'REGRAS_DEMO_PALAVRAS_CHAVE',
         'cancelou_outubro':int(end is not None),'em_janela_180d_pre_cancelamento':int(in_window),
         'texto_ficticio':r['transcricao_ficticia']})
    write_csv(GOLD/'fct_ligacoes_classificadas.csv',labeled,CALL_FIELDS)
    by_product=defaultdict(Counter); total_prod=Counter()
    confidence=Counter(); declared_vs_inferred=Counter()
    for c in causes:
        by_product[c['produto']][c['causa_principal']]+=1
        total_prod[c['produto']]+=1
        confidence[c['confianca']]+=1
        declared_vs_inferred[(c['motivo_declarado'],c['causa_principal'])]+=1
    reason_rows=[]
    for product in sorted(total_prod):
        for reason in sorted(set(ACTIONS)):
            count=by_product[product][reason]
            reason_rows.append({'produto':product,'causa_principal':reason,'cancelamentos':count,
                                'total_cancelamentos_produto':total_prod[product],
                                'percentual_cancelamentos_produto':fmt_ratio(count,total_prod[product])})
    write_csv(REPORTS/'poc01_motivos_por_produto.csv',reason_rows,list(reason_rows[0]))
    crosstab=[{'motivo_declarado':d,'motivo_inferido':i,'clientes':n} for (d,i),n in sorted(declared_vs_inferred.items())]
    write_csv(REPORTS/'poc01_declarado_vs_inferido.csv',crosstab,['motivo_declarado','motivo_inferido','clientes'])
    opportunities=[]
    for c in causes:
        trigger,action,prio,metric=ACTIONS[c['causa_principal']]
        opportunities.append({'cancelamento_id':c['cancelamento_id'],'cliente_hash':c['cliente_hash'],
           'produto':c['produto'],'causa_principal':c['causa_principal'],
           'gatilho':trigger,'oportunidade':action,'prioridade':prio,'hipotese_medicao':metric})
    write_csv(REPORTS/'poc01_oportunidades.csv',opportunities,OPPORTUNITY_FIELDS)
    calls_cancel=[r for r in labeled if r['em_janela_180d_pre_cancelamento']==1]
    calls_by_tag=Counter(r['tema_identificado'] for r in calls_cancel)
    calls_summary=[{'tema':tag,'quantidade_ligacoes':cnt,
                    'percentual_ligacoes':fmt_ratio(cnt,len(calls_cancel))} for tag,cnt in sorted(calls_by_tag.items())]
    write_csv(REPORTS/'poc01_ligacoes_por_tema.csv',calls_summary,['tema','quantidade_ligacoes','percentual_ligacoes'])
    all_call_tags=Counter(r['tema_identificado'] for r in labeled)
    write_csv(REPORTS/'poc01_ligacoes_todas_por_tema.csv',
              [{'tema':tag,'quantidade_ligacoes':count,'percentual_ligacoes':fmt_ratio(count,len(labeled))} 
               for tag,count in sorted(all_call_tags.items())],['tema','quantidade_ligacoes','percentual_ligacoes'])
    details={'coorte':'2026-10','cancelamentos':len(causes),'clientes_sinteticos':len(raw['clientes']),
     'movel_cancelamentos':total_prod['MOVEL'],'fixa_cancelamentos':total_prod['FIXA'],
     'ligacoes_analisadas':len(labeled),'ligacoes_cancelados_180d':len(calls_cancel),'percentual_indeterminado':fmt_ratio(sum(c['causa_principal']=='indeterminado' for c in causes),len(causes)),
     'confiancas':dict(confidence), 'nota':'Percentuais inteiramente sinteticos; nao representam a CLARO.'}
    save_json(REPORTS/'poc01_kpis.json',details)
    print(f'[POC01] {len(causes)} cancelamentos e {len(labeled)} ligacoes etiquetadas; {len(opportunities)} oportunidades')
    return {'kpis':details,'reasons':reason_rows,'calls':calls_summary,'opportunities':opportunities}
