#!/usr/bin/env python3
"""MPOB: preço diário local do CPO malaio, MYR/t; nunca confundir com futuro FCPO."""
import datetime as dt
import json
import re
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
now=dt.datetime.now(dt.timezone.utc)
today=now.date()
SOURCE="https://price.mpob.gov.my/dailys/mas_cpo/"
def parse_price(html, day):
    # A página diária do MPOB é uma fonte de preço físico local, não o futuro Bursa.
    # Exigir data e unidade identificáveis para evitar capturar números de outra tabela.
    clean=unescape(re.sub(r"<[^>]+>", " ", html))
    clean=re.sub(r"\\s+", " ", clean)
    if not re.search(r"(?:CPO|Crude Palm Oil)",clean,re.I) or not re.search(r"(?:RM|MYR)",clean,re.I):
        return None
    # Não inferir valor a partir de HTML arbitrário sem uma estrutura tabular estável.
    # O extrator exige metadados JSON-LD explícitos do dia para evitar cotações incorretas.
    for m in re.finditer(r'<script[^>]*type=["\\\']application/ld\\+json["\\\'][^>]*>(.*?)</script>',html,re.I|re.S):
        try:
            data=json.loads(m.group(1))
            entries=data if isinstance(data,list) else [data]
            for item in entries:
                if not isinstance(item,dict):continue
                price=item.get("price") or (item.get("offers") or {}).get("price")
                stamp=str(item.get("datePublished") or item.get("dateModified") or "")
                if stamp.startswith(day.isoformat()) and price is not None:
                    val=float(str(price).replace(",",""))
                    if 1000<val<15000:return round(val,4)
        except (ValueError,TypeError,AttributeError):
            continue
    return None

points=[]
for offset in range(47,-1,-1):
    day=today-dt.timedelta(days=offset)
    if day.weekday()>=5:continue
    url=SOURCE+day.strftime("%d/%m/%Y")
    try:
        req=Request(url,headers={"User-Agent":"Mozilla/5.0 TradingGlobal/2.6","Accept":"text/html"})
        with urlopen(req,timeout=12) as response:
            html=response.read().decode("utf-8",errors="replace")
        value=parse_price(html,day)
        if value is not None:points.append({"date":day.isoformat(),"value":value})
    except Exception as exc:
        print("Sem leitura validada",day, str(exc)[:90])
if len(points)<3:
    raise RuntimeError("MPOB não disponibilizou 3 preços extraíveis com validação; preservando arquivo anterior. É necessária integração com API/CSV oficial estruturado.")
target=today-dt.timedelta(days=30)
baseline=[p for p in points if target-dt.timedelta(days=10)<=dt.date.fromisoformat(p["date"])<=target]
if not baseline:raise RuntimeError("Referência de 30 dias indisponível; preservando arquivo")
base=baseline[-1];latest=points[-1];last_three=points[-3:]
average=round(sum(p["value"] for p in last_three)/3,4)
delta=round(latest["value"]-base["value"],4)
output={"source":"Malaysian Palm Oil Board (MPOB)","source_url":SOURCE,"instrument":"CPO local delivered, Malaysia; não é FCPO Bursa","unit":"MYR/tonelada","updated_at_utc":now.isoformat(),"latest":latest,"baseline_30d":base,"last_three":last_three,"average_last_three":average,"change_30d_absolute":delta,"change_30d_percent":round(100*delta/base["value"],4)}
path=ROOT/"data"/"cpo-history.json";path.parent.mkdir(parents=True,exist_ok=True)
if path.exists():
    old=json.loads(path.read_text(encoding="utf-8"))
    if all(old.get(k)==output[k] for k in ("latest","baseline_30d","last_three")):raise SystemExit(0)
path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
print("MPOB CPO:",latest)
