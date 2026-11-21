#!/usr/bin/env python3
"""Coleta spot Brent EIA/FRED DCOILBRENTEU. Falha sem substituir JSON válido."""
import csv
import datetime as dt
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SERIES = "DCOILBRENTEU"
CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=" + SERIES
API_URL = "https://api.stlouisfed.org/fred/series/observations"
now = dt.datetime.now(dt.timezone.utc)
today = now.date()
start = today - dt.timedelta(days=75)
rows = []
key = os.getenv("FRED_API_KEY", "").strip()
if key:
    from urllib.parse import urlencode
    url = API_URL + "?" + urlencode({"series_id": SERIES, "api_key": key, "file_type": "json", "observation_start": start.isoformat()})
    req = Request(url, headers={"User-Agent": "TradingGlobal/2.4", "Accept": "application/json"})
    with urlopen(req, timeout=40) as resp:
        payload = json.load(resp)
    rows = [{"date": x["date"], "value": x["value"]} for x in payload.get("observations", [])]
else:
    # CSV público do gráfico FRED: não é a API contratual; pode mudar sem aviso.
    req = Request(CSV_URL + "&cosd=" + start.isoformat(), headers={"User-Agent": "TradingGlobal/2.4", "Accept": "text/csv"})
    with urlopen(req, timeout=40) as resp:
        content = resp.read().decode("utf-8-sig")
    rows = [{"date": r.get("observation_date") or r.get("DATE"), "value": r.get(SERIES)} for r in csv.DictReader(io.StringIO(content))]

valid = {}
for row in rows:
    try:
        date = dt.date.fromisoformat(str(row["date"]))
        value = float(row["value"])
        if not (0 < value < 10000 and date <= today):
            continue
        valid[date.isoformat()] = round(value, 4)
    except (TypeError, ValueError, KeyError):
        continue
ordered = [{"date": d, "value": valid[d]} for d in sorted(valid)]
last_three = ordered[-3:]
if len(last_three) < 2:
    raise RuntimeError("Histórico Brent insuficiente; preservando arquivo anterior")
target = today - dt.timedelta(days=30)
candidates = [p for p in ordered if dt.date.fromisoformat(p["date"]) <= target and dt.date.fromisoformat(p["date"]) >= target - dt.timedelta(days=10)]
if not candidates:
    raise RuntimeError("Sem referência Brent de 30 dias; preservando arquivo anterior")
baseline = candidates[-1]
latest = ordered[-1]
delta = round(latest["value"] - baseline["value"], 4)
percent = round((latest["value"] / baseline["value"] - 1) * 100, 4)
output = {
    "series": SERIES,
    "source": "U.S. Energy Information Administration (EIA), via FRED",
    "source_url": "https://fred.stlouisfed.org/series/" + SERIES,
    "unit": "USD/barril",
    "price_type": "Spot Brent Europe (referência diária; não é futuro ICE)",
    "updated_at_utc": now.isoformat(),
    "latest": latest,
    "baseline_30d": baseline,
    "target_30d": target.isoformat(),
    "change_30d_absolute": delta,
    "change_30d_percent": percent,
    "last_three": last_three,
}
dest = ROOT / "data" / "brent-history.json"
dest.parent.mkdir(parents=True, exist_ok=True)
# Não gravar se não houve nova observação: evita commits a cada 3 horas.
if dest.exists():
    old = json.loads(dest.read_text(encoding="utf-8"))
    if old.get("latest") == latest and old.get("baseline_30d") == baseline and old.get("last_three") == last_three:
        print("Brent sem nova observação; JSON mantido")
        raise SystemExit(0)
dest.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Brent atualizado:", latest, "base 30d:", baseline)
