"""Small no-dependency static HTML executive dashboard for sample outputs."""
import html
from datetime import datetime
from .config import REPORTS
from .utils import fmt_ratio


def _escape(value):
    return html.escape(str(value))


def build(poc01,poc02):
    k1=poc01['kpis']; k2=poc02['kpis']; motives=poc01['reasons']
    htmlrows=''
    for row in sorted(motives,key=lambda x:(x['produto'],-int(x['cancelamentos']))):
        percent=float(row['percentual_cancelamentos_produto'])
        htmlrows+=f'''<tr><td><span class="chip">{_escape(row['produto'])}</span></td>
        <td>{_escape(row['causa_principal'])}</td><td class="n">{_escape(row['cancelamentos'])}</td>
        <td><div class="barwrap"><div class="bar" style="width:{percent}%"></div></div></td><td class="n">{percent:.1f}%</td></tr>'''
    trans=''.join(f"<tr><td>{_escape(r['produto'])}</td><td>{_escape(r['canal_origem'])}</td><td>{_escape(r['canal_destino'])}</td><td class='n'>{_escape(r['quantidade_transicoes'])}</td></tr>"
                  for r in sorted(poc02['transitions'],key=lambda x:-int(x['quantidade_transicoes']))[:14])
    cards=[('Cancelamentos da coorte', k1['cancelamentos'],'Outubro / 2026'),
           ('Clientes sintéticos',k1['clientes_sinteticos'],'Inclui grupo ativo'),
           ('Ligações classificadas',k1['ligacoes_analisadas'],'URA inbound e outbound'),
           ('Sem causa suficiente',f"{k1['percentual_indeterminado']:.1f}%",'Não imputar à concorrência'),
           ('Visitas às lojas',k2['visitas_loja'],'POC 02'),
           ('Clientes pré-loja com URA',f"{k2['percentual_ura_pre_loja']:.1f}%",'Base: clientes com loja')]
    cards_html=''.join(f'<article class="kpi"><div class="num">{_escape(n)}</div><strong>{_escape(label)}</strong><small>{_escape(sub)}</small></article>' for label,n,sub in cards)
    content=f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CLARO | Jornada & Churn — Demonstracao</title><style>
:root{{--navy:#092244;--blue:#1169d6;--cyan:#07a9df;--bg:#f3f6fb;--white:#fff;--mute:#64748b;--border:#e3eaf3}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);font:15px system-ui,-apple-system,Segoe UI,sans-serif;color:#172b48}}
header{{background:linear-gradient(130deg,#092244 0%,#0f4c97 68%,#087dc5 100%);color:white;padding:45px 7% 48px}}
header h1{{margin:0 0 7px;font-size:clamp(26px,4vw,39px)}}header p{{max-width:800px;line-height:1.6;opacity:.88}}
.alert{{display:inline-block;background:#fff2c4;color:#624c00;padding:8px 13px;border-radius:5px;font-size:12px;font-weight:700;letter-spacing:.04em}}
main{{max-width:1250px;margin:-24px auto 60px;padding:0 24px}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:24px}}
.kpi{{background:white;border:1px solid var(--border);border-radius:12px;padding:24px 18px;box-shadow:0 6px 20px #152d4710}}
.num{{font-weight:750;font-size:29px;color:var(--navy);margin-bottom:8px}}
.kpi strong{{display:block;font-size:13px}}.kpi small{{display:block;color:var(--mute);margin-top:7px}}
.section{{background:white;border:1px solid var(--border);border-radius:12px;padding:24px 28px;margin:18px 0;overflow:auto}}
h2{{font-size:20px;margin:0 0 8px}}p.lead{{margin:0 0 18px;color:var(--mute);font-size:13px;line-height:1.5}}
table{{width:100%;border-collapse:collapse;min-width:600px;font-size:13px}}th,td{{text-align:left;padding:12px 10px;border-bottom:1px solid #edf0f5}}th{{color:#53647b;font-weight:650;background:#f8fafd}}
.n{{text-align:right;font-variant-numeric:tabular-nums}}.barwrap{{height:9px;background:#e8eff9;border-radius:9px;min-width:100px;overflow:hidden}}
.bar{{height:100%;background:linear-gradient(90deg,var(--blue),var(--cyan));border-radius:9px}}.chip{{display:inline-block;padding:4px 9px;border-radius:5px;background:#e9f3ff;color:#07548f;font-size:11px;font-weight:750}}
footer{{color:var(--mute);font-size:12px;line-height:1.7;padding:0 26px}}.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:16px}}
.note{{background:#f5f9ff;border-left:3px solid var(--blue);padding:15px 19px;font-size:13px;line-height:1.7;border-radius:3px}}
</style></head><body><header><div class="alert">100% DADOS SINTÉTICOS — NÃO SÃO INDICADORES REAIS DA CLARO</div>
<h1>Customer Journey & Churn Intelligence</h1><p>Prova de conceito v0.1 · Coorte fechada de outubro/2026 · Móvel e Fixa · Rastreabilidade de 180 dias</p></header>
<main><section class="cards">{cards_html}</section>
<section class="section"><h2>POC 01 · Causas principais inferidas por produto</h2><p class="lead">Uma causa principal por cancelamento; percentuais calculados dentro de cada produto. Classificação por regras explicáveis e evidências rastreáveis, ainda não homologada.</p>
<table><thead><tr><th>Produto</th><th>Hipótese de causa principal</th><th class="n">Clientes</th><th>Distribuição</th><th class="n">Percentual</th></tr></thead><tbody>{htmlrows}</tbody></table></section>
<section class="section"><h2>POC 02 · Transições de canais mais frequentes</h2><p class="lead">Transições adjacentes na jornada de 180 dias; representam eventos, não clientes únicos.</p>
<table><thead><tr><th>Produto</th><th>Origem</th><th>Próximo canal</th><th class="n">Transições</th></tr></thead><tbody>{trans}</tbody></table></section>
<div class="two"><div class="note"><strong>Como ler a análise</strong><br>Motivo declarado ≠ causa principal inferida. Uma pessoa pode ter múltiplas evidências. As hipóteses requerem validação manual e dados reais governados.</div>
<div class="note"><strong>Concorrência e LGPD</strong><br>Oferta regional é apenas variável contextual. Só há identificação de destino quando existe registro autorizado de portabilidade ou declaração do próprio cliente.</div></div>
</main><footer>Estudo demonstrativo, sem clientes reais. Consulte README.md, docs/hipoteses_e_metricas.md e relatórios CSV para detalhes.</footer></body></html>'''
    (REPORTS/'dashboard.html').write_text(content,encoding='utf-8')
    print('[DASHBOARD] reports/dashboard.html gerado (abrir diretamente no navegador)')
