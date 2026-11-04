# Contrato de fontes reais — preenchimento incremental

A POC começa com **cabeçalhos fictícios**. À medida que o time disponibilizar o dicionário de uma fonte, substituir o adaptador de entrada correspondente, sem quebrar o contrato Silver e as medidas existentes.

## 1. Checklist de entrada por fonte

| Fonte fictícia | Sistema real (a mapear) | Grão de origem | Data/hora essencial | Chave solicitada | Cuidados |
|---|---|---|---|---|---|
| `clientes.csv` | CRM/cadastro | Cliente | Ativação / histórico | Identificador de cliente | Não exportar CPF, telefone ou nome desnecessariamente |
| `contratos.csv` | CRM/produtos | Contrato/serviço | Vigência, mudança plano | Cliente + contrato + produto | Um cliente pode ter vários serviços |
| `cancelamentos.csv` | CRM/churn | Solicitação/evento de saída | Solicitação, execução, efetivação | Cliente + contrato + cancelamento | Definir quando churn é contabilizado |
| `ura_ligacoes.csv` | Telefonia/URA/Contact Center | Chamada | Início, fim | Cliente + contrato + chamada + protocolo | Inbound/outbound, transferências, gravação/transcrição governada |
| `loja_atendimentos.csv` | POS/CRM loja | Atendimento/visita | Check-in, fechamento | Cliente + contrato + atendimento | Própria vs PDV, sem confundir visita e compra |
| `digital_interacoes.csv` | App/site/web analytics | Sessão, evento ou solicitação | Timestamp de cada ação | Cliente + contrato + sessão + evento | Evitar duplicar pageviews como atendimentos |
| `suporte_tickets.csv` | Field service/service desk | Ticket | Abertura, encerramento, reabertura | Cliente + contrato + ticket | Status histórico e motivo do encerramento |
| `visitas_tecnicas.csv` | Ordem de serviço Fixa | Visita | Agendamento, chegada, conclusão | Cliente + contrato + OS | Somente contratos com serviço residencial aplicável |
| `faturas.csv` | Billing/cobrança | Fatura | Emissão, vencimento, pagamento | Cliente + contrato + fatura | Estornos, baixas, inadimplência, suspensão |
| `acordos_financeiros.csv` | Recuperação de crédito | Acordo | Criação, quebra, quitação | Cliente + contrato + acordo | Parcelas e status ao longo do tempo |
| `reclamacoes.csv` | Ouvidoria/parceiro | Reclamação | Abertura, resposta, solução | Cliente + protocolo permitido | Integração pública somente com finalidade/bases e direitos válidos |
| `portabilidades.csv` | Evento regulado/operacional autorizado | Evento de portabilidade | Solicitação/efetivação | Cliente + linha/serviço autorizado | Não afirmar migração sem dados válidos e autorização |
| `pesquisas_saida.csv` | Pesquisa/NPS/CRM | Resposta | Instante da resposta | Cliente + cancelamento + pesquisa | Consentimento/cobertura/viés de resposta |
| `ofertas_mercado.csv` | Preço público/estudo competitivo | Oferta/região/mês/produto | Vigência | `mes_ref + regiao + produto` | Nunca unir indivíduo por telefone ou hash inventado |

## 2. Contrato mínimo obrigatório para fontes de cliente

```text
cliente_hash      STRING(64)   HMAC-SHA256 gerado em ambiente controlado
contrato_id       STRING       Identificador do contrato/servico
id_origem         STRING       Chave original do evento, sem PII
fonte             STRING       Identificador estável do sistema
momento_evento    TIMESTAMP    UTC recomendado + fuso informado
```

Campos adicionais de rastreabilidade a criar na integração real: `ingested_at`, `source_file`, `run_id`, `row_hash`, `source_timezone`, `event_status`, `valid_from`, `valid_to`, `last_updated_at`. O hash **não** substitui controles de acesso, base legal e segregação de chaves.

## 3. Perguntas que precisamos responder ao receber cada cabeçalho

1. Qual a granularidade da linha: evento, sessão, ticket, histórico de status, fatura ou solicitação?
2. O identificador representa cliente, contrato, linha, instalação ou conta financeira?
3. O campo de tempo é data de criação, atendimento, efetivação, baixa ou atualização?
4. Existem eventos duplicados, reprocessamentos, reaberturas ou backfill?
5. O status é atual ou temos histórico (SCD/timestamp de alteração)?
6. Como a fonte distingue Móvel de Fixa? Quais canais efetivamente existem?
7. Qual é a cobertura de abril a outubro de 2026 e quais atrasos de carga são esperados?
8. O motivo de saída é obrigatório, editável, validado ou classificação livre?
9. O canal de loja consegue consultar protocolos e tickets anteriores?
10. Qual autorização, retenção, perfis de acesso e amostragem foram aprovados para esse dado?

## 4. Procedimento de evolução sem perder a primeira versão

- **Etapa A:** salvar o cabeçalho real no documento de mapeamento (não colar valores pessoais).
- **Etapa B:** criar adaptador em `src/adapters/<fonte>.py` mapeando nomes reais ao contrato Silver.
- **Etapa C:** registrar tabela de equivalência de temas/status/produto e fonte do campo.
- **Etapa D:** rodar testes de esquema, nulos, unicidade, join e data/timezone.
- **Etapa E:** reconciliar quantidade por mês/canal/produto com sistema de origem.
- **Etapa F:** validar amostras de chamadas/tickets/cancelamentos com analistas do negócio.
- **Etapa G:** substituir sintéticos por conexão autorizada e dataset segregado, sem subir dados reais no Git.

**Regra de ouro:** não trocar o nome de colunas Gold em uso sem atualizar todos os consumidores (consultas, dashboards, testes, relatórios, documentação). Convenção de projeto: nomes de tabelas/colunas/medidas sem espaços, sem acentos e com `_`.
