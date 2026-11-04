# Hipóteses, métricas e metodologia

## 1. Perguntas norteadoras

**POC 01 — Por que o cliente cancelou?**

- A falha técnica recorrente pode preceder cancelamentos de banda larga?
- O motivo informado na URA/CRM representa o histórico de incidentes?
- Clientes com alto número de transferências tendem a ter mais interações antes do cancelamento?
- Problemas de cobrança, renegociação e inadimplência estão associados ao desfecho?
- Há indícios de pressão competitiva por região/produto/mês?
- Quais motivos não podem ser classificados com as fontes atuais?
- Quais oportunidades de prevenção aparecem em janelas de 30, 60, 90 e 180 dias?

**POC 02 — O cliente precisou ir à loja depois de tentar outro canal?**

- Quantos clientes foram atendidos pela URA nos 30 dias anteriores à loja?
- Quanto do fluxo presencial é precedido por tentativa no app ou site?
- Quantas jornadas mostram suporte e depois loja, sugerindo recontato?
- Quantos canais o cliente usou antes da visita?
- Qual é a última origem identificada antes da loja e quanto tempo se passou?
- O padrão difere entre cancelados e ativos, descontando diferenças de produto, perfil e exposição?

## 2. Taxonomia provisória

| Motivo | Exemplos | Evidências preferidas | Risco de interpretação |
|---|---|---|---|
| Técnico | Instabilidade, quedas, visita sem solução, ticket aberto | Ordens de serviço, histórico de rede, tickets | Correlação não prova causa exclusiva |
| Financeiro | Fatura vencida, renegociação, acordo quebrado | ERP de cobrança/faturamento e eventos de negociação | Inadimplência pode ser consequência, não causa |
| Atendimento | Contatos não resolvidos, transferências e repetição | Protocolos, gravações e canais digitais | Baixa qualidade de texto pode gerar falso positivo |
| Preço/oferta | Queixa de preço, desconto e adequação | Voz, CRM, pesquisa de saída | Oferta externa não demonstra adesão |
| Concorrência | Portabilidade ou novo operador declarado | Registro autorizado / declaração explícita | Somente uma **evidência direta** individual habilita a categoria |
| Comercial | Venda divergente, plano contratado errado | Pedido, contrato, reclamação | Necessário separar vício de venda de cobrança |
| Indeterminado | Nenhuma evidência suficiente | Ausência de informação | Deve ficar explícito, nunca preenchido arbitrariamente |

Classificação atual é **heurística transparente por pontos**, não modelo de inteligência artificial treinado. `src/transform.py` registra cada ponto por evidência; `src/poc01_cancelamento.py` etiqueta todas as ligações sintéticas por expressões pré-definidas. Para uso real, será necessário conjunto de validação rotulado manualmente, métricas de precisão e revisão por especialistas do negócio.

## 3. Regras de causa e evidência

1. Restringir eventos ao cliente/contrato e aos 180 dias exatos anteriores ao cancelamento.
2. Preservar o `motivo_declarado` sem tratá-lo como verdade do modelo.
3. Classificar falhas com base em eventos; por exemplo, ticket técnico em aberto = 3 pontos, visita técnica sem solução = 2.
4. Inadimplência por fatura = 2 e acordo quebrado = 3.
5. Três ou mais ligações sem resolução = 3 pontos de atendimento; outros relatos podem contribuir.
6. Concorrência: confirmação de portabilidade autorizada = 8, autodeclaração com prestadora = 5. Oferta externa **nunca** entra nesse escore.
7. Somar pontos, escolher uma causa principal quando houver evidência suficiente, registrar demais motivos sustentados e nível de confiança.
8. Se não houver evidência, manter `indeterminado` e criar oportunidade de melhorar captura de informação.
9. Conservar evidências, origens, timestamps e versão da regra para auditoria.

**Importante:** pesquisa de saída é retrospectiva e pode ocorrer no momento do cancelamento, portanto não é contada como contato pré-cancelamento, embora possa fundamentar a causa autodeclarada. Portabilidade após a hora do cancelamento não é tratada como contato anterior nesta versão; seu relacionamento posterior pode ser estudado separadamente com corte e governança explícitos.

## 4. Dicionário de indicadores e denominadores

