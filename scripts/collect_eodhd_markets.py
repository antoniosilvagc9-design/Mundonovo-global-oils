import os,json,math,datetime,urllib.request,urllib.parse,urllib.error
from pathlib import Path
key=os.environ["EODHD_API_KEY"]
now=datetime.datetime.now(datetime.timezone.utc)
markets=[("idx","JKSE","Jakarta Composite"),("sp500","GSPC","S&P 500"),("ibov","BVSP","Ibovespa"),("nifty","NSEI","Nifty 50"),("nikkei","N225","Nikkei 225"),("shcomp","SSEC","Shanghai Composite"),("euronext","N100","Euronext 100")]
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
fmp_publish=os.getenv("FMP_PUBLIC_DISPLAY_AUTHORIZED")=="true"
old=json.loads(path.read_text()) if path.exists() else {}
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
fmp_key=os.getenv("FMP_API_KEY")
if fmp_key:
    try:
        url="https://financialmodelingprep.com/stable/quote?"+urllib.parse.urlencode(dict(symbol="ESUSD",apikey=fmp_key))
        with urllib.request.urlopen(url,timeout=25) as response: rows=json.load(response)
        d=rows[0] if isinstance(rows,list) and rows else {}
        p=num(d.get("price")); ts=num(d.get("timestamp"))
        try: pct=float(d.get("changePercentage"))
        except (TypeError,ValueError): pct=float("nan")
        if d.get("symbol")=="ESUSD" and "e-mini" in str(d.get("name","")).lower() and p and ts and ts<4102444800 and math.isfinite(pct) and pct>-100:
            dt=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc)
            if dt<=now and (now-dt).total_seconds()<120*3600:
                q=dict(id="cme",symbol="ESUSD",index_name="E-mini S&P 500 Futures",source="FMP",price=p,previous_close=p/(1+pct/100),change_percent=pct,as_of=dt.isoformat(),fetched_at=now.isoformat(),data_status="latest_quote_delay_unverified")
                print("ESUSD validated",q["as_of"])
                if fmp_publish and q["as_of"]>=quotes.get("cme",{}).get("as_of",""): quotes["cme"]=q
    except urllib.error.HTTPError as e: print("FMP HTTP",e.code)
    except Exception as e: print("FMP",type(e).__name__)
if publish or fmp_publish:
    quotes={i:q for i,q in quotes.items() if (q.get("source")=="EODHD" and publish) or (q.get("source")=="FMP" and fmp_publish)}
    path.write_text(json.dumps(dict(schema_version=1,provider="multiple",quotes=list(quotes.values())),indent=2)+"\n")
else: print("Diagnostic only: public display authorization not configured.")
