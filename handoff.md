# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（`行政公文系統/工作筆記.md`）。

## ⏯️ 目前做到哪

清掉了積了近一個月的未 commit 工作，四個 commit 已推上 `origin/master`：

1. `22b185b` **本機免費 OCR 服務**（Tesseract + Groq 轉送，`tools/`）。修掉 `run_command` 在 Windows 用 cp950 解 Tesseract UTF-8 輸出導致 stdout 變 None、外顯為「OCR 沒有辨識到文字」的 bug。
2. `8a02094` **新學年度初始化**（學年度設定、批次改派未結案公文、舊學年度已結案封存），並統一系統名稱為「學校公文擬辦提醒系統」。
3. `b0f66b2` **修掉產稿時 `directoryData.find is not a function`**。根因是舊版 Apps Script 對不認得的 action 回 `{status:'ok', data:'unknown action'}`，前端把字串當陣列用。新增 `asArray()` 全面防呆。
4. `26c0347` 三層級初始化文件（`AGENTS.md` 藍圖 + 本交接檔）。
5. `1f1d2f4` **本機 OCR 接上前端**：上傳來文先探測本機服務，探測得到就在本機轉文字（原始 PDF／圖片不外送），探測不到自動退回 Gemini；設定頁新增「本機 OCR 與 AI 供應商」卡片，可切 Gemini／Groq。

另外已完成（非 commit）：**Apps Script 部署由 v6-officer-reminder 更新到 v7-portable**（2026-09-07，第 13 版，網址未變）。

## 🚦 目前狀態

- 前端功能都已實測（見各 commit 訊息的「實測」段），本地工作區乾淨、與 `origin/master` 同步。
- **本機 OCR 只能在本機版用**：線上版是 https，瀏覽器會擋下對 `http://localhost:8766` 的請求；線上版偵測不到就自動走 Gemini，不會壞。要用本機 OCR 就開 8765 + 8766 跑本機版。
- **後端已是 v7-portable**，實測 `version`／`info`／`getDirectory`(28 筆)／`getAll`(16 筆) 全正常，`unknown action` 也已正確回 `status:'error'`。
- **`directoryData.find is not a function` 的真正觸發點仍未確認**：共用網址在 v6 狀態下 `getDirectory` 就是正常的（回 28 筆），所以「後端不認得 getDirectory」解釋不通。防呆修正（`asArray`）該留著，但若日後再現，要從使用者當下的 `sheetsUrl` 與實際回應內容查起。現在 `loadDirectory()` 收到非陣列會跳紅字提示，可當診斷訊號。

## ➡️ 下一步

1. **等使用者回報線上版驗收結果**：Ctrl+Shift+R 強制重新整理後，設定頁「載入通訊錄」應顯示 28 筆、撰稿頁「產稿」不再報錯。
2. 試算表資料清理：追蹤表第 3 列 `date` 是 `0115/06/25`（民國年多一個 0），`org`／`subject` 皆為「（未填）」，疑似早期解析失敗殘留。可考慮在前端加日期格式檢核。
3. 可考慮：追蹤頁「一鍵檢查哪些公文缺承辦人／承辦人不在通訊錄」的檢核按鈕。
4. 可考慮：Groq 撰稿的實際品質尚未用真 key 測過（目前只驗證轉送鏈路通）。

## ⚠️ 注意事項

- Apps Script 更新務必用「新增版本」，按「新增部署作業」會產生新網址、舊網址仍跑舊碼。
- `tools/tessdata/`（約 28MB 語言包）與 `__pycache__/` 已進 `.gitignore`；換電腦時跑 `tools/install_ocr_windows.ps1` 會自動下載語言包。
- 本機 OCR 服務跑在 8766，網頁預覽跑在 8765，兩個都要開才測得到 OCR。
- 不要提交 Gemini／Groq API Key 與 Apps Script 部署網址。
- 這台電腦是 `DESKTOP-31QBU95`；換電腦前確認 Google 雲端硬碟已同步完成。

## 🕐 最後更新

- 時間：2026-09-07 15:10
- 更新者：Claude Code @ DESKTOP-31QBU95
- Git push：✅ 已推（`origin/master`）
