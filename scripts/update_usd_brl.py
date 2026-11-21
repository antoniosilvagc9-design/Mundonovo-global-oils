#!/usr/bin/env python3
"""Busca a última cotação PTAX de venda USD/BRL publicada pelo Banco Central."""
import datetime as dt
import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request

today = dt.datetime.now(dt.timezone.utc).date()
start = today - dt.timedelta(days=14)
base = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
params = {
    "@dataInicial": f"'{start.strftime('%m-%d-%Y')}'",
    "@dataFinalCotacao": f"'{today.strftime('%m-%d-%Y')}'",
    "$format": "json",
}
url = base + "?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={"User-Agent": "MundoNovoGlobalOils/1.0"})
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
except urllib.error.HTTPError as exc:
    detail = exc.read().decode("utf-8", errors="replace")[:2000]
    raise RuntimeError(f"Banco Central retornou HTTP {exc.code}; URL: {url}; detalhes: {detail}") from exc
rows = payload.get("value", [])
if not rows:
    raise RuntimeError("BCB não retornou cotações; arquivo anterior será preservado")
latest = max(rows, key=lambda item: item["dataHoraCotacao"])
result = {
    "pair": "USD/BRL",
    "value": latest["cotacaoVenda"],
    "unit": "BRL por USD",
    "type": "PTAX venda (referência, não cotação comercial em tempo real)",
    "reference_datetime": latest["dataHoraCotacao"],
    "fetched_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "source": "Banco Central do Brasil",
    "source_url": "https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes",
}
dest = pathlib.Path("data/usd-brl.json")
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PTAX venda {result['value']} em {result['reference_datetime']}")
