import re,json,html,urllib.request,concurrent.futures as cf,datetime
UA={"User-Agent":"Mozilla/5.0"}
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf8','ignore')
    except Exception as e: print('ERR',u,e); return ''
T=lambda s:html.unescape(re.sub(r'<[^>]+>','',s)).strip()
today=datetime.date.today()
yms=[(today.year+(today.month-1+i)//12,(today.month-1+i)%12+1) for i in (-1,0,1,2)]
items=[]
# Bandai
for y,m in yms:
    s=get(f"https://gashapon.jp/schedule/?ym={y}{m:02d}")
    if f'{y}.{m:02d}' not in s and f'{y}.{m}' not in s: continue
    for wk in re.split(r'<div class="pg-tit__week">',s)[1:]:
        lab=T(wk.split('<small')[0]); w=re.findall(r'第(\d)週',lab); key=f"{y}-{m:02d}-{w[0] if w else 9}"
        lab=re.sub(r'より順次','',lab)
        for c in re.findall(r'<a class="c-card__link" href="([^"]+)"[^>]*>(.*?)</a>',wk,re.S):
            h,b=c; n=re.search(r'c-card__name">(.*?)</p>',b,re.S); p=re.search(r'price--main">([\d,]+)',b)
            img=re.search(r'<img[^>]*src="([^"]+)"',b)
            st='再' if '再入荷' in b else ('限' if re.search(r'限定',b) else '新')
            items.append(dict(src='B',date=lab,key=key,name=T(n.group(1)) if n else '',price=int(p.group(1).replace(',','')) if p else 0,st=st,url='https://gashapon.jp/products/'+h.split('products/')[-1],img=img.group(1) if img else ''))
# Takara Tomy
for y,m in yms:
    s=get(f"https://www.takaratomy-arts.co.jp/items/gacha/calendar/?ym={y}{m:02d}")
    if f'<p class="year_month black">{y}.{m:02d}' not in s: continue
    for g in re.findall(r'<div class="group[^"]*">(?:<h3 class="black">(.*?)</h3>)?<div class="itemWrap">(.*?)</div></div>',s,re.S):
        lab=T(g[0]).replace('発売',''); d=re.findall(r'(\d+)日週',lab); w=(int(d[0])+6)//7 if d else 9
        lab=f"{m}月第{w}週" if d else f"{m}月（週未定）"
        for h,img,n in re.findall(r'<a href="([^"]+)"><div class="img"><img src="([^"]+)"[^>]*></div><p class="black">(.*?)</p>',g[1],re.S):
            items.append(dict(src='T',date=lab,key=f"{y}-{m:02d}-{w}",name=T(n),price=0,st='新',url='https://www.takaratomy-arts.co.jp/items/'+h.replace('../',''),img=img))
# Kitan
s=get("https://kitan.jp/product_category/newproduct/")
pairs=re.findall(r'<a href="(https://kitan.jp/products/[^"]+/)">\s*<figure class="c-productBox__thum"><img src="([^"]+)"',s)[:60]
def kit(p):
    u,img=p; t=get(u)
    n=re.search(r'<meta property="og:title" content="([^"]+)"',t); name=html.unescape(n.group(1)).split('|')[0].split('｜')[0].strip() if n else ''
    pr=re.search(r'(\d{3,4})\s*円',T(t)); dt=re.search(r'(\d{4})年\s*(\d{1,2})月\s*(上旬|中旬|下旬)?',T(t))
    if dt: y,m,j=int(dt.group(1)),int(dt.group(2)),dt.group(3) or ''; key=f"{y}-{m:02d}-{ {'上旬':1,'中旬':2,'下旬':3}.get(j,0)}"; lab=f"{m}月{j}"
    else: key,lab='0000','時期未定'
    return dict(src='K',date=lab,key=key,name=name,price=int(pr.group(1)) if pr else 0,st='新',url=u,img=img)
with cf.ThreadPoolExecutor(8) as ex: items+= [x for x in ex.map(kit,pairs) if x['name']]
# Gachanavi
s=get("https://gachanavi.com")
for u,b in re.findall(r'<a href="(https://gachanavi.com/item/[^"]+)" class="card(.*?)</a>',s,re.S):
    n=re.search(r'<h3[^>]*>(.*?)</h3>',b,re.S); p=re.search(r'¥([\d,]+)',b); d=re.search(r'(\d{4})年(\d{1,2})月',b); img=re.search(r'src="(https://image.gachanavi.com[^"]+)"',b)
    if not n: continue
    y,m=(int(d.group(1)),int(d.group(2))) if d else (0,0)
    items.append(dict(src='N',date=f"{y}年{m}月" if d else '時期未定',key=f"{y}-{m:02d}-0",name=T(n.group(1)),price=int(p.group(1).replace(',','')) if p else 0,st='新',url=u,img=html.unescape(img.group(1)) if img else ''))
# Gacha Island
def gi_page(u):
    t=get(u);out=[]
    for li in re.split(r'<li class="p-postList__item">',t)[1:]:
        h=re.search(r'href="(https://gacha-island.jp/\d+/)"',li); n=re.search(r'p-postList__title">(.*?)</h2>',li,re.S)
        if not(h and n): continue
        img=re.search(r'src="(https://gacha-island.jp/wp-content/uploads/[^"]+)"',li)
        d=re.search(r'<th>発売</th>\s*<td>\s*(\d{4})年(\d{1,2})月(?:(\d{1,2})日|(上旬|中旬|下旬))?',li)
        p=re.search(r'([\d,]+)円',li); mk=re.search(r'<th>メーカー</th>\s*<td>(.*?)</td>',li,re.S)
        name=T(n.group(1))
        if d:
            y,m=int(d.group(1)),int(d.group(2))
            if d.group(3): w=(int(d.group(3))+6)//7; lab=f"{m}月第{w}週"
            elif d.group(4): w={'上旬':1,'中旬':2,'下旬':4}[d.group(4)]; lab=f"{m}月{d.group(4)}"
            else: w=0; lab=f"{m}月"
            key=f"{y}-{m:02d}-{w}"
        else: key,lab='0000','時期未定'
        out.append(dict(src='I',date=lab,key=key,name=name,price=int(p.group(1).replace(',','')) if p else 0,st='再' if '再販' in name else '新',url=h.group(1),img=img.group(1) if img else '',mk=T(mk.group(1)) if mk else ''))
    pages=[int(x) for x in re.findall(r'/page/(\d+)/"',t)]
    return out,max(pages) if pages else 1
for y,m in yms:
    base=f"https://gacha-island.jp/gacha-release-schedule/release{y}{m:02d}/"
    first,last=gi_page(base);items+=first
    with cf.ThreadPoolExecutor(6) as ex:
        for o,_ in ex.map(gi_page,[f"{base}page/{i}/" for i in range(2,min(last,15)+1)]): items+=o
# dedupe by normalized name (prefer official makers)
seen={};order={'B':0,'T':0,'K':0,'I':1,'N':2}
norm=lambda x:re.sub(r'[\s　～~\-・]','',x)
for it in sorted(items,key=lambda x:order[x['src']]):
    k=norm(it['name'])
    if k and k not in seen: seen[k]=it
out=list(seen.values())
from collections import Counter;print(len(out),Counter(x['src'] for x in out))
json.dump(out,open('items.json','w'),ensure_ascii=False,indent=0)
