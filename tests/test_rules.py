import unittest
from datetime import datetime,timedelta
from src.config import WINDOW_DAYS,CALENDAR_START,CALENDAR_END
from src.poc01_cancelamento import _classify_call
from src.utils import customer_key
from src.transform import _collect_causes

class LogicTests(unittest.TestCase):
    def test_calendar_window_is_183_days(self):
        self.assertEqual((CALENDAR_END-CALENDAR_START).days+1,183)
        self.assertEqual(WINDOW_DAYS,180)

    def test_hmac_deterministic_and_not_plain_id(self):
        a=customer_key('SIMULADO_1')
        self.assertEqual(a,customer_key('SIMULADO_1'))
        self.assertNotEqual(a,customer_key('SIMULADO_2'))
        self.assertNotIn('SIMULADO_1',a)

    def test_call_classification(self):
        label,_=_classify_call('Cliente relata sem sinal e falha tecnica.')
        self.assertEqual(label,'tecnico')
        label,_=_classify_call('Solicitou preco e desconto por oferta.')
        self.assertEqual(label,'preco_oferta')

    def test_undetermined_without_evidence(self):
        c={'cancelamento_id':'CAN-TEST','cliente_hash':customer_key('TEST'),
           'contrato_id':'CTR-TEST','dt_cancelamento':'2026-10-15T12:00:00','motivo_declarado':'sem_informacao'}
        out,evid,bridge=_collect_causes(c,[],{'pesquisas_saida':[]},'MOVEL')
        self.assertEqual(out['causa_principal'],'indeterminado')
        self.assertEqual(out['confianca'],'SEM_EVIDENCIA')

    def test_confirmed_competitor_only_with_evidence(self):
        c={'cancelamento_id':'CAN-TEST','cliente_hash':customer_key('TEST'),
           'contrato_id':'CTR-TEST','dt_cancelamento':'2026-10-15T12:00:00','motivo_declarado':'sem_informacao'}
        p={'evento_id':'portabilidades:PORT-1','cliente_hash':c['cliente_hash'],
           'contrato_id':c['contrato_id'],'dt_evento':'2026-10-14T10:00:00','canal':'PORTABILIDADE',
           'tipo_evento':'PORTABILIDADE','categoria':'concorrencia','status':'CONFIRMADA','resolvido':'1',
           'texto':'','fonte':'portabilidades','id_origem':'PORT-1','competidor':'VIVO','produto':'MOVEL','mes_ref':'202610'}
        out,evid,_=_collect_causes(c,[p],{'pesquisas_saida':[]},'MOVEL')
        self.assertEqual(out['causa_principal'],'concorrencia')
        self.assertEqual(out['confianca'],'ALTA_CONFIRMADA')

    def test_out_of_window_evidence_excluded(self):
        c={'cancelamento_id':'CAN-TEST','cliente_hash':customer_key('TEST'),
           'contrato_id':'CTR-TEST','dt_cancelamento':'2026-10-15T12:00:00','motivo_declarado':'sem_informacao'}
        p={'evento_id':'portabilidades:PORT-1','cliente_hash':c['cliente_hash'],
           'contrato_id':c['contrato_id'],'dt_evento':'2026-04-01T09:00:00','canal':'PORTABILIDADE',
           'tipo_evento':'PORTABILIDADE','categoria':'concorrencia','status':'CONFIRMADA','resolvido':'1',
           'texto':'','fonte':'portabilidades','id_origem':'PORT-1','competidor':'VIVO','produto':'MOVEL','mes_ref':'202604'}
        out,_,_=_collect_causes(c,[p],{'pesquisas_saida':[]},'MOVEL')
        self.assertEqual(out['causa_principal'],'indeterminado')

if __name__=='__main__':unittest.main()
