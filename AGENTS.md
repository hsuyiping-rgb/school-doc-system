# 學校公文擬辦提醒系統（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介

以**單一 `index.html`**（HTML + CSS + 原生 JavaScript，無框架、無建置流程）打造的零後端工具，結合 Google Gemini AI 產出符合公文格式的「簽／函稿／擬辦」，並提供辦理期限追蹤、承辦人催辦與 Google Sheets 雲端同步。

- 線上版：https://hsuyiping-rgb.github.io/school-doc-system/
- 前端：單一 `index.html`
- AI：Google Gemini（`gemini-2.5-flash`，使用者自備 API Key）；另有本機 OCR 方案（Tesseract）
- 儲存：瀏覽器 `localStorage`（本機）＋ Google Sheets（雲端，選用）
- 雲端橋接：Google Apps Script Web App（GET 參數溝通，設定頁可一鍵複製程式碼）
- 部署：GitHub Pages 靜態託管
- 後端版本代號：`v7-portable`（`curl ".../exec?action=version"` 可驗證）

## 關鍵時程

- 無固定截止日；依學校行政需求滾動開發。
- 每個上班日早上由 Apps Script 觸發器寄出承辦人催辦信。

## 目標與路線圖

- [x] 階段一：AI 撰稿（簽／函稿／擬辦）＋來文 OCR 解析
- [x] 階段二：公文追蹤（期限倒數、狀態）＋重複防治＋Google Sheets 同步
- [x] 階段三：處室分層與角色檢視、人員通訊錄、每日 Email 彙總提醒
- [x] 階段四：承辦人個別催辦（7 日內含逾期）、追蹤頁就地改承辦人、催辦信 CC 管理者
- [x] 階段五：打包通用版 `v7-portable`（他校可下載使用、試算表自動建立）
- [x] 階段六：函稿雙模式（關鍵字生成／優化潤飾）
- [x] 階段七：新學年度初始化 — 學年度設定、批次改派未結案公文、舊結案公文封存與檢視
- [x] 階段八：本機免費 OCR（Tesseract）＋ Groq API 轉送服務，並接上前端（僅本機版可用）
- [ ] 可考慮：追蹤頁「一鍵檢查哪些公文缺承辦人／承辦人不在通訊錄」檢核按鈕
- [ ] 可考慮：舊公文批次補承辦人的體驗優化

## 資料夾結構

```
行政公文系統/
├── index.html              # 主程式：HTML + CSS + 前端 JS + Apps Script 範本（單檔架構）
├── README.md               # 使用說明與部署說明
├── AGENTS.md               # 本檔（專案藍圖）
├── handoff.md              # 交接檔（每次收工必更新）
├── .gitignore              # 忽略 .claude/、*.gsheet、暫存圖片
├── docs/
│   ├── local-ocr.md        # 本機 OCR 使用說明（未 commit）
│   └── screenshots/        # README 使用的介面圖（compose.svg、tracker.svg）
└── tools/                  # 本機 OCR 服務（未 commit）
    ├── local_ocr_server.py     # OCR + Groq 轉送服務
    ├── install_ocr_windows.ps1 # 一次性安裝（Tesseract、pypdfium2、中文語言包）
    ├── start_ocr_server.ps1    # 每次使用前啟動
    └── tessdata/               # 繁中語言包
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `AGENTS.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | https://github.com/hsuyiping-rgb/school-doc-system （私有） | 指定時 |
| L3 | Obsidian | `行政公文系統/工作筆記.md` | 有需要時 |

## 啟動方式

在專案根目錄啟動本機伺服器（`.claude/launch.json` 已設定）：

```powershell
python -m http.server 8765
```

然後開啟 `http://localhost:8765`。

需要本機 OCR 時，另開一個視窗跑 `.\tools\start_ocr_server.ps1`（詳見 `docs/local-ocr.md`）。

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- 不要提交 Gemini／Groq API Key、Apps Script 部署網址、試算表捷徑或個人本機設定
- 修改 `index.html` 時，優先維持單檔架構，除非使用者明確要求拆分
- 調整介面時同時檢查桌面與手機寬度，避免按鈕或文字重疊
- 更新 README 截圖請放 `docs/screenshots/`，確認相對路徑在 GitHub Pages 仍可顯示

## 踩坑筆記（詳見 Obsidian 筆記）

- **Apps Script 更新**：走「部署 → 管理部署作業 → 編輯 → 新增版本」，網址才不變且新碼生效；按「新增部署作業」會產生新網址、舊網址仍跑舊碼。
- **Sheets 日期**：Sheets 會自動把日期轉時間戳；寫入時設純文字、讀取時還原民國日期。
- **長網址失敗**：上傳走 GET，content 過長會超出網址上限；已精簡並截斷 400 字。
- **瀏覽器快取**：更新後功能異常時按 Ctrl + Shift + R 強制重新整理。
