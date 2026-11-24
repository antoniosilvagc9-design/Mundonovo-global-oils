# Auditoria de mercado — 24/11/2026

## Estado verificado
- index.html: ticker com nove links oficiais, leitura de data/global-market-ticker.json a cada 300 s.
- JSON de cotações vazio.
- scripts/collect_eodhd_markets.py: sete índices EODHD e ESUSD FMP (E-mini S&P 500, não soja). Delay intradiário não verificado; fallback diário EODHD.
- Workflow collect-eodhd-markets.yml: dias úteis 21:15 UTC, execução agendada condicionada a variáveis de autorização; chaves em Secrets. Não foi consultado conteúdo dos Secrets.
- Risco: registros antigos podem permanecer quando ambas as autorizações são desligadas; fallback diário não verifica idade. Não habilitar publicação antes de corrigir e obter licença.
- Testes históricos relatados: oito mercados consultados; Twelve Data, Finnhub e Alpha Vantage sem cobertura adequada dos índices. Não reexecutados nesta auditoria.

## Licenciamento
EODHD pessoal não permite uso empresarial ou exposição pública: https://eodhd.com/help/personal-use
FMP pessoal não permite uso empresarial ou publicação: https://site.financialmodelingprep.com/terms-of-service
Widgets gratuitos com marca: https://www.tradingview.com/widget/
Cobertura específica: https://www.tradingview.com/widget-docs/markets/
FAQ: https://www.tradingview.com/widget-docs/faq/data/
B3: https://www.tradingview.com/blog/pb/b3-data-available-in-tradingview-widgets-41743/

## Matriz de testes a executar visualmente
| Mercado | Símbolo candidato (não testado nesta auditoria) | Cobertura documental |
|---|---|---|
| Bursa | MYX:FBMKLCI | Não confirmada |
| IDX | IDX:COMPOSITE | Fechamento diário |
| CBOT | CBOT:ZS1! | Não confirmada |
| EUA | SP:SPX | Índice não confirmado |
| B3 | BMFBOVESPA:IBOV | 15 min |
| NSE | NSE:NIFTY | Não confirmada |
| Japão | TVC:NI225 | Não confirmada |
| Shanghai | SSE:000001 | Fechamento diário |
| Euronext | EURONEXT:N100 | Não confirmada |

Não confundir cobertura da plataforma TradingView com cobertura do widget. Não extrair valores, remover atribuição ou alimentar a calculadora. Testar cada símbolo no configurador oficial, confirmar valor, indicador, atraso e ausência de mensagem de indisponibilidade; depois incorporar apenas os aprovados. Frequência exata de atualização do widget não verificada. Nenhuma cotação ou licença nova foi validada ao vivo. Não houve alteração na produção.
