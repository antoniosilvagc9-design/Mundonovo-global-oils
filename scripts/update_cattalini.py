import requests, re, json, hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
url='http://www.unisolution.com.br/Clientes/Cattalini/CliCattaLineUp.asp'
r=requests.get(url,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
r.raise_for_status()
r.encoding='windows-1252'
soup=BeautifulSoup(r.text,'html.parser')
now=datetime.now(ZoneInfo('America/Sao_Paulo'))
rows=[]
berth=''
navio=''
def clean(t): return ' '.join(t.get_text(' ',strip=True).split())
def dt(s):
    try: return datetime.strptime(s,'%d/%m/%Y').date().isoformat()
    except ValueError: return ''
for tr in soup.find_all('tr'):
    cells=tr.find_all('td',recursive=False)
    sec=next((c for c in cells if c.get('colspan')=='10' and 'DescPier' in c.get('class',[])),None)
    if sec:
        berth=clean(sec);navio='';continue
    if len(cells)<9 or not berth: continue
    v=list(map(clean,cells))
    if v[4]:
        navio=re.sub(r'\s*\(CT\d+\)\s*$','',v[4]).strip()
        eta,etb,ets=dt(v[0]),dt(v[2]),dt(v[3])
        status,agency=v[1],v[5]
        ident=hashlib.sha256('|'.join([berth,navio,eta,etb]).encode()).hexdigest()[:16]
    if not navio: continue
    product=v[6].lstrip('*').strip()
    m=re.search(r'([\d.,\s]+)\s*(KG|LT)\b',v[7],re.I)
    if not product or product.upper().startswith('TOTAL NAVIO') or not m: continue
    qty=int(re.sub(r'\D','',m[1]))
    op=v[-1].upper()
    rows.append({'ID escala':ident,'Berço / especificação':berth,'ETA':eta,'ETB':etb,'ETS':ets,'Navio':navio,'Agência':agency,'Produto':product,'Quantidade':qty,'Unidade':m[2].upper(),'Status':status,'Observações':v[8],'Tipo Oper.':v[-1],'Tipo de Operação':'IMPORTAÇÃO' if 'IMPORTA' in op else 'EXPORTAÇÃO' if 'EXPORTA' in op else 'CABOTAGEM' if op=='CBD' else 'NÃO INFORMADO','Tipo Registro':'PROVISÓRIO' if product.upper()=='TBN' else 'CARGA','Nor/Não':'NÃO INFORMADO'})
if len(rows)<5 or len({x['Navio'] for x in rows})<3: raise ValueError('Extração incompleta')
p=Path('data/cattalini');p.mkdir(parents=True,exist_ok=True)
payload=json.dumps({'updated_at':now.isoformat(),'source':url,'rows':rows},ensure_ascii=False,indent=2)
(p/'history').mkdir(exist_ok=True)
(p/'history'/now.strftime('%Y%m%d_%H%M%S.json')).write_text(payload,encoding='utf-8')
tmp=p/'current.tmp';tmp.write_text(payload,encoding='utf-8');tmp.replace(p/'current.json')
