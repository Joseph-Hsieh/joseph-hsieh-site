# 每週觀察：更新流程

每週一由排程任務自動執行，也可以手動照這份流程做。

## 1. 蒐集新聞

找出**過去 7 天內**發布的新聞，**四個分類各 7 到 9 則**（每週合計約 28 到 36 則）：

| 分類 key | 名稱 | 優先來源（可補充其他可信媒體） |
|---|---|---|
| `impact` | 全球影響力投資 | ImpactAlpha、GIIN、Devex、AVPN、Responsible Investor、GSG Impact |
| `gvc` | 全球創業投資 | Crunchbase News、TechCrunch、PitchBook News、Reuters、Bloomberg |
| `twvc` | 台灣創投 | Meet創業小聚、數位時代、經濟日報、工商時報、TechOrange、國發會／國發基金新聞稿 |
| `fo` | 家族辦公室 | Campden FB、WealthBriefing、Bloomberg、Citi / UBS 等家辦報告、港星金管局新聞稿 |

選題原則：
- 優先選有具體數字、制度變化或亞洲角度的新聞；台灣與亞洲相關的消息優先。
- 不收錄純行銷稿、轉載或未經證實的傳聞；同一件事只收一則。
- 已在前幾週刊登過的連結，`tools/add_week.py` 會自動略過。
- 過往週次一律保留、不刪除，網站的每週觀察頁可用關鍵字查詢全部歷史新聞；任一分類超過 9 則時 `add_week.py` 會拒絕寫入，不足 7 則會提出警告。

## 2. 撰寫摘要

每則需要：`title_zh`、`title_en`、`title_ja`、`sum_zh`、`sum_en`、`sum_ja`、`source`、`date`（YYYY-MM-DD）、`url`；英文原文另加 `vocab`（見下）。

- 摘要用自己的話改寫，不直接引用原文句子；中文約 60 到 100 字，英、日文長度相當。
- 每則摘要要點出「發生什麼事＋關鍵數字＋為什麼重要」。
- 用繁體中文與台灣用語；日文用敬體以外的一般新聞文體。
- 數字、機構名稱、日期要與原文一致；不確定的內容寧可不寫。

### 學習單字（vocab，選填）

原文為英文的新聞，另加 `vocab` 欄位：剛好 3 個值得學習的英文單字或片語，網站會在該則摘要下方顯示「學習單字／Vocabulary／学習語彙」小框。

```json
"vocab": [
  {"term": "dry powder", "zh": "尚未投入的可投資資金", "ja": "未投資の待機資金", "en": "committed capital not yet invested"},
  ...共 3 個
]
```

- `term` 必須是原文中**逐字出現**的字詞（閱讀原文時挑選）；`zh` 用繁體中文台灣用語，`ja` 用自然的商務日文，`en` 是簡短的英文解釋。
- 優先選商業／投資慣用語、搭配詞與產業術語，對台灣投資專業人士有用；不選人名、機構名或數字；同一週內不重複。
- 原文為中文或日文、或因付費牆／封鎖無法開啟原文的新聞，不加 `vocab`。
- `tools/add_week.py` 會驗證：若有 `vocab`，必須是 3 個物件，且每個都有非空的 term／zh／ja／en。
- 中文頁顯示中文解釋、日文頁顯示日文、英文頁顯示英文；沒有 `vocab` 的新聞顯示方式不變。

## 3. 加入網站並發布

```
python3 tools/add_week.py week.json   # 驗證並加入 data/site.json
python3 build.py                      # 重新產生 dist/
git add -A && git commit -m "Weekly brief: 2026-10-05" && git push
```

`week` 用當週星期一的日期，`label` 用「2026 年 10 月第 1 週」的格式。推送後 Cloudflare 會在一兩分鐘內自動更新網站。
