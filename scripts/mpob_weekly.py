#!/usr/bin/env python3
"""Download MPOB weekly price XLSX and export validated observations."""
import datetime as dt
import io
import json
import re
import urllib.request
from pathlib import Path
from openpyxl import load_workbook

BASE = "https://price.mpob.gov.my/excel/weekly/weekly_report/"
OUT = Path("data/mpob-weekly-prices.json")
REGIONS = ["NORTH", "SOUTH", "CENTRAL", "EAST COAST", "P. MALAYSIA", "SABAH", "SARAWAK", "MALAYSIA"]

def number(value):
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    value = value.strip().replace(",", "")
    return float(value) if re.fullmatch(r"\d+(?:\.\d+)?", value) else None

def collect(year, month):
    url = f"{BASE}{year}{month:02d}01"
    req = urllib.request.Request(url, headers={"User-Agent": "MundoNovo-DataResearch/1.0", "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"})
    with urllib.request.urlopen(req, timeout=35) as response:
        content = response.read(4_000_001)
    if len(content) > 4_000_000 or not content.startswith(b"PK"):
        raise ValueError(f"Not an XLSX file: {url}")
    sheet = load_workbook(io.BytesIO(content), read_only=True, data_only=True).active
    rows = list(sheet.values)
    if not rows or "WEEKLY PALM OIL PRICES" not in str(rows[0][0]).upper():
        raise ValueError(f"Unexpected worksheet heading: {url}")
    header = [str(x).strip().upper() if x is not None else "" for x in rows[1]]
    cols = {region: header.index(region) for region in REGIONS if region in header}
    if "MALAYSIA" not in cols or "P. MALAYSIA" not in cols:
        raise ValueError(f"Missing regional columns: {url}")
    records = []
    week = None
    week_dates = None
    for row in rows[2:]:
        label = str(row[0]).strip() if row[0] is not None else ""
        if re.match(r"^\d+(st|nd|rd|th) Week$", label, re.I):
            week = label
            week_dates = str(row[1]).strip() if row[1] is not None else None
            continue
        if not week or label not in ("Crude Palm Oil (Local Delivered)", "Palm Kernel (Ex-Mill)", "Crude Palm Kernel Oil (Local Delivered)"):
            continue
        for region, col in cols.items():
            raw = row[col] if col < len(row) else None
            records.append({"month": f"{year}-{month:02d}", "week": week, "week_dates": week_dates, "product": label, "region": region, "price_rm_per_tonne": number(raw), "raw": str(raw).strip() if raw is not None else None})
    if not records or not any(x["price_rm_per_tonne"] is not None for x in records):
        raise ValueError(f"No usable prices: {url}")
    return {"month": f"{year}-{month:02d}", "source_url": url, "records": records}

def main():
    today = dt.datetime.now(dt.timezone.utc)
    last = min(today.month if today.year == 2026 else 12, 11) if today.year >= 2026 else 0
    if last < 1:
        raise RuntimeError("No 2026 reports due yet")
    months = []
    errors = []
    for month in range(1, last + 1):
        try:
            report = collect(2026, month)
            months.append(report)
            print(f"OK {report['month']}: {len(report['records'])} observations")
        except Exception as exc:
            errors.append(f"2026-{month:02d}: {exc}")
            print(f"FAILED {errors[-1]}")
    if errors:
        raise RuntimeError("Incomplete MPOB download; existing dataset preserved. " + "; ".join(errors))
    result = {"source": "Malaysian Palm Oil Board (MPOB)", "unit": "RM/tonne", "fetched_at_utc": today.isoformat(), "months": months}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {OUT}: {sum(len(m['records']) for m in months)} observations")

if __name__ == "__main__":
    main()