| Indicador | Fórmula | Grão / denominador |
|---|---|---|
| Total cancelados | `COUNT(DISTINCT cancelamento_id)` | Coorte outubro, por produto |
| % causa principal | Cancelamentos com causa X ÷ cancelamentos do produto | Cancelamentos (motivos exclusivos) |
| % motivos contribuintes | Clientes com evidência X ÷ clientes cancelados do produto | Clientes; percentuais **não** somam 100% |
| Contatos antes do cancelamento | Contagem de interações nos 180 dias anteriores | Cliente/contrato; filtrar fontes de evento |
| Canais distintos | `COUNT(DISTINCT canal)` na janela | Cliente/contrato |
| Ligações por tema | Ligações classificadas tema X ÷ total de ligações analisadas | Eventos de voz, não clientes |
| Resolução em 30d | Tickets fechados no máximo 30 dias após abertura e até o corte ÷ tickets elegíveis | Ticket; corte na data de cancelamento ou fim de outubro |
| % clientes que ligaram antes da loja | Clientes com URA na janela pré-loja ÷ clientes com visita à loja | Cliente/contrato com loja, última visita para agregação |
| % multicanal antes da loja | Clientes que usaram 2+ canais antes da visita ÷ clientes com visita | Cliente/contrato com loja |
| Tempo até a loja | `dt_loja - dt_ultimo_evento_anterior` | Por visita, em horas |
| Divergência declarado vs inferido | Contagem por par de categorias | Cancelamento |
| Exposição à oferta | Preço da oferta regional concorrente no mês vs mensalidade | Contexto região/mês/produto, **não** migração individual |
| Motivo indeterminado | Clientes sem evidência suficiente ÷ cancelados | Coorte, por produto |

### Cortes recomendados após dados reais

- Produto Móvel/Fixa; plano e faixa de mensalidade; região e UF; canal de entrada; canais percorridos; lojas próprias/PDV; série mensal abr–set; faixas 0–7, 8–30, 31–60, 61–90, 91–180 dias; suporte resolvido/não resolvido; frequência de recontato; reclamação externa; atraso financeiro; tempo de contrato.
- Construir também grupo **ativo comparável**. A primeira POC o inclui como dado sintético, mas o relatório de causa é corretamente restrito à coorte cancelada. Para medir risco/efeito causal em dados reais: amostragem e controle de exposição, segmentação, sazonalidade, dependência entre contratos, probabilidade de atendimento e testes prospectivos.

## 5. Hipóteses de trabalho e testes

| ID | Hipótese a validar | Sinal observável | Fonte prioritária | Próximo teste |
|---|---|---|---|---|
| H01 | Reincidência de falha técnica precede cancelamento de Fixa | Tickets abertos / 2+ visitas | Suporte e técnico | Sequência temporal e casos rotulados |
| H02 | URA não resolve e cliente procura loja | URA ≤30d antes loja | URA e loja | Taxa por clientes únicos e motivos |
| H03 | Digital falha antes do presencial | App/site sem solução → loja | Digital e loja | Sequências e taxa de autosserviço |
| H04 | Fatura/renegociação explicam parte da evasão | Inadimplência + acordo quebrado | Cobrança | Separar voluntário de não pagamento |
| H05 | Transferências aumentam esforço do cliente | 3+ ligações não resolvidas | Telefonia | Analisar FCR, TMA e transferências reais |
| H06 | Preço de concorrência cria pressão | Delta mensalidade vs oferta regional | Ofertas públicas | Comparação agregada, sem rotular cliente |
| H07 | Migração real pode ser identificada em parcela dos casos | Evento autorizado de portabilidade | Registros autorizados | Medir cobertura, consentimento e falso positivo |
| H08 | Motivo declarado diverge do histórico | Declaração ≠ classificação auditável | Cancelamento + eventos | Revisão humana estratificada |
| H09 | Atraso na resolução é associado à saída | Ticket não resolvido até corte | Suporte | Coortes ativo vs cancelado e ajustes de viés |
| H10 | Loja recebe cliente sem histórico compartilhado | URA/APP/SITE antes da loja | CRM + canais | Verificar disponibilidade de protocolo |
| H11 | Reclamações públicas evidenciam falhas sistêmicas | Reclamações abertas por motivo | Reclamações | Matching somente licenciado e governado |
| H12 | Grande fração não tem causa observável | Indeterminado | Todas | Mapa de lacunas da captura de dados |

## 6. O que a POC não demonstra

- Não estima churn real da CLARO, eficácia comprovada de retenção, causa causal, precisão de IA nem cobertura real de portabilidade.
- Não realiza scrape do Reclame Aqui, não lê gravações reais, não identifica operadores atuais por número telefônico e não captura contatos pessoais.
- Resultados numéricos do relatório são inventados de forma controlada e devem ser substituídos por dados autorizados antes de qualquer recomendação operacional real.
