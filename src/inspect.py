"""Audit one fabricated customer's event timeline and churn evidence.

Usage:
  python -m src.inspect --sample
  python -m src.inspect --sample --causa tecnico --produto FIXA
  python -m src.inspect --cliente_hash <synthetic_hash>
"""
import argparse
import sqlite3
from datetime import timedelta
from .config import WAREHOUSE,WINDOW_DAYS
from .utils import parse_datetime


def main():
    parser=argparse.ArgumentParser(description='Inspecionar jornada e evidencias de uma pessoa sintetica')
    parser.add_argument('--sample',action='store_true',help='Escolher um exemplo do warehouse sintético')
    parser.add_argument('--cliente_hash',help='Chave HMAC sintética (64 caracteres)')
    parser.add_argument('--causa',choices=['tecnico','financeiro','atendimento','preco_oferta','concorrencia','comercial','indeterminado'])
    parser.add_argument('--produto',choices=['MOVEL','FIXA'])
    parser.add_argument('--limit',type=int,default=50,help='Limite de eventos exibidos')
    args=parser.parse_args()
    if not WAREHOUSE.exists():
        parser.error('Execute primeiro: python -m src.main --all')
    if not args.sample and not args.cliente_hash:
        parser.error('Use --sample ou --cliente_hash <hash>')
    con=sqlite3.connect(WAREHOUSE)
    con.row_factory=sqlite3.Row
    try:
        clauses=[];pars=[]
        if args.cliente_hash:
            clauses.append('cliente_hash=?');pars.append(args.cliente_hash)
        if args.causa:
            clauses.append('causa_principal=?');pars.append(args.causa)
        if args.produto:
            clauses.append('produto=?');pars.append(args.produto)
        where=' AND '.join(clauses) if clauses else '1=1'
        row=con.execute('SELECT * FROM fct_cancelamentos_analitica WHERE '+where+' ORDER BY dt_cancelamento LIMIT 1',pars).fetchone()
        if row is None:
            print('Nenhum registro com os filtros informados.')
            return
        row=dict(row)
        end=parse_datetime(row['dt_cancelamento'])
        start=end-timedelta(days=WINDOW_DAYS)
        print('='*90)
        print('JORNADA FICTICIA | Cliente:',row['cliente_hash'])
        print('Contrato:',row['contrato_id'],'| Produto:',row['produto'])
        print('Cancelamento:',row['dt_cancelamento'],'| Motivo declarado:',row['motivo_declarado'])
        print('Causa principal:',row['causa_principal'],'| Confiança:',row['confianca'])
        print('Contribuintes:',row['motivos_contribuintes'] or 'nenhum')
        print(f'Janela individual: {start.isoformat()} a {end.isoformat()} (fim exclusivo)')
        print('-'*90)
        print('TIMELINE / FONTE / CANAL / CATEGORIA / STATUS')
        history=con.execute('''SELECT dt_evento,fonte,canal,categoria,status,id_origem
          FROM fct_jornada_eventos WHERE cliente_hash=? AND contrato_id=?
          AND dt_evento>=? AND dt_evento<? ORDER BY dt_evento LIMIT ?''',
          [row['cliente_hash'],row['contrato_id'],start.isoformat(),end.isoformat(),max(1,args.limit)]).fetchall()
        for e in history:
            print(f"{e['dt_evento'][:19]:19s} | {e['canal']:20s} | {e['categoria']:16s} | {e['status']:17s} | {e['fonte']}:{e['id_origem']}")
        print('-'*90)
        print('EVIDENCIAS / PONTOS:')
        evid=con.execute('''SELECT motivo,pontuacao,tipo_evidencia,fonte,id_origem
                FROM fct_evidencias_motivo WHERE cancelamento_id=?
                ORDER BY CAST(pontuacao AS INTEGER) DESC''',[row['cancelamento_id']]).fetchall()
        for e in evid[:30]:
            print(f"  +{e['pontuacao']} {e['motivo']:15s} | {e['tipo_evidencia']:28s} | {e['fonte']}:{e['id_origem']}")
        print('='*90)
        print('LEMBRETE: Demonstração sintética. Hipóteses inferidas, não causas confirmadas em clientes reais.')
    finally:
        con.close()

if __name__=='__main__':
    main()
