import os,json,urllib.request,urllib.parse,urllib.error,pathlib
root=pathlib.Path("data/supply-demand/images")
root.mkdir(parents=True,exist_ok=True)
key=os.environ.get("PIXABAY_API_KEY","").strip()
if not key: raise SystemExit("PIXABAY_API_KEY ausente")
# Each group must match at least one exact tag. Never infer geographic location.
rules={
"climatepara":(["drought dry landscape","dry river drought","drought dry field"],[{"drought","dry","arid"},{"landscape","river","field","soil","earth","lake","reservoir"}],{"fire","flame","wildfire","corn","cornfield"}),
"cropstress":(["cracked dry soil","drought cracked earth"],[{"drought","dry","arid"},{"soil","earth","cracked soil","cracks","ground"}],{"corn","cornfield"}),
"rainrisk":(["dry reservoir drought","drought river low water"],[{"drought","dry","water shortage"},{"river","reservoir","lake","water","riverbed"}],set()),
"indonesia":(["oil palm plantation","palm plantation","palm oil plantation"],[{"oil palm","palm oil"},{"plantation","palm plantation","oil palm plantation","aerial","palm trees","field"}],{"fruit","food","seed","nut"}),
"para":(["oil palm plantation","palm plantation","palm trees agriculture"],[{"oil palm","palm oil"},{"plantation","palm plantation","oil palm plantation","aerial","palm trees","field"}],{"corn","cornfield","fruit","food","seed"}),
"stocks":(["oil storage tanks","storage tank industrial","tank farm"],[{"tank","tanks","storage tank","storage tanks","oil tank","oil tanks","tank farm"},{"storage","oil","industrial","industry","refinery","tank farm","storage tank","storage tanks"}],set()),
"china":(["oil tanker ship","tanker port","cargo ship port"],[{"ship","cargo ship","tanker","oil tanker","container ship"},{"port","harbor","harbour","terminal","tanker","oil tanker"}],set()),
"biodiesel":(["biodiesel plant","biofuel refinery","oil refinery"],[{"biodiesel","biofuel","refinery","oil refinery"},{"industry","industrial","plant","factory","refinery","oil refinery"}],{"port","ship"}),
"energy":(["oil refinery","petroleum refinery"],[{"refinery","oil refinery"},{"oil","petroleum","energy","oil refinery"}],set())
}
def tags(h): return {t.strip().lower() for t in h.get("tags","").split(",")}
def score(h,groups,exclude):
    t=tags(h)
    if t & exclude or not all(t & g for g in groups): return -1
    return sum(len(t & g) for g in groups)+2*bool(t & {"drought","dry","aerial","oil tanker","biodiesel","storage tanks"})
def get(url,accept=None):
    headers={"User-Agent":"MundoNovoTrade/1.0"}
    if accept: headers["Accept"]=accept
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r: return r.read()
p=root/"manifest.json"
old=json.loads(p.read_text()) if p.exists() else {}
manifest={}
used=set()
for name,(queries,groups,exclude) in rules.items():
    candidates={}
    try:
        for q in queries:
            url="https://pixabay.com/api/?"+urllib.parse.urlencode({"key":key,"q":q,"image_type":"photo","orientation":"horizontal","safesearch":"true","per_page":50})
            for h in json.loads(get(url,"application/json"))["hits"]:
                v=score(h,groups,exclude)
                if v>=0: candidates[h["id"]]=(v,h,q)
        for v,h,q in sorted(candidates.values(),key=lambda x:x[0],reverse=True):
            if h["pageURL"] in used: continue
            data=get(h["largeImageURL"])
            if not data.startswith(b"\xff\xd8"): continue
            (root/(name+".jpg")).write_bytes(data)
            manifest[name]={"path":"data/supply-demand/images/"+name+".jpg","page":h["pageURL"],"author":h["user"],"tags":h["tags"],"query":q,"editorial_score":v}
            used.add(h["pageURL"])
            print(name,"accepted",h["id"],"score",v,flush=True)
            break
    except urllib.error.HTTPError as e: print(name,"HTTP",e.code,flush=True)
    except Exception as e: print(name,type(e).__name__,flush=True)
    if name not in manifest:
        previous=old.get(name,{})
        if previous.get("page") and previous["page"] not in used and score(previous,groups,exclude)>=0 and (root/(name+".jpg")).exists():
            manifest[name]=previous
            used.add(previous["page"])
        else: print(name,"no relevant image; omit from manifest",flush=True)
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
