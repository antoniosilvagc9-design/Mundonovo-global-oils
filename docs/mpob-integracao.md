# Integração MPOB — verificação de fontes (21/11/2026)

## Confirmado em fonte oficial
- Malaysian Palm Oil Board (MPOB), Economics and Industry Development Division: https://bepi.mpob.gov.my/
- Divulgação mensal de produção, estoques, exportações, importações e preço FFB; calendário geralmente no dia 10, aproximadamente 12h30 da Malásia.
- A página de estatísticas apresenta aviso de login/registro para acesso ao conteúdo. Não assumir API pública ou autorização de raspagem.
- Fonte: https://bepi.mpob.gov.my/index.php/about-us-11749/services

## Fonte alternativa oficial aberta (não equivalente)
- OpenDOSM, estatísticas de comércio total da Malásia: https://open.dosm.gov.my/data-catalogue/trade_headline
- CSV público: https://storage.dosm.gov.my/trade/trade_headline.csv
- Licença CC BY 4.0 conforme portal.
- IMPORTANTE: esse dataset é comércio total de mercadorias, NÃO exportações específicas de óleo de palma. Não usar seus valores como se fossem MPOB.

## Próximos passos
1. Verificar quais tabelas MPOB podem ser acessadas legitimamente sem login ou por permissão explícita.
2. Selecionar a fonte oficial e documentar formato, periodicidade e regras de uso.
3. Criar adaptador de ingestão que valide mês de referência, unidades (toneladas), números e revisões.
4. Publicar data/mpob-malaysia.json apenas após validação, com fonte e timestamp.
5. Mostrar estados de ausência de dados sem inventar números.

## Campos desejados
- reference_month (AAAA-MM)
- cpo_production_tonnes
- total_palm_oil_closing_stocks_tonnes
- palm_oil_exports_tonnes
- publication_date
- revision_status
- source_url
- fetched_at_utc

Não confundir estoque total de óleo de palma com estoque de óleo de palma bruto.
