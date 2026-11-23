"""Dados totalmente fictícios para demonstração, não são cotações reais."""
from datetime import date

def get_demo_data():
    return {
        "empresa": "Mundo Novo",
        "periodo": str(date.today()),
        "modo": "DEMONSTRAÇÃO — DADOS FICTÍCIOS",
        "commodities": [
            {"nome": "Óleo de palma", "variacao_pct": 2.8, "indice": 102.8},
            {"nome": "Óleo de soja", "variacao_pct": -1.4, "indice": 98.6},
            {"nome": "Petróleo Brent", "variacao_pct": 1.1, "indice": 101.1},
        ],
        "usd_brl": 5.20,
        "contratos": 18,
        "margem_media_pct": 12.4,
        "estoque_ton": 1250,
    }
