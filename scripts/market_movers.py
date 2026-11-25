import os,json,urllib.request,urllib.parse,time,math
from datetime import datetime,timezone
from pathlib import Path
key=os.environ.get("FINNHUB_API_KEY")
if not key: raise SystemExit("Configure FINNHUB_API_KEY with public display rights before running.")
commodity="ADM BG CTVA MOS CF NTR DE XOM CVX COP SLB VLO MPC PSX FCX NEM BHP RIO VALE"
general="AAPL MSFT NVDA AMZN GOOGL META TSLA AVGO JPM BAC WMT COST KO PEP MCD DIS UNH JNJ CAT BA GE IBM ORCL NFLX AMD INTC"
nasdaq=set("AAPL MSFT NVDA AMZN GOOGL META TSLA AVGO COST PEP NFLX AMD INTC".split())
rows={}
for symbol in (commodity+" "+general).split():
    try:
        url="https://finnhub.io/api/v1/quote?"+urllib.parse.urlencode({"symbol":symbol,"token":key})
        with urllib.request.urlopen(url,timeout=20) as response: q=json.load(response)
        p,pc,t=float(q["c"]),float(q["pc"]),int(q["t"])
        if min(p,pc,t)<=0 or not all(map(math.isfinite,[p,pc])): raise ValueError()
        rows[symbol]={"name":symbol,"tv":("NASDAQ:" if symbol in nasdaq else "NYSE:")+symbol,"price":p,"change":100*(p/pc-1),"timestamp":t}
    except Exception:
        raise SystemExit("Incomplete quote coverage for "+symbol+"; keeping previous snapshot.")
    time.sleep(1.2)
latest=max(r["timestamp"] for r in rows.values())
if time.time()-latest>7*86400: raise SystemExit("Stale quotes")
if any(latest-r["timestamp"]>36*3600 for r in rows.values()): raise SystemExit("Inconsistent quote sessions")
out={"updated_at":datetime.now(timezone.utc).isoformat(),"source":"Finnhub / TradingView (gráficos)","coverage":str(len(rows))+" ações monitoradas; últimos preços disponíveis, não ranking mundial"}
for label,universe in [("commodity",commodity),("general",commodity+" "+general)]:
    rr=[rows[x] for x in universe.split()]
    out[label+"-down"]=sorted((x for x in rr if x["change"]<0),key=lambda x:x["change"])[:3]
    out[label+"-up"]=sorted((x for x in rr if x["change"]>0),key=lambda x:-x["change"])[:3]
p=Path("data/market-movers.json");p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
