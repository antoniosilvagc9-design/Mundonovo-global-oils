#!/usr/bin/env python3
"""Coleta RSS pública, sem scraping de matérias nem análise inventada."""
import os
import html
import urllib.error
import datetime as dt, email.utils, hashlib, json, pathlib, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"market-news.json"
NOW=dt.datetime.now(dt.timezone.utc)
TOPICS=[
 ("Economia Brasileira","(Fazenda OR Copom OR Selic OR IPCA OR PIB OR risco fiscal OR dívida pública OR dólar) (site:agenciabrasil.ebc.com.br OR site:gov.br OR site:bcb.gov.br OR site:ibge.gov.br OR site:valor.globo.com)","pt"),
 ("Economia Brasileira","Brazil (real OR fiscal OR central bank OR finance minister OR inflation OR interest rates) (site:reuters.com OR site:imf.org)","en"),
 ("Economia Brasileira","(Federal Reserve OR Fed OR juros americanos) (dólar OR real OR Brasil) (site:agenciabrasil.ebc.com.br OR site:valor.globo.com)","pt"),
 ("Óleo de palma","palm oil (MPOB OR Malaysia OR Bursa Malaysia) (site:bernama.com OR site:theedgemalaysia.com OR site:mpob.gov.my)","en"),
 ("Óleo de palma","palm oil (Indonesia OR China OR India) (site:reuters.com OR site:antaranews.com OR site:business-standard.com)","en"),
 ("Soja","soybeans OR soybean oil (site:reuters.com OR site:usda.gov OR site:ams.usda.gov)","en"),
 ("Soja","soja safra exportações (site:gov.br OR site:conab.gov.br OR site:canalrural.com.br)","pt"),
 ("Soja","soja aceite molienda exportaciones (site:bcr.com.ar OR site:bolsadecereales.com OR site:lanacion.com.ar)","es"),
 ("Biodiesel","biodiesel Indonesia (B40 OR B50 OR palm oil) (site:antaranews.com OR site:reuters.com OR site:esdm.go.id)","en"),
 ("Biodiesel","biodiesel mistura produção (site:gov.br OR site:canalrural.com.br)","pt"),
 ("Biodiesel","biodiesel biofuels (site:eia.gov OR site:epa.gov OR site:reuters.com OR site:europa.eu)","en"),
 ("Logística","(shipping OR freight OR port) (site:reuters.com OR site:maersk.com OR site:drewry.co.uk)","en"),
 ("Logística","portos frete exportações (site:gov.br OR site:portosdoparana.pr.gov.br)","pt"),
 ("Câmbio","(dollar OR exchange rate OR currencies) (site:reuters.com OR site:federalreserve.gov OR site:ecb.europa.eu)","en"),
 ("Câmbio","dólar câmbio Banco Central (site:agenciabrasil.ebc.com.br OR site:bcb.gov.br OR site:valor.globo.com)","pt"),
 ("Petróleo","(Brent OR crude oil) (site:reuters.com OR site:eia.gov OR site:opec.org)","en"),
 ("Comércio exterior","(China OR India) (imports OR tariffs OR trade) (site:reuters.com OR site:business-standard.com OR site:chinadaily.com.cn)","en"),
 ("Comércio exterior","(European Union OR EU) (trade OR imports OR tariffs) (site:reuters.com OR site:ec.europa.eu)","en"),
 ("Comércio exterior","exportaciones agroindustriales Argentina (site:bcr.com.ar OR site:argentina.gob.ar OR site:lanacion.com.ar)","es"),
]
COUNTRIES={"malásia":["malaysia","malaysian","mpob"],"indonésia":["indonesia","indonesian","gapki"],"china":["china","chinese"],"índia":["india","indian"],"brasil":["brazil","brasil","brazilian"],"estados unidos":["united states","u.s.","usda","federal reserve"],"argentina":["argentina","argentine","argentinian","rosario","ciara-cec","ciara cec","bolsa de cereales"],"união europeia":["european union","eu commission"]}
HIGH=["export ban","tariff hike","supply disruption","port closure","biodiesel mandate","export tax","embargo","sanctions","production cut"]
MED=["export","import","stock","harvest","demand","price","interest rate","freight","policy","forecast","tariff","crop","biodiesel"]

