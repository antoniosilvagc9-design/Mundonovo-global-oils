# Importação FCPO — Trading Global

**Situação:** a Bursa Malaysia retornou HTTP 403 no GitHub Actions. Não há coleta automática autorizada confirmada. Este fluxo importa arquivos CSV obtidos legitimamente pelo usuário.

## Como importar
1. Baixe o CSV `derivative_trading_statistic_YYYYMMDD.csv` na Bursa Malaysia.
2. Confirme que as condições de uso permitem armazenar/publicar os dados neste repositório. Caso contrário, mantenha o arquivo privado e use o script localmente.
3. Envie os arquivos permitidos para `data/fcpo-inbox/` usando **Add file → Upload files** no GitHub.
4. Abra **Actions → Importar FCPO de CSV autorizado → Run workflow**. O push do arquivo também inicia a validação.
5. O workflow gera `data/cpo-history.json` apenas se houver CSVs válidos. Não preenche datas faltantes.

Para três pregões, forneça três CSVs. Para referência de 30 dias, forneça também o CSV do pregão em/antes de 30 dias do último pregão importado.

**Contrato:** por enquanto o script seleciona o vencimento com maior volume em cada dia. Uma troca de vencimento pode criar variações não comparáveis; a série informa essa metodologia. Nenhuma cotação deve ser chamada de 'tempo real'.

**Privacidade/licença:** o fato de um CSV ser baixável no navegador não garante direito de redistribuição em repositório público. Não publique dados se a licença não permitir. O script também funciona offline:
```
python scripts/import_fcpo_csv.py /caminho/derivative_trading_statistic_*.csv --output /caminho/cpo-history.json
```
