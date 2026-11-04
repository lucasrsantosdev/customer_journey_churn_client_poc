# Governança, privacidade, segurança e ética de dados

## Status de proteção desta POC

A versão v0.1 só contém **dados fabricados**, identificadores simulados e transcrições artificiais. Não utiliza chamadas reais, CPF, MSISDN, nome civil, endereço pessoal nem identificação dos reclamantes de plataformas públicas. O uso da marca CLARO identifica o **tema do estudo**, não constitui endosso ou projeto corporativo oficial.

## Regras antes de integrar dados reais

1. Formalizar controlador/operador, finalidade específica e hipótese legal adequada ao tratamento.
2. Limitar dados aos campos necessários; evitar transcrições integrais sem finalidade e controle de acesso.
3. Usar HMAC-SHA256 com segredo gerenciado em cofre, rotação e versionamento de chaves, segregando a tabela de correspondência e chaves de identidade.
4. **Pseudonimização não é anonimização.** Uma chave estável que une interações pode permitir individualização; os controles e direitos da LGPD continuam aplicáveis.
5. Restringir acesso ao dado granular por perfil, auditar consultas e aplicar retenção/expurgo acordados.
6. Efetuar mascaramento e verificação de PII em transcrições de áudio e reclamações antes de qualquer treinamento de NLP/LLM.
7. Publicar somente métricas agregadas com limiares mínimos de grupos e tratamento de reidentificação quando necessário.
8. Não usar enriquecimento de ex-clientes por listas adquiridas, scraping de telefone/perfil ou consulta de operadora por número sem avaliação legal, autorizações, finalidade e condições contratuais válidas.
9. Portabilidade pode ter registro operacional legítimo e direito regulado, mas a POC **não** pressupõe acesso a base identificável de terceiros. Usar somente canal formal, dados autorizados ou declaração do titular.
10. Não confundir oferta promocional de mercado com confirmação de novo vínculo de cliente.
11. Separar ambientes e dados: `data/raw/synthetic/` versionável; `data/raw/real/` e `data/private/` sempre ignorados pelo Git.
12. Avaliar relatório de impacto (RIPD), direitos do titular e base legal com DPO/jurídico antes do uso corporativo.

## Informações não obtidas aqui

- Reclame Aqui: os exemplos são fictícios; nenhuma reclamação real foi coletada. Integração futura depende de fonte e permissão válidas, matching minimizado e governança.
- Operadora de destino: não há consulta real nem mailing real de ex-clientes em concorrentes.
- Ofertas de mercado: nomes das operadoras e preços no CSV são ilustrativos, não pesquisa de preços verificáveis.

## Referências para análise de governança (consultar versão vigente)

- Autoridade Nacional de Proteção de Dados (ANPD), **Estudo técnico sobre anonimização de dados na LGPD**: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos/estudo_tecnico_sobre_anonimizacao_de_dados_na_lgpd___analise_juridica.pdf/@@download/file
- Governo Digital, **Guia de boas práticas de LGPD**: https://www.gov.br/governodigitalseguro/pt-br/privacidade-e-seguranca/guias/guia_lgpd.pdf
- Anatel, **Portabilidade de telefonia móvel**: https://www.gov.br/anatel/pt-br/consumidor/conheca-seus-direitos-2/telefonia-movel/portabilidade
- Anatel, **Perguntas frequentes de numeração**: https://www.gov.br/anatel/pt-br/regulado/numeracao/perguntas-frequentes

> Esta documentação não substitui parecer jurídico nem autorização interna para processamento de dados pessoais. A avaliação deve considerar a finalidade concreta e a origem de cada dataset.
