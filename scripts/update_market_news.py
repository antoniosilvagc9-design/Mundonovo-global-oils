#!/usr/bin/env python3
"""Coleta RSS pública, sem scraping de matérias nem análise inventada."""
import os
import datetime as dt, email.utils, hashlib, json, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"market-news.json"
NOW=dt.datetime.now(dt.timezone.utc)
TOPICS=[
 ("Óleo de palma","palm oil Malaysia Indonesia MPOB exports stocks"),
 ("Soja","soybean oil CBOT USDA Brazil Argentina exports"),
 ("Biodiesel","Indonesia biodiesel B40 B50 palm oil mandate"),
 ("Logística","shipping freight ports Red Sea trade commodities"),
 ("Câmbio","Federal Reserve dollar Brazilian real exchange rate"),
 ("Petróleo","Brent crude oil OPEC EIA supply"),
 ("Comércio exterior","India China vegetable oil imports tariffs")
]
COUNTRIES={"malásia":["malaysia","malaysian","mpob"],"indonésia":["indonesia","indonesian","gapki"],"china":["china","chinese"],"índia":["india","indian"],"brasil":["brazil","brasil","brazilian"],"estados unidos":["united states","u.s.","usda","federal reserve"],"argentina":["argentina"],"união europeia":["european union","eu commission"]}
HIGH=["export ban","tariff hike","supply disruption","port closure","biodiesel mandate","export tax","embargo","sanctions","production cut"]
MED=["export","import","stock","harvest","demand","price","interest rate","freight","policy","forecast","tariff","crop","biodiesel"]
def fetch(topic):
 q=urllib.parse.quote(topic+" when:7d")
 url=f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
 req=urllib.request.Request(url,headers={"User-Agent":"TradingGlobalNews/1.0 (+https://github.com/antoniosilvagc9-design/Mundonovo-global-oils)"})
 with urllib.request.urlopen(req,timeout=22) as resp:
  return ET.fromstring(resp.read(2_000_000))
def parse_date(raw):
 try:return email.utils.parsedate_to_datetime(raw).astimezone(dt.timezone.utc)
 except (TypeError,ValueError,OverflowError):return None
# Pixabay: busca imagens temáticas; a chave fica apenas no GitHub Actions.
PIXABAY_TERMS={
 "Óleo de palma":"oil palm plantation",
 "Soja":"soybean field",
 "Biodiesel":"biofuel agriculture",
 "Logística":"cargo container port",
 "Câmbio":"finance currency exchange",
 "Petróleo":"oil refinery",
 "Comércio exterior":"cargo shipping containers",
}
def pixabay_images(category, api_key):
 if not api_key:
  return []
 params=urllib.parse.urlencode({
  "key":api_key,"q":PIXABAY_TERMS.get(category,"global trade"),
  "image_type":"photo","safesearch":"true","per_page":20,
  "orientation":"horizontal",
 })
 try:
  req=urllib.request.Request("https://pixabay.com/api/?"+params,
      headers={"User-Agent":"TradingGlobalNews/1.0"})
  with urllib.request.urlopen(req,timeout=12) as response:
   data=json.load(response)
  return [{"url":hit["webformatURL"],"page":hit.get("pageURL",""),
           "author":hit.get("user","Pixabay")}
          for hit in data.get("hits",[])
          if str(hit.get("webformatURL","")).startswith("https://")]
 except Exception as exc:
  # Nunca registrar a URL da requisição, pois ela contém a chave.
  print("Pixabay indisponível para",category,":",type(exc).__name__)
  return []

