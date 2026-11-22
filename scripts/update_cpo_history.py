#!/usr/bin/env python3
"""FCPO Bursa Malaysia via Commodities-API; falha fechada se unidade/ativo não verificáveis."""
import datetime as dt
import json
import math
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

KEY=os.environ.get("COMMODITIES_API_KEY","").strip()
if not KEY:
    raise RuntimeError("Configure COMMODITIES_API_KEY em GitHub Actions Secrets (Settings > Secrets and variables > Actions).")
ROOT=Path(__file__).resolve().parents[1]
now=dt.datetime.now(dt.timezone.utc)
today=now.date()
end=today-dt.timedelta(days=1)
start=today-dt.timedelta(days=39)
# Uma janela de 40 dias cabe em dois intervalos de até 30 dias, conforme plano.
ranges=[(start,start+dt.timedelta(days=19)),(start+dt.timedelta(days=20),end)]
def query(start_date,end_date):
    params=urlencode({"access_key":KEY,"start_date":start_date.isoformat(),"end_date":end_date.isoformat(),"base":"MYR","symbols":"FCPO"})
    req=Request("https://commodities-api.com/api/timeseries?"+params,headers={"Accept":"application/json","User-Agent":"TradingGlobal/2.6"})
    with urlopen(req,timeout=40) as response:
        payload=json.load(response)
    if payload.get("success") is not True or payload.get("timeseries") is not True:
        raise RuntimeError("API recusou timeseries: "+str(payload.get("error",{}).get("type","erro não especificado")))
    if payload.get("base")!="MYR":
        raise RuntimeError("Base de moeda inesperada; esperado MYR")
    unit=str(payload.get("unit","")).lower()
    if not any(x in unit for x in ("tonne","ton","metric")):
        raise RuntimeError("Unidade não confirmada como tonelada métrica: "+repr(payload.get("unit")))
    rates=payload.get("rates")
    if not isinstance(rates,dict):raise RuntimeError("Resposta sem série rates")
    return rates,unit
values={}
for a,b in ranges:
    rates,unit=query(a,b)
    for day,record in rates.items():
        try:
            date=dt.date.fromisoformat(day)
            rate=float(record["FCPO"])
            # A API publica taxa inversa com base em moeda: MYR por tonelada = 1/rate.
            value=1/rate
            if not(math.isfinite(value) and 1000<value<15000 and start<=date<=end):continue
            values[day]=round(value,4)
        except (KeyError,ValueError,TypeError,ZeroDivisionError):
            continue
ordered=[{"date":d,"value":v} for d,v in sorted(values.items())]
if len(ordered)<3:raise RuntimeError("Menos de 3 preços FCPO válidos; preservando histórico anterior")
target=today-dt.timedelta(days=30)
bases=[p for p in ordered if target-dt.timedelta(days=10)<=dt.date.fromisoformat(p["date"])<=target]
if not bases:raise RuntimeError("Referência de 30 dias não encontrada")
base,latest,three=bases[-1],ordered[-1],ordered[-3:]
delta=round(latest["value"]-base["value"],4)
output={
 "source":"Commodities-API","source_url":"https://commodities-api.com/symbols/FCPO",
 "symbol":"FCPO","market":"Bursa Malaysia Derivatives",
 "instrument":"Futuro de óleo de palma (FCPO); não é preço físico MPOB",
 "currency":"MYR","unit":"MYR/tonelada métrica",
 "method":"base=MYR; preço calculado como 1/taxa FCPO retornada pela API",
 "updated_at_utc":now.isoformat(),"latest":latest,"baseline_30d":base,
 "last_three":three,"average_last_three":round(sum(p["value"] for p in three)/3,4),
 "change_30d_absolute":delta,"change_30d_percent":round(100*delta/base["value"],4)
}
dest=ROOT/"data"/"cpo-history.json"
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():
    old=json.loads(dest.read_text(encoding="utf-8"))
    if all(old.get(k)==output[k] for k in ("latest","baseline_30d","last_three")):
        print("Sem alteração nas observações; histórico preservado")
        raise SystemExit(0)
dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("FCPO validado",latest,"referência",base)