COUNTRIES["união europeia"] += ["european commission","comissão europeia","european central bank","union europea"]
COUNTRIES["estados unidos"] += ["estados unidos","eia","epa"]
HIGH += ["proibição de exportação","corte de produção","embargo","sanções","cierre de puerto","recorte de producción","suba de aranceles","b40","b50"]
MED += ["exportação","importação","estoque","safra","preço","juros","câmbio","frete","exportaciones","importaciones","cosecha","precios","molienda"]
LOCALES={"en":"hl=en-US&gl=US&ceid=US:en","es":"hl=es-419&gl=AR&ceid=AR:es-419","pt":"hl=pt-BR&gl=BR&ceid=BR:pt-419"}

MARKET_TERMS={
 "Economia Brasileira":r"fazenda|copom|selic|ipca|\\bpib\\b|infla[cç][aã]o|fiscal|d[ií]vida p[uú]blica|d[oó]lar|c[aâ]mbio|juros|banco central|balan[cç]a comercial|reforma tribut[aá]ria|finance minister|central bank|inflation|interest rates|brazilian real",
 "Óleo de palma":r"palm oil|oil palm|óleo de palma|azeite de dendê|\bdendê\b|\bcpo\b|\bmpob\b",
 "Soja":r"\bsoja\b|\bsoy\b|soybeans?|soybean oil|aceite de soja|oleaginosas|oilseeds",
 "Biodiesel":r"biodiesel|biofuels?|biocombust[ií]ve(?:l|is)|biocombustibles?|\bb40\b|\bb50\b",
 "Logística":r"shipping|freight|cargo|\bports?\b|\bportos?\b|puertos?|\bfrete\b|containers?|contêiner|sea transport",
 "Câmbio":r"\bdollar\b|\bdólar\b|exchange rate|\bcâmbio\b|\bcurrencies\b|\bcurrency\b|\bforex\b|federal reserve|banco central",
 "Petróleo":r"crude|\bbrent\b|\bwti\b|\bopec\b|\bpetróleo\b|oil prices?|oil supply|oil demand",
 "Comércio exterior":r"exports?|imports?|tariffs?|trade|exporta|importa|arancel|\btarifas?\b|comércio exterior",
}

def fetch(topic, language):
 q=urllib.parse.quote(topic+" when:30d")
 url=f"https://news.google.com/rss/search?q={q}&{LOCALES[language]}"
 req=urllib.request.Request(url,headers={"User-Agent":"TradingGlobalNews/1.0 (+https://github.com/antoniosilvagc9-design/Mundonovo-global-oils)"})
 with urllib.request.urlopen(req,timeout=22) as resp:
  return ET.fromstring(resp.read(2_000_000))
def feed_summary(node, headline, source):
 raw=html.unescape(node.findtext("description") or "")
 if "<ol" in raw.lower():return None
 plain=" ".join(html.unescape(re.sub(r"<[^>]+>"," ",raw)).split())
 plain=plain.removesuffix(source).strip(" -–")
 if plain.casefold().startswith(headline.casefold()):plain=plain[len(headline):].strip(" -–")
 if len(plain.split())<10 or plain.casefold() in headline.casefold():return None
 return plain[:900]

def parse_date(raw):
 try:return email.utils.parsedate_to_datetime(raw).astimezone(dt.timezone.utc)
 except (TypeError,ValueError,OverflowError):return None
# Pixabay: busca imagens temáticas; a chave fica apenas no GitHub Actions.
PIXABAY_TERMS={
 "Economia Brasileira":"Brazil finance economy currency",
 "Óleo de palma":"oil palm plantation",
 "Soja":"soybean field",
 "Biodiesel":"biofuel agriculture",
 "Logística":"oil tanker ship",
 "Câmbio":"finance currency exchange",
 "Petróleo":"oil refinery",
 "Comércio exterior":"chemical tanker ship",
}
COUNTRY_PHOTOS={
 "c546ab726313b88eda":("France","Bordeaux France","bordeaux|france"),
 "c54095d32cdaf6be41":("Indonesia","Bali Indonesia","bali|indonesia"),
 "6998352077adbeba34":("India","Taj Mahal India","taj.mah[a]?l|india"),
 "d729544ac15e9801e7":("Turkey","Istanbul Turkey","istanbul|turkey|türkiye"),
 "eu-steel-20261116":("Japan","Mount Fuji Japan","fuji|japan"),
 "87f329a7672f9aebd6":("Argentina","Argentina landscape","argentina"),
 "a256550742d83a3538":("Argentina","Argentina Patagonia","argentina"),
 "979b8e2adffd3da896":("Argentina","Buenos Aires Argentina","buenos.aires|argentina"),
}

