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
