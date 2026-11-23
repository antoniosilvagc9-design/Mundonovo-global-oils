# Gerador executivo — protótipo Mundo Novo

API local FastAPI com dados **100% fictícios**, sem acesso ao ERP ou a APIs externas.

## Executar
```bash
cd executive-report
python -m venv .venv
# Ative o ambiente virtual conforme seu sistema
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Teste `http://127.0.0.1:8000/docs`. Gere o PowerPoint com POST `/api/executive-report/generate`.

## Integração com o dashboard
O dashboard estático hospedado no GitHub Pages **não executa Python**. O botão do frontend deverá chamar esta API quando ela estiver hospedada em serviço privado, com autenticação, HTTPS, CORS restrito e controles de acesso. Não exponha endpoint de geração corporativa sem autenticação.

## Próximas etapas
- Testes automatizados, validação e limites de requisição.
- Hospedagem e autenticação corporativa.
- Conector de mercado autorizado.
- Integração de leitura do ERP somente após aprovação da TI.
- Revisão humana de insights antes de envio à diretoria.
