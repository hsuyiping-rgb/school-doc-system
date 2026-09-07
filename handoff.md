# 交接檔（handoff.md）

> 任何 Agent、任何電腦接手前**必讀**；收工時**必更新**。本檔只放交接必需的精簡資訊，詳細脈絡放 Obsidian（`行政公文系統/工作筆記.md`）。

## ⏯️ 目前做到哪

2026-09-07 一整天把積壓近一個月的工作清完，並多做了兩件事。共 7 個 commit，全部已推上 `origin/master`（`c9002d0` → `129b856`）：

| commit | 內容 |
|---|---|
| `22b185b` | 本機免費 OCR 服務（Tesseract + Groq 轉送） |
| `8a02094` | 新學年度初始化（學年度設定、批次改派、舊案封存）＋系統更名 |
| `b0f66b2` | 修 `directoryData.find is not a function` |
| `26c0347` | 三層級初始化文件（`AGENTS.md` + 本檔） |
| `1f1d2f4` | 本機 OCR 接上前端 + AI 供應商可切 Gemini／Groq |
| `ed1fa34` | 交接檔更新 |
| `129b856` | 日期格式檢核與正規化 |

另外完成：**Apps Script 部署由 v6-officer-reminder 更新到 v7-portable**（第 13 版，網址未變），使用者已在線上版驗收通過——通訊錄載入 28 筆、產稿正常。

## 🚦 目前狀態

- 線上版（GitHub Pages）與 Apps Script 後端都是最新，已由使用者實測正常。
- 本地工作區乾淨，與 `origin/master` 同步。
- 後端實測：`version` = v7-portable、`info` 正常、`getDirectory` 28 筆、`getAll` 16 筆、`unknown action` 正確回 `status:'error'`。
- **本機 OCR 只能在本機版用**：線上版是 https，瀏覽器會擋下對 `http://localhost:8766` 的請求。線上版偵測不到會自動走 Gemini，不會壞。要用就同時開 8765（網頁）與 8766（OCR 服務）。
- **Groq 撰稿只驗證了轉送鏈路**（用假 key 收到 Groq 的錯誤回應），沒用真 key 跑過實際公文。

## ➡️ 下一步

1. **使用者手動刪除試算表裡的髒資料列**：`date` 為 `0115/06/25`、`org` 與 `subject` 皆為「（未填）」那一列。日期正規化只改本機，改不到 Sheets（Apps Script 沒有更新日期的 action）。刪完在系統按「從 Sheets 同步」即可一致。
2. 若日後發現 Sheets 還有多筆日期異常，再評估幫 Apps Script 加 `updateDate` action（要重新部署）。
3. 可考慮：追蹤頁「一鍵檢查哪些公文缺承辦人／承辦人不在通訊錄」的檢核按鈕。
4. 有 Groq API Key 後實測撰稿品質，中文公文建議先用 Qwen3 32B。

## ⚠️ 注意事項

- **Apps Script 更新一定要先貼新碼再建版本**。這次踩過：直接走「管理部署作業 → 編輯 → 新增版本」而沒先在編輯器貼上新碼，等於把舊碼再包一次，版本號變了、內容還是 v6。貼完先 Ctrl+F 搜 `v7-portable` 確認再建版本。
- 部署一律用「管理部署作業 → 編輯 → 新增版本」，按「新增部署作業」會換網址。
- `directoryData.find is not a function` 的**真正觸發點仍未確認**。共用網址在 v6 狀態下 `getDirectory` 本來就正常（回 28 筆），所以「後端不認得 getDirectory」解釋不通。`asArray` 防呆該留著；若再現，從當下的 `sheetsUrl` 與實際回應內容查起，`loadDirectory()` 收到非陣列會跳紅字可當診斷訊號。
- `tools/tessdata/`（約 28MB 語言包）與 `__pycache__/` 已進 `.gitignore`；換電腦跑 `tools/install_ocr_windows.ps1` 會自動下載。
- 不要提交 Gemini／Groq API Key 與 Apps Script 部署網址。
- 這台電腦是 `DESKTOP-31QBU95`；換電腦前確認 Google 雲端硬碟已同步完成。

## 🕐 最後更新

- 時間：2026-09-07 16:10
- 更新者：Claude Code @ DESKTOP-31QBU95
- Git push：待推（本次收工的文件更新）
