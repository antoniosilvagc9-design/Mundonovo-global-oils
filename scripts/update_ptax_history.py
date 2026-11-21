#!/usr/bin/env python3
"""Trading Global: histórico oficial PTAX, sem preenchimento artificial."""
import json, urllib.parse, urllib.request, datetime as dt, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
today=dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date()
start=today-dt.timedelta(days=15)
fmt=lambda d:d.strftime("%m-%d-%Y")
params={"@moeda":"'USD'","@dataInicial":f"'{fmt(start)}'","@dataFinalCotacao":f"'{fmt(today)}'","$format":"json","$select":"cotacaoVenda,dataHoraCotacao,tipoBoletim","$orderby":"dataHoraCotacao asc"}
url="https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"+urllib.parse.urlencode(params,safe="'")
req=urllib.request.Request(url,headers={"User-Agent":"TradingGlobal/1.0","Accept":"application/json"})
with urllib.request.urlopen(req,timeout=30) as response:
    records=json.load(response)["value"]
days={}
for r in records:
    when=r.get("dataHoraCotacao","")
    val=r.get("cotacaoVenda")
    if when and isinstance(val,(float,int)) and val>0:
        day=when[:10]
        if day not in days or when>days[day]["time"]:
            days[day]={"time":when,"value":val,"type":r.get("tipoBoletim","")}
points=[days[d] for d in sorted(days)[-3:]]
if len(points)<2: raise RuntimeError("Menos de dois pregões PTAX; preservando arquivo anterior")
output={"source":"Banco Central do Brasil — PTAX venda","source_url":"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/","unit":"BRL/USD","type":"Último boletim disponível em cada dia útil","updated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"points":points}
dest=ROOT/"data"/"usd-brl-history.json"
dest.parent.mkdir(exist_ok=True)
dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("PTAX: ",len(points),"pregões; último",points[-1]["time"])
