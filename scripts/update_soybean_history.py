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
}
path = ROOT / "data" / "soybean-history.json"
path.parent.mkdir(parents=True, exist_ok=True)
if path.exists():
    old = json.loads(path.read_text(encoding="utf-8"))
    if all(old.get(k) == out[k] for k in ("latest", "baseline_30d", "last_three")):
        print("Sem novos preços; preservando JSON")
        raise SystemExit(0)
path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Soja:", latest, "referência:", base)