def photo_identity(photo, category):
 page=photo.get("page","")
 match=re.search(r"-(\d+)/?$",page)
 if not match:return None
 description=(page+" "+photo.get("tags","")).lower()
 if "container" in description:return None
 maritime=(category in ("Logística","Comércio exterior") and not photo.get("illustrative_country")) or re.search(r"\b(ship|freighter|cargo|dock|harbour|harbor)\b",description)
 if maritime and (not re.search(r"\btanker\b",description) or re.search(r"\b(truck|aircraft|plane|firefighter)\b",description)):return None
 return match.group(1)

ECONOMY_QUERIES={
 "fiscal":["Brasilia congress architecture","Brasilia government buildings","public finance documents"],
 "markets":["stock exchange trading screen","financial market chart","business district Sao Paulo"],
 "rates":["central bank building","financial calculator documents","bank office"],
 "prices":["supermarket shopping groceries","Brazil retail market","shopping basket"],
 "trade":["Brazil industrial factory","Brazil port aerial","warehouse logistics"],
 "currency":["currency exchange office","US dollar banknotes","Brazilian real banknotes"],
 "general":["Sao Paulo skyline","business meeting office","Brazil commercial buildings"],
}
def economy_theme(item):
 title=(item.get("title_original","")+" "+item.get("title_pt","")).lower()
 for theme,pattern in [
  ("fiscal",r"trabuco|fazenda|fiscal|tribut|congresso|d[ií]vida|governo"),
  ("rates",r"selic|copom|juros|central bank|banco central|federal reserve"),
  ("prices",r"ipca|infla|pre[cç]os|consumo"),
  ("markets",r"ibovespa|bolsa|a[cç][oõ]es|investiment"),
  ("trade",r"export|import|ind[uú]stria|com[eé]rcio|pib"),
  ("currency",r"d[oó]lar|c[aâ]mbio|currency|exchange rate")]:
  if re.search(pattern,title):return theme
 return "general"

def economy_visual(photo):
 s=(photo.get("page","")+" "+photo.get("tags","")).lower()
 if re.search(r"banknote|ballots|brazilian money|brazilian real|currency|money|note",s):return "money"
 if re.search(r"chart|graph|trading screen|stock market",s):return "chart"
 if re.search(r"building|architecture|skyline|city|congress",s):return "architecture"
 if re.search(r"office|meeting|business people",s):return "office"
 if re.search(r"supermarket|shopping|groceries",s):return "retail"
 if re.search(r"factory|industrial|warehouse|port",s):return "industry"
 return "other"

def pixabay_images(category, api_key):
 if not api_key:
  return []
 params=urllib.parse.urlencode({
  "key":api_key,"q":PIXABAY_TERMS.get(category,category),
  "image_type":"photo","safesearch":"true","per_page":200,
  "orientation":"horizontal",
 })
 try:
  req=urllib.request.Request("https://pixabay.com/api/?"+params,
      headers={"User-Agent":"TradingGlobalNews/1.0"})
  with urllib.request.urlopen(req,timeout=12) as response:
   data=json.load(response)
  return [{"url":hit["webformatURL"],"page":hit.get("pageURL",""),
           "author":hit.get("user","Pixabay"),"tags":hit.get("tags","") or ""}
          for hit in data.get("hits",[])
          if str(hit.get("webformatURL","")).startswith("https://")]
 except Exception as exc:
  # Nunca registrar a URL da requisição, pois ela contém a chave.
  print("Pixabay indisponível para",category,":",type(exc).__name__,getattr(exc,"code",""))
  return []

