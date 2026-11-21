#!/usr/bin/env python3
"""Histórico indicativo do futuro contínuo de soja ZS=F (Yahoo Finance)."""
import datetime as dt
import json
import math
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SYMBOL = "ZS=F"
now = dt.datetime.now(dt.timezone.utc)
today = now.date()
url = "https://query1.finance.yahoo.com/v8/finance/chart/" + quote(SYMBOL, safe="") + "?range=3mo&interval=1d"
req = Request(url, headers={"User-Agent": "Mozilla/5.0 TradingGlobal/2.5", "Accept": "application/json"})
with urlopen(req, timeout=35) as response:
    payload = json.load(response)
chart = payload["chart"]
if chart.get("error"):
    raise RuntimeError(str(chart["error"]))
result = chart["result"][0]
timestamps = result.get("timestamp", [])
quote_data = result["indicators"]["quote"][0]
closes = quote_data.get("close", [])
valid = {}
for ts, value in zip(timestamps, closes):
    if value is None:
        continue
    v = float(value)
    if not (math.isfinite(v) and 100 < v < 5000):
        continue
    day = dt.datetime.fromtimestamp(ts, dt.timezone.utc).date()
    if day > today:
        continue
    valid[day.isoformat()] = round(v, 4)
ordered = [{"date": day, "value": val} for day, val in sorted(valid.items())]
if len(ordered) < 3:
    raise RuntimeError("Menos de três pregões válidos")
target = today - dt.timedelta(days=30)
baseline_candidates = [p for p in ordered if target - dt.timedelta(days=10) <= dt.date.fromisoformat(p["date"]) <= target]
if not baseline_candidates:
    raise RuntimeError("Sem referência válida anterior a 30 dias")
base, latest, last_three = baseline_candidates[-1], ordered[-1], ordered[-3:]
delta = latest["value"] - base["value"]

# PTAX venda oficial do BCB: usar última observação de cada data de soja
# ou o pregão cambial anterior (até cinco dias corridos).
from urllib.error import HTTPError
from urllib.parse import urlencode
needed = [base] + last_three
first = min(dt.date.fromisoformat(p["date"]) for p in needed) - dt.timedelta(days=7)
last = max(dt.date.fromisoformat(p["date"]) for p in needed)
fmt = lambda d: d.strftime("%m-%d-%Y")
bcb_url = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)"
    "?@moeda='USD'&@dataInicial='" + fmt(first) + "'&@dataFinalCotacao='" + fmt(last) + "'&%24format=json&%24top=1000"
)
req_fx = Request(bcb_url, headers={"User-Agent": "Mozilla/5.0 TradingGlobal/2.5", "Accept": "application/json"})
with urlopen(req_fx, timeout=35) as response:
    fx_records = json.load(response)["value"]
daily_fx = {}
for record in fx_records:
    stamp = record.get("dataHoraCotacao", "")
    rate = record.get("cotacaoVenda")
    if stamp and isinstance(rate, (int, float)) and math.isfinite(rate) and rate > 0:
        date = stamp[:10]
        if date not in daily_fx or stamp > daily_fx[date]["timestamp"]:
            daily_fx[date] = {"timestamp": stamp, "rate": rate}
if not daily_fx:
    raise RuntimeError("PTAX indisponível; preservando dados anteriores")
def convert_point(p):
    day = dt.date.fromisoformat(p["date"])
    options = [(d, v) for d, v in daily_fx.items() if 0 <= (day - dt.date.fromisoformat(d)).days <= 5]
    if not options:
        raise RuntimeError("PTAX não encontrada para a data " + p["date"])
    fx_day, fx = max(options, key=lambda item: item[0])
    # 1 bushel de soja = 27,2155422 kg; 100 centavos = 1 USD
    value_brl = (p["value"] / 100) * (60 / 27.2155422) * fx["rate"]
    return {**p, "brl_per_60kg_bag": round(value_brl, 4), "ptax_date": fx_day, "ptax_brl_usd": fx["rate"]}
converted = [convert_point(p) for p in last_three]
converted_base = convert_point(base)
converted_latest = converted[-1]
average = round(sum(p["brl_per_60kg_bag"] for p in converted) / len(converted), 4)

out = {
    "symbol": SYMBOL,
    "source": "Yahoo Finance (provedor secundário, não CME oficial)",
    "source_url": "https://finance.yahoo.com/quote/ZS=F/history/",
    "market": "CBOT / CME Group",
    "instrument": "Futuro contínuo de soja (vencimento pode mudar por rolagem)",
    "price_type": "Fechamento diário indicativo; não settlement oficial",
    "unit": "centavos de USD/bushel",
    "updated_at_utc": now.isoformat(),
    "latest": latest,
    "baseline_30d": base,
    "target_30d": target.isoformat(),
    "change_30d_absolute": round(delta, 4),
    "change_30d_percent": round(delta / base["value"] * 100, 4),
    "last_three": last_three,
    "converted_last_three": converted,
    "converted_baseline_30d": converted_base,
    "converted_latest": converted_latest,
    "average_last_three_brl_per_60kg_bag": average,
    "conversion_method": "CBOT US¢/bushel / 100 × (60 / 27.2155422) × PTAX venda BRL/USD na data ou último pregão anterior (até 5 dias)",
}
path = ROOT / "data" / "soybean-history.json"
path.parent.mkdir(parents=True, exist_ok=True)
if path.exists():
    old = json.loads(path.read_text(encoding="utf-8"))
    if all(old.get(k) == out[k] for k in ("latest", "baseline_30d", "last_three", "converted_last_three", "converted_baseline_30d", "average_last_three_brl_per_60kg_bag")):
        print("Sem novos preços; preservando JSON")
        raise SystemExit(0)
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Soja:", latest, "referência:", base)
