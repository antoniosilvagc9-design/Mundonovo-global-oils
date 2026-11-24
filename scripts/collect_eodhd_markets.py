import os,json,math,datetime,urllib.request,urllib.parse,urllib.error
from pathlib import Path
key=os.environ["EODHD_API_KEY"]
now=datetime.datetime.now(datetime.timezone.utc)
markets=[("idx","JKSE","Jakarta Composite"),("sp500","GSPC","S&P 500"),("ibov","BVSP","Ibovespa"),("nifty","NSEI","Nifty 50"),("nikkei","N225","Nikkei 225"),("shcomp","SSEC","Shanghai Composite"),("euronext","N100","Euronext 100"),("klci","BMPLA","Bursa Malaysia Plantation Index")]
def get(path,**params):
    try:
        url="https://eodhd.com/api/"+path+"?"+urllib.parse.urlencode(dict(api_token=key,fmt="json",**params))
        with urllib.request.urlopen(url,timeout=25) as r: return json.load(r)
    except urllib.error.HTTPError as e: print(path,"HTTP",e.code)
    except Exception as e: print(path,type(e).__name__)
def num(x):
    try:
        n=float(x)
        return n if math.isfinite(n) and n>0 else None
    except (ValueError,TypeError): return None
path=Path("data/global-market-ticker.json")
publish=os.getenv("EODHD_PUBLIC_DISPLAY_AUTHORIZED")=="true"
old=json.loads(path.read_text()) if publish and path.exists() else {}
quotes={q["id"]:q for q in old.get("quotes",[]) if "id" in q}
for ident,symbol,name in markets:
    code=symbol+".INDX"
    d=get("real-time/"+code)
    q=None
    if isinstance(d,dict) and d.get("code")==code:
        p,prev,ts=map(num,[d.get("close"),d.get("previousClose"),d.get("timestamp")])
        if p and prev and ts and ts<4102444800:
            dt=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc)
            if dt<=now and (now-dt).total_seconds()<120*3600:
                q=dict(price=p,previous_close=prev,as_of=dt.isoformat(),data_status="latest_quote_delay_unverified")
    if not q:
        rows=get("eod/"+code,**{"from":(now.date()-datetime.timedelta(days=15)).isoformat(),"order":"d"})
        if isinstance(rows,list):
            bars=sorted({r["date"]:num(r.get("close")) for r in rows if isinstance(r,dict) and r.get("date") and num(r.get("close"))}.items(),reverse=True)
            if len(bars)>=2:
                q=dict(price=bars[0][1],previous_close=bars[1][1],as_of=bars[0][0],data_status="daily_close")
    if q:
        q.update(id=ident,symbol=code,index_name=name,source="EODHD",fetched_at=now.isoformat(),change_percent=(q["price"]/q["previous_close"]-1)*100)
        print(code,q["data_status"],q["as_of"])
        if publish:
            prior=quotes.get(ident)
            if not prior or prior.get("symbol")!=code or q["as_of"]>=prior.get("as_of",""): quotes[ident]=q
    else: print(code,"unavailable")
if publish:
    path.write_text(json.dumps(dict(schema_version=1,provider="EODHD",quotes=list(quotes.values())),indent=2)+"\n")
else: print("Diagnostic only: public display authorization not configured.")