def translate_titles(items):
 previous={}
 try:
  previous={n['title_original']:n['title_pt'] for n in json.loads(OUT.read_text(encoding='utf-8'))['news'] if n.get('title_pt')}
 except (OSError,ValueError,KeyError,TypeError): pass
 try:
  summaries={n['id']:n['summary_pt'] for n in json.loads(OUT.read_text(encoding='utf-8'))['news'] if n.get('summary_pt')}
 except (OSError,ValueError,KeyError,TypeError): summaries={}
 for item in items:
  item['summary_pt']=item.get('summary_pt') or summaries.get(item['id'])
  if item.get('language')=='pt' and item.get('summary_original') and not item['summary_pt']:
   item['summary_pt']=item['summary_original']
  item['title_pt']=item['title_original'] if item.get('language')=='pt' else previous.get(item['title_original'])
 for code in ('en','es'):
  pending=[n for n in items if n.get('language','en')==code and (not n['title_pt'] or (n.get('summary_original') and not n.get('summary_pt')))]
  if not pending: continue
  try:
   import argostranslate.package as pkg
   import argostranslate.translate as tr
   def translator():
    langs=tr.get_installed_languages()
    src=next((l for l in langs if l.code==code),None)
    pt=next((l for l in langs if l.code in ('pt_BR','pt-br','pt')),None)
    if src and pt:
     try:return src.get_translation(pt)
     except Exception:return None
    return None
   engine=translator()
   if engine is None:
    pkg.update_package_index()
    packages=pkg.get_available_packages()
    def install(source,targets):
     candidates=[p for p in packages if p.from_code==source and p.to_code in targets]
     if not candidates:return False
     pkg.install_from_path(candidates[0].download())
     return True
    if not install(code,('pt_BR','pt-br','pt')) and code=='es':
     install('es',('en',))
     install('en',('pt_BR','pt-br','pt'))
    engine=translator()
   if engine is None:raise RuntimeError('Modelo indisponível')
   for item in pending:
    try:
     if item.get('summary_original') and not item.get('summary_pt'):
      item['summary_pt']=engine.translate(item['summary_original']).strip()
     if item.get('title_pt'):continue
     title=item['title_original']; suffix=' - '+item['source']
     has_suffix=title.endswith(suffix)
     translated=engine.translate(title[:-len(suffix)] if has_suffix else title).strip()
     if translated:item['title_pt']=translated+(suffix if has_suffix else '')
    except Exception as exc:print('Falha na tradução',code,type(exc).__name__)
  except Exception as exc:print('Argos indisponível',code,type(exc).__name__,str(exc)[:180])
  print('Argos',code,': traduzidas',sum(bool(n.get('title_pt')) for n in pending),'de',len(pending))
 print('Argos: notícias traduzidas',sum(bool(n.get('title_pt')) for n in items),'de',len(items))

