# ガチャwiki

ガチャの新作・再入荷をまとめて見られるサイトです。データは毎朝自動で更新されます。

- 公開: GitHub Pages（Settings → Pages → main / root）
- 自動更新: Actions「毎朝のデータ更新」（手動実行は Run workflow）
- 報告の取り込み: リポジトリの Secrets に NOTION_TOKEN を登録すると有効になります

開発の進め方: VS Code の Claude で scripts/template.html などを編集 → Sourcetree でコミット・プッシュ → 数分で公開ページに反映。
