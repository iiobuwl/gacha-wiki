# 承認済みのユーザー報告をNotionから取り込む（NOTION_TOKEN が無ければ何もしない）
import os,json,urllib.request,datetime
TOKEN=os.environ.get("NOTION_TOKEN","").strip()
DS="9b3b56fb6b8e421690c61aaea633ef04"  # データベースID（2022-06-28 版APIで使う）
H={"Authorization":"Bearer "+TOKEN,"Notion-Version":"2022-06-28","Content-Type":"application/json"}
def req(method,url,body=None):
    r=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=H,method=method)
    return json.load(urllib.request.urlopen(r,timeout=30))
def txt(p):
    if not p:return ""
    arr=p.get("rich_text") or p.get("title") or []
    return "".join(x.get("plain_text","") for x in arr).strip()
def main():
    if not TOKEN:print("NOTION_TOKEN なし: スキップ");return []
    rows=[];cur=None
    while True:
        body={"filter":{"or":[{"property":"ステータス","select":{"equals":"承認"}},{"property":"ステータス","select":{"equals":"掲載済み"}}]},"page_size":100}
        if cur:body["start_cursor"]=cur
        r=req("POST",f"https://api.notion.com/v1/databases/{DS}/query",body)
        rows+=r["results"]
        if not r.get("has_more"):break
        cur=r["next_cursor"]
    out=[]
    for pg in rows:
        P=pg["properties"]
        name=txt(P.get("確定_商品名")) or txt(P.get("商品名")) or txt(P.get("ガチャの名前"))
        if not name:continue
        d=(P.get("確定_発売日",{}).get("date") or {}).get("start")
        if d:
            y,m,dd=map(int,d[:10].split("-"));w=(dd-1)//7+1
            date,key=f"{m}月第{w}週",f"{y}-{m:02d}-{w}"
        else: date,key="時期未定","0000"
        price=int(P.get("確定_価格",{}).get("number") or P.get("価格",{}).get("number") or 0)
        url=P.get("確定_公式URL",{}).get("url") or P.get("商品URL",{}).get("url") or ""
        mk=txt(P.get("確定_メーカー")) or txt(P.get("メーカー"))
        out.append(dict(src="U",date=date,key=key,name=name,price=price,st="新",url=url,mk=mk))
        if (P.get("ステータス",{}).get("select") or {}).get("name")=="承認":
            try:req("PATCH",f"https://api.notion.com/v1/pages/{pg['id']}",{"properties":{"ステータス":{"select":{"name":"掲載済み"}}}})
            except Exception as e:print("ステータス更新失敗",e)
    print("ユーザー報告",len(out),"件")
    return out
if __name__=="__main__":
    try:json.dump(main(),open("reports.json","w"),ensure_ascii=False)
    except Exception as e:
        print("Notion取り込み失敗:",e);json.dump([],open("reports.json","w"))
