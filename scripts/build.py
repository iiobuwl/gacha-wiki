import json,re,datetime,os
JST=datetime.timezone(datetime.timedelta(hours=9));today=datetime.datetime.now(JST).date()
cut=(today-datetime.timedelta(days=62)).strftime('%Y-%m')
items=[x for x in json.load(open('items.json')) if x['key']>=cut]
if len(items)<100: raise SystemExit(f"取得件数が少なすぎます({len(items)}件)。サイト構造の変化の可能性があるため更新を中止します。")
norm=lambda s:re.sub(r'[\s　～~\-・]','',s).lower()
seen={norm(x['name']) for x in items}
if os.path.exists('reports.json'):
    for r in json.load(open('reports.json')):
        if norm(r['name']) not in seen: items.append(r);seen.add(norm(r['name']))
rows=[[x['src'],x['date'],x['key'],x['name'],x['price'],x['st'],x['url'],'',x.get('mk','')] for x in items]
t=open('scripts/template.html',encoding='utf8').read()
t=t.replace('__DATA__',json.dumps(rows,ensure_ascii=False,separators=(',',':'))).replace('__DATE__',f'（{today.year}年{today.month}月{today.day}日時点）')
open('index.html','w',encoding='utf8').write(t)
print('書き出し',len(rows),'件')
