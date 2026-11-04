# Contribuindo

Este repositório é uma prova de conceito técnica e demonstrativa. Não publique bases reais de clientes, transcrições, tokens, segredos, identidades, planilhas de contatos, screenshots de sistemas internos ou credenciais.

1. Abra uma issue com a fonte, o grão e a hipótese que pretende investigar.
2. Documente qualquer alteração em chaves, campos, taxonomia ou cálculo no `docs/dicionario_dados.md` e `docs/hipoteses_e_metricas.md`.
3. Adicione teste de integração e regra de qualidade.
4. Execute `python -m src.main --all` e `python -m unittest discover -s tests -v`.
5. Verifique se o Git não inclui dados reais, segredos, identificação civil ou evidência pessoal.
6. Faça pull request pequeno, rastreável e com explicação do impacto nas POCs 01 e 02.

**Convenção:** `snake_case` sem acentos, espaços ou variáveis com nomes ambíguos. Não renomear contratos Gold sem migração dos consumidores.
