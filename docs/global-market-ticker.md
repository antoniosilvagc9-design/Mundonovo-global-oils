# Global Market Ticker — integração segura

A faixa horizontal é exibida em `index.html` e não apresenta preços fictícios.

## Fonte e permissões

O coletor opcional usa a API **documentada** Twelve Data (`/time_series`, intervalo `1day`). Isso **não** significa que os 12 índices estejam disponíveis no plano gratuito ou que exista direito de redistribuição pública. Confirme cobertura, códigos exatos, custo e licença com o fornecedor **antes** de habilitar a coleta no GitHub Pages.

A API Alpha Vantage oferece índices via `INDEX_DATA`, mas a documentação marca esse recurso como **premium**; não foi selecionada como fonte gratuita.

## Configuração no GitHub

1. Confirmar com Twelve Data a autorização para exibir os dados publicamente.
2. Em Settings > Secrets and variables > Actions, cadastrar secret `TWELVE_DATA_API_KEY`.
3. Cadastrar secret `MARKET_SYMBOLS_JSON` com JSON contendo **somente símbolos efetivamente testados e licenciados**, por exemplo `{"dow":"SIMBOLO_VALIDADO"}`. O texto é um placeholder, não um símbolo real.
4. Criar variable `MARKET_DATA_PUBLICATION_AUTHORIZED` = `yes` **somente após confirmar a licença**.
5. Executar workflow manualmente, verificar logs, JSON e publicação. O agendamento de 3 em 3 horas está preparado; sem a variável de autorização ele não consulta a API.

O coletor preserva valores validados em caso de falha e só publica novas observações. Não deduz abertura de mercado a partir do dia da semana; sem calendário oficial, exibe 'STATUS NÃO CONFIRMADO'. Valores são fechamentos diários, não cotações ao vivo.

## Validação

`python -m unittest discover -s tests -p 'test_market_ticker.py'`

Os testes verificam parser e falhas, mas não comprovam conectividade/licença. O feed real permanece pendente até configuração e execução autorizada.


## Auditoria de fontes gratuitas — 21/11/2026

**Twelve Data Basic:** plano gratuito com 8 créditos por minuto e 800 por dia, destinado a uso interno, testes e desenvolvimento. Os termos exigem autorização específica para redistribuição ou exibição externa; não autorizar publicação pública somente porque a API responde. Fontes:
- https://twelvedata.com/pricing
- https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage
- https://twelvedata.com/terms

**Stooq:** há CSVs de fechamento de índices como S&P 500, Nikkei e DAX, porém não foi comprovada licença de redistribuição no dashboard público, nem robustez de coleta não assistida. Não ativar como substituto automático sem permissão explícita.

**Outros candidatos:** B3, CME, Bursa Malaysia, NSE, IDX, SSE, JPX, HKEX, Deutsche Börse, Nasdaq Data Link e FMP exigem avaliação individual de instrumento, API e direitos de exibição. Nenhum foi validado neste ciclo para todos os 12 mercados.

### Matriz de cobertura (status comprovado)

| ID | Instrumento | Coleta autorizada e testada | Último preço publicado |
|---|---|---|---|
| dow | Dow Jones Industrial Average | Pendente | Indisponível |
| sp500 | S&P 500 | Pendente | Indisponível |
| nasdaq | Nasdaq Composite | Pendente | Indisponível |
| ibov | Ibovespa | Pendente | Indisponível |
| cme | E-mini S&P 500 Futures | Pendente | Indisponível |
| klci | FTSE Bursa Malaysia KLCI | Pendente | Indisponível |
| nifty | Nifty 50 | Pendente | Indisponível |
| idx | IDX Composite | Pendente | Indisponível |
| shcomp | Shanghai Composite | Pendente | Indisponível |
| nikkei | Nikkei 225 | Pendente | Indisponível |
| hsi | Hang Seng | Pendente | Indisponível |
| dax | DAX | Pendente | Indisponível |

O ticker já mostra os 12 nomes e a animação, mas não confunde a interface pronta com uma alimentação de preços funcionando. O arquivo `data/global-market-ticker.json` continua vazio intencionalmente. A automação permanece protegida por `MARKET_DATA_PUBLICATION_AUTHORIZED`.

**Próxima etapa:** obter autorização escrita de exibição pública de dados de fechamento, ou integrar um widget incorporável que tenha termos explícitos de exibição pública e cubra os instrumentos. Um widget não substitui uma API para o JSON e precisa ser identificado como tal.
