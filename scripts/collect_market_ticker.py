#!/usr/bin/env python3
"""Import licensed Twelve Data daily index closes; never fabricate quotes.

Configure MARKET_SYMBOLS_JSON as a mapping of ticker IDs to provider-verified
symbols, and TWELVE_DATA_API_KEY in GitHub Actions secrets. Verify redistribution
rights before enabling this workflow on a public Pages site.
"""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request

OUTPUT = pathlib.Path("data/global-market-ticker.json")
IDS = {"dow","sp500","nasdaq","ibov","cme","klci","nifty","idx","shcomp","nikkei","hsi","dax"}
URL = "https://api.twelvedata.com/time_series"

def parse_daily(payload, market_id, symbol):
    if not isinstance(payload, dict) or payload.get("status") == "error":
        raise ValueError("Provider returned error or invalid JSON")
    rows = payload.get("values")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("Need two verified trading sessions")
    valid = []
    for row in rows:
        try:
            day = dt.date.fromisoformat(row["datetime"][:10])
            price = float(row["close"])
            if not (0 < price < 1e12):
                continue
            valid.append((day, price))
        except (ValueError, TypeError, KeyError):
            continue
    valid.sort(reverse=True)
    unique = []
    for day, price in valid:
        if not any(d == day for d, _ in unique):
            unique.append((day, price))
    if len(unique) < 2:
        raise ValueError("Insufficient valid closing observations")
    latest, previous = unique[:2]
    if latest[0] > dt.datetime.now(dt.timezone.utc).date():
        raise ValueError("Future dated observation")
    meta = payload.get("meta") or {}
    currency = meta.get("currency")
    if not isinstance(currency, str) or not currency.strip():
        raise ValueError("Provider currency missing")
    # Market status is not inferred from weekdays: exchange calendars vary.
    return {"id": market_id, "price": latest[1], "previous_close": previous[1],
            "currency": currency, "as_of": latest[0].isoformat()+"T23:59:59Z",
            "market_status": "STATUS NÃO CONFIRMADO",
            "source": "Twelve Data · fechamento diário", "delayed": True,
            "source_url": "https://twelvedata.com/"}

def collect(api_key, mapping):
    result = []
    for market_id, symbol in mapping.items():
        if market_id not in IDS or not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Unknown market ID or empty symbol")
        params = urllib.parse.urlencode({"symbol":symbol,"interval":"1day","outputsize":5,"apikey":api_key})
        request = urllib.request.Request(URL+"?"+params, headers={"User-Agent":"MundoNovo-GlobalMarketTicker/1.0 (authorized API)"})
        try:
            with urllib.request.urlopen(request, timeout=18) as response:
                payload = json.load(response)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"{market_id}: provider unavailable ({type(exc).__name__})", file=sys.stderr)
            continue
        try:
            result.append(parse_daily(payload,market_id,symbol))
        except ValueError as exc:
            print(f"{market_id}: {exc}",file=sys.stderr)
    return result

def main():
    if os.getenv("MARKET_DATA_PUBLICATION_AUTHORIZED") != "yes":
        print("No public redistribution authorization; preserving existing data.")
        return 0
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    mapping_text = os.getenv("MARKET_SYMBOLS_JSON")
    if not api_key or not mapping_text:
        print("Missing API key or verified symbol mapping; no update.")
        return 0
    mapping = json.loads(mapping_text)
    if not isinstance(mapping,dict) or not mapping:
        raise ValueError("MARKET_SYMBOLS_JSON must be a nonempty object")
    collected = collect(api_key,mapping)
    existing = {}
    if OUTPUT.exists():
        data=json.loads(OUTPUT.read_text(encoding="utf-8"))
        existing={q["id"]:q for q in data.get("quotes",[]) if q.get("id") in IDS}
    for q in collected:
        old=existing.get(q["id"])
        if old and old.get("as_of","")>q["as_of"]:
            continue
        existing[q["id"]]=q
    if not collected:
        print("No valid new data; keeping last validated prices.")
        return 0
    result={"schema_version":1,"provider":"Twelve Data","data_type":"daily_close","quotes":list(existing.values())}
    content=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=content:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(content,encoding="utf-8")
    print(f"Validated {len(collected)} observations; stored {len(existing)} markets.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