def main():
 items={};errors=[]
 for category,query in TOPICS:
  try:root=fetch(query)
  except Exception as exc:errors.append(category+": "+str(exc)[:140]);continue
  for node in root.findall("./channel/item"):
   title=(node.findtext("title") or "").strip()
   link=(node.findtext("link") or "").strip()
   pub=parse_date(node.findtext("pubDate"))
   source_node=node.find("source")
   source=(source_node.text or "").strip() if source_node is not None else ""
   if not title or not link.startswith("https://") or not pub or not source:continue
   if pub>NOW+dt.timedelta(minutes=10) or pub<NOW-dt.timedelta(days=7):continue
   # Google News fornece manchete, fonte e link; não fornece o texto integral verificado.
   normalized=re.sub(r"\W+","",title.lower())
   key=hashlib.sha256((normalized[:100]+"|"+source.lower()).encode()).hexdigest()[:18]
   hay=(title+" "+source).lower()
   regions=[name.title() for name,keys in COUNTRIES.items() if any(k in hay for k in keys)]
   hits_high=[w for w in HIGH if w in hay];hits_med=[w for w in MED if w in hay]
   impact="Alto" if hits_high else "Médio" if hits_med else "Baixo"
   reason=("Termo de possível impacto elevado na manchete: "+", ".join(hits_high[:2]) if hits_high else
           "A manchete menciona fatores de mercado: "+", ".join(hits_med[:2]) if hits_med else
           "Monitoramento informativo; impacto econômico não confirmado")
   obj={"id":key,"title_original":title,"title_pt":None,"summary_pt":None,
    "source":source,"url":link,"published_at":pub.isoformat(),"collected_at":NOW.isoformat(),
    "regions":regions or ["Global"],"category":category,"commodities":[category] if category in ("Óleo de palma","Soja","Petróleo") else [],
    "impact":impact,"impact_reason":reason,"context_confirmed":None,"commercial_analysis":None,
    "verification":"Metadados RSS; conteúdo integral não verificado","language":"en","source_type":"Google News RSS (agregador)"}
   if key not in items or pub>dt.datetime.fromisoformat(items[key]["published_at"]):items[key]=obj
 ordered=sorted(items.values(),key=lambda x:({"Alto":2,"Médio":1,"Baixo":0}[x["impact"]],x["published_at"]),reverse=True)[:80]
 if not ordered:
  if OUT.exists():print("Nenhuma notícia nova; preservando último arquivo válido.");return
  raise RuntimeError("Nenhum RSS acessível com notícias verificáveis: "+"; ".join(errors))
 api_key=os.environ.get("PIXABAY_API_KEY", "").strip()
 if not api_key: raise RuntimeError("PIXABAY_API_KEY não configurada")
 image_dir=ROOT/"data"/"news-images"
 image_dir.mkdir(parents=True,exist_ok=True)
 pools={}; used=set(); count=0
 for item in ordered:
  category=item["category"]
  if category not in pools: pools[category]=pixabay_images(category,api_key)
  for photo in pools[category]:
   if photo["url"] in used: continue
   filename=hashlib.sha256(photo["url"].encode()).hexdigest()[:24]+".jpg"
   target=image_dir/filename
   try:
    if not target.exists():
     with urllib.request.urlopen(photo["url"],timeout=15) as response:
      content=response.read(5_000_001)
     if len(content)>5_000_000 or not content.startswith(b"\xff\xd8"): continue
     target.write_bytes(content)
    used.add(photo["url"])
    item["image"]={"url":"https://antoniosilvagc9-design.github.io/Mundonovo-global-oils/data/news-images/"+filename,"page":photo["page"],"author":photo["author"]}
    count+=1
    break
   except Exception as exc: print("Falha ao baixar imagem:",type(exc).__name__)
 print("Notícias com imagens:",count,"de",len(ordered))
 payload={"updated_at_utc":NOW.isoformat(),"feed":"Google News RSS — manchetes e metadados de terceiros","limitations":"Título no idioma original; resumo e análise não gerados sem acesso ao texto. Classificação heurística, não avaliação factual do impacto.","errors":errors,"news":ordered}
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Salvas",len(ordered),"notícias; fontes:",len(set(x["source"] for x in ordered)),"falhas:",len(errors))
if __name__=="__main__":main()
