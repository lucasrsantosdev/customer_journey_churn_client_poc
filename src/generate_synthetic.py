"""Fully fabricated, deterministic source-system headers and sample records.

No customer, phone, invoice, store interaction or claim in this file is real.
"""
from __future__ import annotations
import random
from collections import defaultdict
from datetime import datetime, date, timedelta
from .config import RAW, SEED, CALENDAR_START, COHORT_END
from .utils import customer_key, write_csv, save_json

HEADERS = {
    'clientes': ['cliente_hash', 'segmento', 'uf', 'cidade', 'regiao', 'dt_ativacao', 'perfil_sintetico'],
    'contratos': ['contrato_id', 'cliente_hash', 'produto', 'plano', 'mensalidade', 'dt_inicio', 'status_atual'],
    'cancelamentos': ['cancelamento_id', 'cliente_hash', 'contrato_id', 'dt_cancelamento', 'canal_solicitacao', 'motivo_declarado', 'tipo_cancelamento'],
    'ura_ligacoes': ['ligacao_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'direcao', 'tema_registrado', 'protocolo', 'duracao_seg', 'transferencias', 'resolvido_primeiro_contato', 'transcricao_ficticia'],
    'loja_atendimentos': ['atendimento_loja_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'loja_id', 'tipo_loja', 'motivo_visita', 'protocolo', 'resolvido'],
    'digital_interacoes': ['interacao_digital_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'plataforma', 'acao', 'tema', 'protocolo', 'resultado'],
    'suporte_tickets': ['ticket_id', 'cliente_hash', 'contrato_id', 'dt_abertura', 'dt_fechamento', 'canal_abertura', 'categoria', 'status', 'resultado'],
    'visitas_tecnicas': ['visita_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'ordem_servico', 'diagnostico', 'status_visita', 'visita_repetida'],
    'faturas': ['fatura_id', 'cliente_hash', 'contrato_id', 'mes_ref', 'dt_vencimento', 'valor', 'dt_pagamento', 'status_pagamento', 'dias_atraso'],
    'acordos_financeiros': ['acordo_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'valor_renegociado', 'qtd_parcelas', 'status_acordo'],
    'reclamacoes': ['reclamacao_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'origem', 'tema', 'status', 'dt_resolucao', 'texto_ficticio'],
    'portabilidades': ['portabilidade_id', 'cliente_hash', 'contrato_id', 'dt_evento', 'prestadora_destino', 'fonte_registro', 'verificacao_autorizada'],
    'pesquisas_saida': ['pesquisa_id', 'cliente_hash', 'contrato_id', 'dt_hora', 'resposta_motivo', 'concorrente_declarado', 'nota_atendimento', 'autorizado'],
    'ofertas_mercado': ['oferta_id', 'mes_ref', 'regiao', 'produto', 'prestadora', 'valor_mensal', 'tipo_oferta', 'fonte_publica', 'validade_inicio', 'validade_fim']
}

REGIONS = [('SP', 'Santo Andre', 'SUDESTE'), ('RJ', 'Rio de Janeiro', 'SUDESTE'),
           ('MG', 'Belo Horizonte', 'SUDESTE'), ('PR', 'Curitiba', 'SUL'),
           ('BA', 'Salvador', 'NORDESTE'), ('PE', 'Recife', 'NORDESTE'),
           ('GO', 'Goiania', 'CENTRO_OESTE')]
TOPIC_TEXT = {
    'tecnico': 'Cliente relata sem sinal e instabilidade, solicita suporte para falha tecnica.',
    'financeiro': 'Cliente relata fatura em atraso e solicita renegociar parcelamento.',
    'atendimento': 'Cliente diz que atendimento anterior nao resolveu, precisou repetir e foi transferido.',
    'preco_oferta': 'Cliente considera preco caro e deseja desconto no valor mensal do plano.',
    'concorrencia': 'Cliente quer informacoes de portabilidade para outra operadora.',
    'comercial': 'Cliente informa plano errado na contratacao e solicita ajuste de venda.',
    'informacao': 'Cliente solicita informacao de segunda via e dados do plano, sem reclamacao.'
}


def _dt_str(value: datetime) -> str:
    return value.strftime('%Y-%m-%dT%H:%M:%S')


def _at(rng: random.Random, base: date, hour_min=8, hour_max=19) -> datetime:
    return datetime.combine(base, datetime.min.time()).replace(hour=rng.randint(hour_min, hour_max), minute=rng.randint(0, 59))


def _before(rng: random.Random, cutoff: date, min_days: int, max_days: int) -> datetime:
    d = cutoff - timedelta(days=rng.randint(min_days, max_days))
    if d < CALENDAR_START:
        d = CALENDAR_START + timedelta(days=rng.randint(0, 6))
    return _at(rng, d)


def generate(n_customers=600, n_cancel=240):
    """Create 14 reproducible mock source datasets, preserving individual joins."""
    rng = random.Random(SEED)
    rows = defaultdict(list)
    id_count = defaultdict(int)

    def add(table, **values):
        id_count[table] += 1
        rows[table].append(values)

    def nextid(prefix, table):
        return f'{prefix}-{id_count[table]+1:06d}'

    cancelled_ids = set(rng.sample(range(n_customers), n_cancel))
    profiles = ['tecnico', 'financeiro', 'atendimento', 'preco_oferta', 'concorrencia', 'comercial', 'indeterminado']
    profile_weights = [25, 22, 15, 13, 10, 8, 7]
    for idx in range(n_customers):
        key = customer_key(f'PESSOA_SINTETICA_{idx+1:07d}')
        contract = f'CTR-SIM-{idx+1:07d}'
        cancelled = idx in cancelled_ids
        product = rng.choices(['MOVEL', 'FIXA'], weights=[58, 42], k=1)[0]
        uf, city, region = rng.choice(REGIONS)
        profile = rng.choices(profiles, weights=profile_weights, k=1)[0] if cancelled else rng.choice(['estavel', 'informacao', 'tecnico', 'atendimento'])
        cancel_date = date(2026, 10, rng.randint(1, 31)) if cancelled else None
        cutoff = cancel_date or COHORT_END
        activation = date(2025, rng.randint(1, 12), rng.randint(1, 28))
        monthly = round(rng.uniform(39, 129) if product == 'MOVEL' else rng.uniform(79, 199), 2)
        plan = rng.choice(['Controle 20GB', 'Pos 40GB', 'Pos 80GB']) if product == 'MOVEL' else rng.choice(['Fibra 300M', 'Fibra 500M', 'Fibra 750M'])
        add('clientes', cliente_hash=key, segmento='PF', uf=uf, cidade=city, regiao=region, dt_ativacao=activation, perfil_sintetico=profile)
        add('contratos', contrato_id=contract, cliente_hash=key, produto=product, plano=plan,
            mensalidade=f'{monthly:.2f}', dt_inicio=activation, status_atual='CANCELADO' if cancelled else 'ATIVO')

        def add_call(when, topic, direction='INBOUND', solved=False, transfers=0):
            add('ura_ligacoes', ligacao_id=nextid('CALL','ura_ligacoes'), cliente_hash=key, contrato_id=contract,
                dt_hora=_dt_str(when), direcao=direction, tema_registrado=topic,
                protocolo=nextid('P', 'ura_ligacoes'), duracao_seg=rng.randint(110, 1250),
                transferencias=transfers, resolvido_primeiro_contato=int(solved), transcricao_ficticia=TOPIC_TEXT[topic])

        def add_store(when, topic, resolved=False):
            add('loja_atendimentos', atendimento_loja_id=nextid('LJ', 'loja_atendimentos'), cliente_hash=key,
                contrato_id=contract, dt_hora=_dt_str(when), loja_id=f'LOJA-SIM-{rng.randint(1,12):03d}',
                tipo_loja=rng.choice(['PROPRIA', 'PONTO_VENDA']), motivo_visita=topic,
                protocolo=nextid('PLOJA','loja_atendimentos'), resolvido=int(resolved))

        def add_digital(when, topic, platform=None, result='SEM_SOLUCAO'):
            plat = platform or rng.choice(['APP','SITE'])
            add('digital_interacoes', interacao_digital_id=nextid('DIG','digital_interacoes'), cliente_hash=key,
                contrato_id=contract, dt_hora=_dt_str(when), plataforma=plat, acao='ABRIR_SOLICITACAO' if topic!='informacao' else 'CONSULTAR_CONTA',
                tema=topic, protocolo=nextid('PD','digital_interacoes'), resultado=result)

        def add_ticket(when, category, status='ABERTO', end=None):
            add('suporte_tickets', ticket_id=nextid('TIC','suporte_tickets'), cliente_hash=key,
                contrato_id=contract, dt_abertura=_dt_str(when), dt_fechamento=_dt_str(end) if end else '',
                canal_abertura=rng.choice(['URA', 'APP', 'SITE']), categoria=category, status=status,
                resultado='RESOLVIDO' if status=='FECHADO' else 'PENDENTE')

        def add_visit(when, repeated=False, status='NAO_RESOLVIDO'):
            if product != 'FIXA':
                return
            add('visitas_tecnicas', visita_id=nextid('TEC','visitas_tecnicas'), cliente_hash=key,
                contrato_id=contract, dt_hora=_dt_str(when), ordem_servico=nextid('OS','visitas_tecnicas'),
                diagnostico=rng.choice(['INSTABILIDADE_REDE','SINAL_FRACO','EQUIPAMENTO']),
                status_visita=status, visita_repetida=int(repeated))

        # Some neutral routine contacts in the comparative six full calendar months.
        if profile != 'indeterminado':
            if rng.random() < 0.58:
                add_digital(_before(rng, cutoff, 70, 165), 'informacao', result='CONCLUIDO')
            if rng.random() < 0.27:
                add_call(_before(rng, cutoff, 80, 170), 'informacao', solved=True)
            if rng.random() < 0.17:
                add_store(_before(rng, cutoff, 60, 155), 'informacao', resolved=True)

        if cancelled:
            declared = {
                'tecnico': 'problema_tecnico', 'financeiro': 'preco_alto',
                'atendimento': 'atendimento_ruim', 'preco_oferta': 'preco_alto',
                'concorrencia': 'sem_informacao', 'comercial': 'mudanca_plano',
                'indeterminado': 'sem_informacao'
            }[profile]
            if rng.random()<0.14:
                declared = rng.choice(['sem_informacao', 'preco_alto','outros'])
            add('cancelamentos', cancelamento_id=nextid('CAN', 'cancelamentos'), cliente_hash=key,
                contrato_id=contract, dt_cancelamento=_dt_str(_at(rng,cancel_date)),
                canal_solicitacao=rng.choice(['URA', 'LOJA','APP','SITE']),
                motivo_declarado=declared,
                tipo_cancelamento='VOLUNTARIO' if profile!='financeiro' or rng.random()<0.5 else 'INADIMPLENCIA')

        if profile=='tecnico':
            for j in range(rng.randint(2, 5) if cancelled else 1):
                add_call(_before(rng, cutoff, 3+j*8, 10+j*13), 'tecnico', solved=False, transfers=rng.randint(0,2))
            add_digital(_before(rng, cutoff, 17, 38), 'tecnico')
            opening = _before(rng,cutoff,14,36)
            add_ticket(opening, 'INSTABILIDADE', status='ABERTO' if cancelled else 'FECHADO',
                       end=None if cancelled else opening+timedelta(days=3))
            if product=='FIXA':
                add_visit(_before(rng,cutoff,15,27))
                if cancelled or rng.random()<0.25:
                    add_visit(_before(rng,cutoff,3,10),repeated=True)
            if cancelled and rng.random()<0.6:
                storewhen = _before(rng,cutoff,1,7)
                add_digital(storewhen-timedelta(days=3),'tecnico')
                add_store(storewhen,'tecnico')
        elif profile=='financeiro':
            add_call(_before(rng,cutoff,12,38), 'financeiro',solved=False,transfers=1)
            add_digital(_before(rng,cutoff,10,25), 'financeiro')
            if cancelled or rng.random()<0.4:
                add('acordos_financeiros', acordo_id=nextid('AC','acordos_financeiros'),cliente_hash=key,
                    contrato_id=contract,dt_hora=_dt_str(_before(rng,cutoff,12,30)),
                    valor_renegociado=f'{monthly*rng.uniform(1.6, 3.3):.2f}',qtd_parcelas=rng.randint(2,6),
                    status_acordo='QUEBRADO' if cancelled else 'EM_DIA')
            if cancelled and rng.random()<0.5:
                storewhen = _before(rng,cutoff,2,8)
                add_call(storewhen-timedelta(days=4),'financeiro')
                add_store(storewhen,'financeiro')
        elif profile=='atendimento':
            for j in range(4 if cancelled else 2):
                add_call(_before(rng,cutoff,2+j*6,5+j*9),'atendimento',solved=False,transfers=rng.randint(1,4))
            add_digital(_before(rng,cutoff,7,18),'atendimento')
            if cancelled:
                storewhen = _before(rng,cutoff,1,4)
                add_call(storewhen-timedelta(days=2),'atendimento',transfers=2)
                add_store(storewhen,'atendimento')
        elif profile=='preco_oferta':
            add_call(_before(rng,cutoff,6,19),'preco_oferta',solved=False)
            add_digital(_before(rng,cutoff,5,15),'preco_oferta')
            if cancelled and rng.random()<0.65:
                storewhen=_before(rng,cutoff,2,8)
                add_digital(storewhen-timedelta(days=1),'preco_oferta')
                add_store(storewhen,'preco_oferta')
        elif profile=='concorrencia':
            if cancelled and rng.random()<0.72:
                add_call(_before(rng,cutoff,2,10),'concorrencia',solved=False)
            if cancelled and product=='MOVEL' and rng.random()<0.60:
                operator=rng.choice(['VIVO','TIM','ALGAR'])
                add('portabilidades',portabilidade_id=nextid('PORT','portabilidades'),
                    cliente_hash=key,contrato_id=contract,dt_evento=_dt_str(_before(rng,cutoff,0,3)),
                    prestadora_destino=operator,fonte_registro='EVENTO_AUTORIZADO_SINTETICO',verificacao_autorizada=1)
        elif profile=='comercial':
            add_call(_before(rng,cutoff,6,22),'comercial',solved=False)
            add_digital(_before(rng,cutoff,5,16),'comercial')
            if cancelled and rng.random()<0.6:
                add_store(_before(rng,cutoff,1,8),'comercial')
        elif profile=='informacao' and rng.random()<0.2:
            add_call(_before(rng,cutoff,15,75),'informacao',solved=True)

        if cancelled and profile not in ('indeterminado',) and rng.random()<0.26:
            source=rng.choice(['RECLAME_AQUI', 'OUVIDORIA'])
            when=_before(rng,cutoff,4,24)
            add('reclamacoes',reclamacao_id=nextid('REC','reclamacoes'),cliente_hash=key,
                contrato_id=contract,dt_hora=_dt_str(when),origem=source,tema=profile,
                status='NAO_RESOLVIDA',dt_resolucao='',texto_ficticio=TOPIC_TEXT.get(profile, TOPIC_TEXT['informacao']))
        if cancelled and rng.random()<0.63:
            competitor = rng.choice(['VIVO','TIM','ALGAR']) if profile=='concorrencia' else ''
            add('pesquisas_saida',pesquisa_id=nextid('PS','pesquisas_saida'),cliente_hash=key,
                contrato_id=contract,dt_hora=_dt_str(_at(rng,cancel_date)),
                resposta_motivo=profile if profile!='indeterminado' else 'nao_informado',
                concorrente_declarado=competitor,nota_atendimento=rng.randint(1,10),autorizado=1)

        # Billing is a separate source; no invented join with offer data.
        for month in range(4,11):
            due=date(2026,month,15)
            if due>cutoff:
                continue
            late=profile=='financeiro' and cancelled and month in (max(4,cancel_date.month-2), max(4,cancel_date.month-1))
            if late:
                paid=''
                status='INADIMPLENTE'
                delay=max(0,(cutoff-due).days)
            elif rng.random()<0.10:
                delay=rng.randint(1,8)
                pay=due+timedelta(days=delay)
                if pay>cutoff:
                    paid=''
                    status='EM_ATRASO'
                else:
                    paid=pay.isoformat()
                    status='PAGO_COM_ATRASO'
            else:
                delay=0
                paid=due.isoformat()
                status='PAGO'
            add('faturas', fatura_id=nextid('FAT','faturas'),cliente_hash=key,
                contrato_id=contract,mes_ref=f'2026{month:02d}',dt_vencimento=due,
                valor=f'{monthly:.2f}',dt_pagamento=paid,status_pagamento=status,dias_atraso=delay)

    # External offers: public, contextual mock-up and deliberately NOT person keyed.
    for month in range(4, 11):
        for region in ['SUDESTE','SUL','NORDESTE','CENTRO_OESTE']:
            for product in ['MOVEL', 'FIXA']:
                for provider in ['VIVO','TIM','ALGAR']:
                    add('ofertas_mercado',oferta_id=nextid('OFT','ofertas_mercado'),
                        mes_ref=f'2026{month:02d}',regiao=region,produto=product,
                        prestadora=provider,valor_mensal=f'{rng.uniform(34,100) if product=="MOVEL" else rng.uniform(69,160):.2f}',
                        tipo_oferta=rng.choice(['CAMPANHA', 'PROMOCAO', 'PRECO_REGULAR']),
                        fonte_publica='FONTE_DEMONSTRATIVA_NAO_VALIDADA',
                        validade_inicio=date(2026,month,1),validade_fim=date(2026,month,28))

    RAW.mkdir(parents=True, exist_ok=True)
    manifest={}
    for table, headers in HEADERS.items():
        write_csv(RAW / f'{table}.csv', rows[table], headers)
        manifest[table]={'rows':len(rows[table]),'columns':headers,'synthetic':True,
                         'path':f'data/raw/synthetic/{table}.csv'}
    save_json(RAW/'manifest.json',{'seed':SEED,'customers':n_customers,
              'cancellations_oct_2026':n_cancel,'datasets':manifest,
              'warning':'100% DADOS SINTETICOS; nenhum dado de cliente real.'})
    print(f'[SINTETICO] {n_customers} clientes; {n_cancel} cancelamentos; {len(HEADERS)} fontes')
    return manifest

if __name__=='__main__':
    generate()