def main():
 items={};errors=[]
 for category,query,language in TOPICS:
  try:root=fetch(query,language)
  except Exception as exc:errors.append(category+": "+str(exc)[:140]);continue
  for node in root.findall("./channel/item"):
   title=(node.findtext("title") or "").strip()
   link=(node.findtext("link") or "").strip()
   pub=parse_date(node.findtext("pubDate"))
   source_node=node.find("source")
   source=(source_node.text or "").strip() if source_node is not None else ""
   if not title or not link.startswith("https://") or not pub or not source:continue
   headline=title.removesuffix(" - "+source).strip()
   if not re.search(MARKET_TERMS[category],headline,re.IGNORECASE):continue
   if pub>NOW+dt.timedelta(minutes=10) or pub<NOW-dt.timedelta(days=30):continue
   # Google News fornece manchete, fonte e link; não fornece o texto integral verificado.
   normalized=re.sub(r"\W+","",title.lower())
   key=hashlib.sha256((normalized[:100]+"|"+source.lower()).encode()).hexdigest()[:18]
   hay=(title+" "+source).lower()
   regions=[name.title() for name,keys in COUNTRIES.items() if any(re.search(r"(?<!\w)"+re.escape(k)+r"(?!\w)",hay) for k in keys)]
   hits_high=[w for w in HIGH if w in hay];hits_med=[w for w in MED if w in hay]
   impact="Alto" if hits_high else "Médio" if hits_med else "Baixo"
   reason=("Termo de possível impacto elevado na manchete: "+", ".join(hits_high[:2]) if hits_high else
           "A manchete menciona fatores de mercado: "+", ".join(hits_med[:2]) if hits_med else
           "Monitoramento informativo; impacto econômico não confirmado")
   obj={"id":key,"title_original":title,"title_pt":None,"summary_pt":None,"summary_original":feed_summary(node,headline,source),
    "source":source,"url":link,"published_at":pub.isoformat(),"collected_at":NOW.isoformat(),
    "regions":regions or ["Global"],"category":category,"commodities":[category] if category in ("Óleo de palma","Soja","Petróleo") else [],
    "impact":impact,"impact_reason":reason,"context_confirmed":None,"commercial_analysis":None,
    "verification":"Metadados RSS; conteúdo integral não verificado","language":language,"source_type":"Google News RSS (agregador)"}
   if category=="Economia Brasileira":
    obj["regions"]=list(dict.fromkeys(["Brasil",*regions]))
   if key not in items or (items[key]["category"]!="Economia Brasileira" and (category=="Economia Brasileira" or pub>dt.datetime.fromisoformat(items[key]["published_at"]))):items[key]=obj
 try:
  archive=json.loads(OUT.read_text(encoding="utf-8")).get("news",[])
 except (OSError,ValueError,TypeError):
  archive=[]
 cutoff=(NOW-dt.timedelta(days=30)).isoformat()
 for article in archive:
  if article.get("published_at","")>=cutoff and article.get("id"):
   if article["id"] in items and items[article["id"]]["category"]=="Economia Brasileira":
    items[article["id"]]=dict(article,category="Economia Brasileira",regions=list(dict.fromkeys(["Brasil",*article.get("regions",[])])))
   else:items.setdefault(article["id"],article)
 ranked=sorted(items.values(),key=lambda article:article["published_at"],reverse=True)
 reserved={}
 groups=[
  (sorted({topic[0] for topic in TOPICS}),lambda n:[n["category"]]),
  (["Global",*[name.title() for name in COUNTRIES]],lambda n:n["regions"]),
  (["Alto","Médio","Baixo"],lambda n:[n["impact"]]),
 ]
 for labels,values in groups:
  for label in labels:
   matching=[article for article in ranked if label in values(article)]
   for article in matching[:4]:
    reserved[article["id"]]=article
   if len(matching)<4:
    print("Cobertura em 30 dias:",label,len(matching),"de 4")
 for article in ranked:
  if len(reserved)>=200:break
  reserved.setdefault(article["id"],article)
 ordered=sorted(reserved.values(),key=lambda article:article["published_at"],reverse=True)
 if not ordered:
  if OUT.exists():print("Nenhuma notícia nova; preservando último arquivo válido.");return
  raise RuntimeError("Nenhum RSS acessível com notícias verificáveis: "+"; ".join(errors))
 api_key=os.environ.get("PIXABAY_API_KEY", "").strip()
 image_dir=ROOT/"data"/"news-images"
 image_dir.mkdir(parents=True,exist_ok=True)
 base="./data/news-images/"
 legacy_bases=("https://antoniosilvagc9-design.github.io/Mundonovo-global-oils/data/news-images/","https://inteligencia-design.github.io/Mundonovo-global-oils/data/news-images/")
 previous={}
 try:
  previous={n["id"]:n.get("image") for n in json.loads(OUT.read_text(encoding="utf-8"))["news"]}
 except (OSError,ValueError,KeyError,TypeError): pass
 identities=set(); digests=set(); used=set(); pools={}; attempts=0; count=0; stopped=False; failures=0
 economy_counts={}; economy_authors={}; theme_counts={}
 economy_total=sum(n["category"]=="Economia Brasileira" for n in ordered)
 visual_limit=max(2,(economy_total+5)//6)
 def economy_allowed(photo):
  v=economy_visual(photo); a=photo.get("author","")
  return economy_counts.get(v,0)<visual_limit and economy_authors.get(a,0)<max(2,(economy_total+9)//10)
 def economy_record(photo):
  v=economy_visual(photo); a=photo.get("author","")
  economy_counts[v]=economy_counts.get(v,0)+1; economy_authors[a]=economy_authors.get(a,0)+1
 # Preserve existing assignments before allocating new photographs.
 for item in ordered:
  item.pop("image",None)
  photo=previous.get(item["id"])
  if not isinstance(photo,dict): continue
  if item["category"]=="Economia Brasileira" and api_key and not economy_allowed(photo):continue
  identity=photo_identity(photo,item["category"])
  if not identity or identity in identities:continue
  url=photo.get("url","")
  for legacy in legacy_bases:
   if url.startswith(legacy):url=base+url.removeprefix(legacy);break
  filename=url.removeprefix(base)
  if url.startswith(base) and re.fullmatch(r"[a-f0-9]{24}\.jpg",filename) and filename not in used and (image_dir/filename).is_file():
   digest=hashlib.sha256((image_dir/filename).read_bytes()).digest()
   if digest in digests:continue
   digests.add(digest); identities.add(identity)
   item["image"]=dict(photo,url=url); used.add(filename); count+=1
   if item["category"]=="Economia Brasileira":economy_record(photo)
 for item in ordered:
  if "image" in item or stopped or not api_key: continue
  category=item["category"]
  country=COUNTRY_PHOTOS.get(item["id"])
  query=country[1] if country else category
  if category=="Economia Brasileira":
   theme=economy_theme(item); queries=ECONOMY_QUERIES[theme]; offset=theme_counts.get(theme,0)%len(queries); theme_counts[theme]=theme_counts.get(theme,0)+1
   queries=queries[offset:]+queries[:offset]
  else:queries=[query]
  candidates=[]
  for query in queries:
   if query not in pools:pools[query]=pixabay_images(query,api_key)
   candidates.extend(pools[query])
  if category=="Economia Brasileira":
   candidates.sort(key=lambda p:(economy_counts.get(economy_visual(p),0),economy_authors.get(p.get("author",""),0)))
  for photo in candidates:
   if category=="Economia Brasileira" and not economy_allowed(photo):continue
   if country:
    if not re.search(country[2],photo["page"]+" "+photo.get("tags",""),re.I):continue
    photo=dict(photo,illustrative_country=country[0])
   identity=photo_identity(photo,category)
   if not identity or identity in identities:continue
   filename=hashlib.sha256(identity.encode()).hexdigest()[:24]+".jpg"
   if filename in used: continue
   used.add(filename)
   target=image_dir/filename
   try:
    if not target.exists():
     if attempts>=len(ordered)+30: stopped=True; break
     attempts+=1
     req=urllib.request.Request(photo["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*;q=0.9,*/*;q=0.1"})
     with urllib.request.urlopen(req,timeout=15) as response:
      content=response.read(5_000_001)
     if len(content)>5_000_000 or not content.startswith(b"\xff\xd8"):
      print("Imagem inválida ou acima do limite"); continue
     target.write_bytes(content)
    digest=hashlib.sha256(target.read_bytes()).digest()
    if digest in digests:continue
    identities.add(identity); digests.add(digest)
    item["image"]={"illustrative_country":photo.get("illustrative_country"),"tags":photo.get("tags",""),"url":base+filename,"page":photo["page"],"author":photo["author"]}
    if category=="Economia Brasileira":economy_record(photo)
    count+=1; failures=0; break
   except urllib.error.HTTPError as exc:
    print("Falha no download: HTTP",exc.code); failures+=1
    if exc.code in (403,429) or failures>=5: stopped=True; break
   except Exception as exc:
    print("Falha ao baixar imagem:",type(exc).__name__); failures+=1
    if failures>=5: stopped=True; break
 print("Pixabay: downloads tentados",attempts,"notícias com imagens",count,"de",len(ordered))
 translate_titles(ordered)
 payload={"updated_at_utc":NOW.isoformat(),"feed":"Google News RSS — manchetes e metadados de terceiros","limitations":"Manchetes traduzidas automaticamente quando disponível; original preservado; resumo e análise não gerados sem acesso ao texto. Classificação heurística, não avaliação factual do impacto.","errors":errors,"news":ordered}
 OUT.parent.mkdir(exist_ok=True)
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Salvas",len(ordered),"notícias; fontes:",len(set(x["source"] for x in ordered)),"falhas:",len(errors))
if __name__=="__main__":main()
