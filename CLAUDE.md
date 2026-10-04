# ガチャwiki 開発メモ（Claude向け）

ガチャ（カプセルトイ）の新作・再入荷を一覧できるサイト。GitHub Pagesで公開し、毎朝 GitHub Actions がデータを更新する。

## 構成
- index.html … 公開ページ。build.py が自動生成するので直接編集しない
- scripts/template.html … ページの元。見た目・機能の変更はここ。`__DATA__` と `__DATE__` は build.py が置き換える
- scripts/scrape.py … 5サイト（ガシャポン公式・タカラトミーアーツ・キタンクラブ・ガチャガチャアイランド・ガチャナビ）から取得し items.json を作る
- scripts/notion.py … Notion「ガチャ未掲載報告」のうちステータス「承認」「掲載済み」を reports.json に取り込み、「承認」を「掲載済み」に変える。NOTION_TOKEN が無ければスキップ
- scripts/build.py … items.json（直近62日以降）と reports.json を template.html に流し込み index.html を書き出す。取得が100件未満なら中止
- .github/workflows/update.yml … 毎朝5:52（日本時間）に上の3つを実行して index.html をコミット

## データ形式
DATA の各行: [src, 表示用時期, 並び替えキー(YYYY-MM-W), 商品名, 価格, 区分(新/再/限), URL, サムネ(常に空), メーカー]
src: B=バンダイ T=タカラトミーアーツ K=キタンクラブ I=ガチャガチャアイランド N=ガチャナビ U=ユーザー報告

## 守るルール
- 商品画像は著作権のため載せない（サムネは常に空）
- お気に入り・ゲット・設定は localStorage に保存。キーは「src|商品名」なので毎朝の更新で消えない。既存の保存キー名（gacha-*）は変えない
- 見出しやカードのアニメーションはページを開いたときだけ。ボタン操作で再生しない
- 起動アニメーション（カプセルが降って画面を埋める）→使い方ダイアログ（「次回から表示しない」あり）の順
- ライト/ダーク両対応。ダークで白が浮かないこと。prefers-reduced-motion ではアニメーションを止める
- スマホ幅（390px）で横にはみ出さないこと
- 報告フォーム: https://battle-lightning-659.notion.site/65eeda23bf374ceca2c919c3915fc846?pvs=105
- 文章にアスタリスクを使わない

## 変更後の確認
template.html を変えたら `python scripts/build.py`（items.json が必要なら先に `python scripts/scrape.py`）で index.html を作り、ブラウザで表示とエラーを確認する。index.html の再生成はコミットしてよい。
