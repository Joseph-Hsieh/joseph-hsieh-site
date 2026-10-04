# joseph-hsieh.com

謝文淵 Joseph Hsieh 的個人網站原始碼。繁中、簡中、英、日四語的靜態網站，由 Cloudflare Pages 自動建置與發布。

## 網站結構

| 網址 | 內容 |
|---|---|
| `/`、`/zh-hans/`、`/en/`、`/ja/` | 首頁（關於、服務、觀點、每週觀察、經歷、所屬機構、聯絡） |
| `/insights/`、`/en/insights/`、`/ja/insights/` | 觀點文章列表 |
| `/insights/<slug>/` | 每篇文章的獨立頁面 |
| `/news/` | 最新一週的每週觀察；過往週次在 `/news/<日期>/` |
| `/sitemap.xml`、`/robots.txt`、`/feed.xml`、`/llms.txt` | 搜尋引擎、RSS 與 AI 搜尋用檔案 |

## 怎麼修改內容

所有文字都在 `data/site.json`，網站會依這份檔案重新產生：

- **個人資料、服務、經歷、所屬機構**：`profile`、`services`、`career`、`orgs`
- **觀點文章**：`articles`。網站上的排列順序就是這份清單的順序（不依日期自動排序），首頁最多顯示 6 篇。每篇要有 `slug`（英文網址名稱）、`title`、`date`、`summary`、`body`（支援 `## 小標`、`**粗體**`、`- 清單`）。簡體中文版由 `build.py` 以 OpenCC（`vendor/opencc`）從繁體自動轉換，不需另外維護；英、日文版加 `_en`、`_ja` 欄位；有 `body_en`／`body_ja` 時會顯示完整譯文。
- **每週新聞**：`news.weeks`，最新一週放最前面，分類為 `impact`、`gvc`、`twvc`、`fo`。

改好推送到 GitHub 後，Cloudflare Pages 會在一兩分鐘內自動更新網站。新增或改文章標題後，執行 `python3 tools/make_images.py` 重新產生分享縮圖（需要 Pillow 與 Noto Sans CJK 字型）。

## Cloudflare Pages 設定

- Build command：`python3 build.py`
- Build output directory：`dist`
- 自訂網域：`joseph-hsieh.com`（另可加 `www.joseph-hsieh.com` 並轉址到主網域）

## 本機預覽

```
python3 build.py
cd dist && python3 -m http.server 8000
```
