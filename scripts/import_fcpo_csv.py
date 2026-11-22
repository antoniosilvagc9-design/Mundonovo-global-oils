#!/usr/bin/env python3
"""Offline validation of Bursa Malaysia FCPO derivative statistics CSV files."""
import argparse,csv,datetime as dt,json
from decimal import Decimal
from pathlib import Path

REQUIRED={'day_id','prod_id','contract_month','set_price','previous','change','volume','open_interest'}
BASE='https://www.bursamalaysia.com/misc/missftp/derivative/derivative_trading_statistic_'
def parse(path):
    path=Path(path)
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,delimiter='|')
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError('Colunas ausentes: '+path.name)
        records=[]
        for r in reader:
            if r['prod_id'].strip()!='FCPO': continue
            day=dt.date.fromisoformat(r['day_id'].strip()).isoformat()
            month=r['contract_month'].strip()
            if len(month)!=6 or not month.isdigit() or not 1<=int(month[-2:])<=12:
                raise ValueError('Vencimento inválido')
            price=Decimal(r['set_price']); previous=Decimal(r['previous'])
            volume=int(r['volume']); oi=Decimal(r['open_interest'])
            if not (1000<price<15000 and previous>0 and volume>=0 and oi>=0):
                raise ValueError('Preço/volume inválido')
            records.append({'date':day,'contract_month':month,'settlement_myr_per_tonne':float(price),
              'previous_myr_per_tonne':float(previous),'change_myr_per_tonne':float(Decimal(r['change'])),
              'volume':volume,'open_interest':float(oi)})
    if not records:raise ValueError('Nenhum FCPO')
    dates={r['date'] for r in records}
    if len(dates)!=1:raise ValueError('Datas diferentes no CSV')
    day=next(iter(dates))
    # Downloaders may append a numeric copy suffix, e.g. ' (1)', to the official filename.
    # Preserve the date check for canonical filenames while accepting such copies.
    import re
    match=re.fullmatch(r'derivative_trading_statistic_(\d{8})(?: \(\d+\))?\.csv',path.name)
    if match and match.group(1)!=day.replace('-',''):
        raise ValueError('Data no nome difere da data no CSV')
    traded=[r for r in records if r['volume']>0]
    if not traded:raise ValueError('Sem contratos negociados')
    selected=max(traded,key=lambda r:(r['volume'],r['open_interest'],r['contract_month']))
    return {'date':day,'source_file':path.name,'source_url':BASE+day.replace('-','')+'.csv',
      'selected':selected,'total_fcpo_volume':sum(r['volume'] for r in records),'contracts_count':len(records)}
def build(paths, existing=None):
    records={}
    if existing and Path(existing).is_file():
        old=json.loads(Path(existing).read_text(encoding='utf-8'))
        if old.get('instrument')!='FCPO' or old.get('contract_policy')!='highest_daily_volume':
            raise ValueError('Histórico existente incompatível')
        for item in old.get('observations',[]):
            if item.get('date') and item.get('selected',{}).get('settlement_myr_per_tonne',0)>0:
                records[item['date']]=item
    for p in paths:
        x=parse(p)
        if x['date'] in records and records[x['date']]['selected']!=x['selected']:
            raise ValueError('Conflito entre dados existentes e CSV para '+x['date'])
        records[x['date']]=x
    ordered=[records[k] for k in sorted(records)]
    latest=ordered[-1];three=ordered[-3:]
    target=dt.date.fromisoformat(latest['date'])-dt.timedelta(days=30)
    previous=[r for r in ordered if dt.date.fromisoformat(r['date'])<=target]
    baseline=previous[-1] if previous else None
    return {'instrument':'FCPO','market':'Bursa Malaysia Derivatives','currency':'MYR','unit':'metric_tonne',
      'price_type':'official_settlement','contract_policy':'highest_daily_volume',
      'data_status':'complete' if len(three)==3 and baseline else 'partial_history',
      'latest':latest,'last_three':three,
      'three_day_average':round(sum(r['selected']['settlement_myr_per_tonne'] for r in three)/3,4) if len(three)==3 else None,
      'reference_30d':{'target_date':target.isoformat(),'session':baseline},
      'observations':ordered,
      'note':'Rolling most-liquid contract: changes of contract may affect comparisons. Offline import only.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('files',nargs='+');ap.add_argument('--output')
    ap.add_argument('--existing');args=ap.parse_args();out=build(args.files,args.existing)
    if args.output:
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Validated',len(out['observations']),'days; status',out['data_status'])
    else:print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
