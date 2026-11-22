#!/usr/bin/env python3
"""One-shot, low-volume diagnostic. Does not bypass access controls."""
import datetime as dt
import json
import urllib.error
import urllib.request

TARGETS = [
    "https://www.bursamalaysia.com/",
    "https://www.bursamalaysia.com/market_information/market_statistic/derivatives",
    "https://www.bursamalaysia.com/misc/missftp/derivative/derivative_trading_statistic_20261120.csv",
]
def inspect(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MundoNovo-TradingGlobal-Diagnostics/1.0 (public market data access check)"})
    record = {"url": url, "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            body = response.read(512)
            record.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get("Content-Type"),
                          content_length=response.headers.get("Content-Length"),
                          looks_like_csv=b"day_id" in body and b"prod_id" in body)
    except urllib.error.HTTPError as exc:
        record.update(status=exc.code, content_type=exc.headers.get("Content-Type"),
                      error="HTTP response denied or unavailable; no retry")
    except Exception as exc:
        record.update(error=type(exc).__name__, detail=str(exc)[:180])
    return record
if __name__ == "__main__":
    for target in TARGETS:
        print(json.dumps(inspect(target), ensure_ascii=False))
