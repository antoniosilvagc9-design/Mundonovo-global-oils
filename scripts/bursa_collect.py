"""Collect only after written permission; no publication by default."""
import argparse, csv, datetime as dt, hashlib, io, json, os, pathlib, time
import urllib.request, urllib.error
from zoneinfo import ZoneInfo

START = dt.date(2021, 11, 24)
BASE = "https://www.bursamalaysia.com/misc/missftp/derivative/derivative_trading_statistic_{}.csv"
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backfill", action="store_true")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--output", default="bursa-private")
    a = p.parse_args()
    if os.getenv("BURSA_DOWNLOAD_AUTHORIZED") != "true":
        print("Disabled: written download permission required.")
        return
    root = pathlib.Path(a.output)
    root.mkdir(parents=True, exist_ok=True)
    today = dt.datetime.now(ZoneInfo("Asia/Kuala_Lumpur")).date()
    day = START if a.backfill else max(START, today-dt.timedelta(days=7))
    count = 0
    while day <= today and count < a.limit:
        stamp = day.strftime("%Y%m%d")
        day += dt.timedelta(days=1)
        path = root / (stamp+".csv")
        if path.exists() and a.backfill:
            continue
        if dt.datetime.strptime(stamp,"%Y%m%d").weekday() >= 5:
            continue
        count += 1
        url = BASE.format(stamp)
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"MundoNovo market research collector"})
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read(10_000_001)
                if len(raw)>10_000_000 or "html" in response.headers.get("Content-Type","").lower():
                    raise ValueError("Unexpected response")
                if not response.url.startswith("https://www.bursamalaysia.com/"):
                    raise ValueError("Unexpected redirect")
            decoded = raw.decode("utf-8-sig")
            rows = list(csv.reader(io.StringIO(decoded)))
            if len(rows)<2 or not any(any("FCPO" in cell.upper() for cell in row) for row in rows) or "<html" in decoded.lower():
                raise ValueError("Unverified CSV schema")
            digest = hashlib.sha256(raw).hexdigest()
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
                path.write_bytes(raw)
                path.with_suffix(".json").write_text(json.dumps({"source":url,"sha256":digest,"requested_date":stamp,"rows":len(rows)},indent=2))
            print(stamp, "CSV candidate validated; schema/date review still required")
        except urllib.error.HTTPError as e:
            print(stamp, "HTTP", e.code)
            if e.code in (401,403,429): raise SystemExit("Access refused or limited; stop.")
        except (ValueError, UnicodeError, OSError) as e:
            print(stamp, str(e))
        time.sleep(3)
if __name__ == "__main__":
    main()
