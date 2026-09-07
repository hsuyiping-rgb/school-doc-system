# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（`行政公文系統/工作筆記.md`）。

## ⏯️ 目前做到哪

清掉了積了近一個月的未 commit 工作，四個 commit 已推上 `origin/master`：

1. `22b185b` **本機免費 OCR 服務**（Tesseract + Groq 轉送，`tools/`）。修掉 `run_command` 在 Windows 用 cp950 解 Tesseract UTF-8 輸出導致 stdout 變 None、外顯為「OCR 沒有辨識到文字」的 bug。
2. `8a02094` **新學年度初始化**（學年度設定、批次改派未結案公文、舊學年度已結案封存），並統一系統名稱為「學校公文擬辦提醒系統」。
3. `b0f66b2` **修掉產稿時 `directoryData.find is not a function`**。根因是舊版 Apps Script 對不認得的 action 回 `{status:'ok', data:'unknown action'}`，前端把字串當陣列用。新增 `asArray()` 全面防呆。
4. `<本次文件 commit>` 三層級初始化文件（`AGENTS.md` 藍圖 + 本交接檔）。

## 🚦 目前狀態

- 前端功能都已實測（見各 commit 訊息的「實測」段），本地工作區乾淨、與 `origin/master` 同步。
- **本機 OCR 只完成後端**：`tools/local_ocr_server.py` 三個端點（`/health`、`/ocr`、`/ai/groq`）獨立實測通過，但 `index.html` 完全沒有呼叫它的程式碼，設定頁也沒有「AI 供應商切到 Groq」的介面。`docs/local-ocr.md` 已標註此限制。
- **線上版通訊錄仍載不進來**：前端已不會崩潰，但要真的載入資料，使用者必須重新部署 Apps Script。

## ➡️ 下一步

1. **使用者重新部署 Apps Script**（部署 → 管理部署作業 → **編輯 → 新增版本**，不要按「新增部署作業」），然後在線上版按「產稿」與「載入通訊錄」確認正常。
2. 決定要不要把本機 OCR 接上前端：需要在上傳來文時先打 `http://localhost:8766/ocr`（失敗再退回 Gemini），並在設定頁加 AI 供應商切換（Gemini／Groq）＋ Groq API Key 與模型欄位。
3. 可考慮：追蹤頁「一鍵檢查哪些公文缺承辦人／承辦人不在通訊錄」的檢核按鈕。

## ⚠️ 注意事項

- Apps Script 更新務必用「新增版本」，按「新增部署作業」會產生新網址、舊網址仍跑舊碼。
- `tools/tessdata/`（約 28MB 語言包）與 `__pycache__/` 已進 `.gitignore`；換電腦時跑 `tools/install_ocr_windows.ps1` 會自動下載語言包。
- 本機 OCR 服務跑在 8766，網頁預覽跑在 8765，兩個都要開才測得到 OCR。
- 不要提交 Gemini／Groq API Key 與 Apps Script 部署網址。
- 這台電腦是 `DESKTOP-31QBU95`；換電腦前確認 Google 雲端硬碟已同步完成。

## 🕐 最後更新

- 時間：2026-09-07 13:10
- 更新者：Claude Code @ DESKTOP-31QBU95
- Git push：✅ 已推（`origin/master`）
