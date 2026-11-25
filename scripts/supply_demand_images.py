import os,json,urllib.request,urllib.parse,pathlib
root=pathlib.Path("data/supply-demand/images")
root.mkdir(parents=True,exist_ok=True)
key=os.environ["PIXABAY_API_KEY"]
queries={"indonesia":"oil palm plantation aerial","para":"dry agricultural soil drought","stocks":"industrial storage tanks","china":"cargo ship port terminal","biodiesel":"industrial refinery tanks","energy":"oil refinery"}
manifest={}
for name,q in queries.items():
    try:
        url="https://pixabay.com/api/?"+urllib.parse.urlencode({"key":key,"q":q,"image_type":"photo","orientation":"horizontal","safesearch":"true","per_page":15})
        with urllib.request.urlopen(url,timeout=30) as r: hits=json.load(r)["hits"]
        if not hits: continue
        h=hits[0]
        with urllib.request.urlopen(h["largeImageURL"],timeout=30) as r: data=r.read()
        if not data.startswith(b"\xff\xd8"): continue
        (root/(name+".jpg")).write_bytes(data)
        manifest[name]={"path":"data/supply-demand/images/"+name+".jpg","page":h["pageURL"],"author":h["user"],"tags":h["tags"],"query":q}
    except Exception as e: print(name,type(e).__name__)
if not manifest: raise SystemExit("No images collected")
p=root/"manifest.json"
old=json.loads(p.read_text()) if p.exists() else {}
old.update(manifest)
p.write_text(json.dumps(old,ensure_ascii=False,indent=2))
