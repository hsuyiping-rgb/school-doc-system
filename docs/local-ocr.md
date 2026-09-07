# 本機 OCR 使用說明

這個專案提供一個本機免費 OCR 服務，用 Tesseract 辨識 PDF / 圖片，不需要把檔案送到 Gemini API。
同一個本機服務也負責 Groq API 轉送，避免瀏覽器直接呼叫 Groq 時遇到 CORS 問題。

> ⚠️ **目前狀態：後端服務可用，但 `index.html` 尚未接上。**
> `tools/local_ocr_server.py` 已可獨立運作（`/health`、`/ocr`、`/ai/groq` 皆實測通過），
> 但網頁端還沒有「呼叫本機 OCR」與「AI 供應商切換到 Groq」的介面，
> 所以下方「使用流程」與「Groq 撰稿」是**接上前端之後**的預期操作方式。
> 在那之前，可用 curl 或瀏覽器直接打本機服務測試。

## 第一次安裝

在專案根目錄執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\install_ocr_windows.ps1
```

安裝內容：

- Tesseract OCR
- Python PDF 渲染套件：pypdfium2
- 專案內的繁體中文語言包：`tools/tessdata/chi_tra.traineddata`

## 每次使用前啟動

在專案根目錄執行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\start_ocr_server.ps1
```

OCR 服務會在：

```text
http://localhost:8766
```

網頁仍使用原本的預覽網址：

```text
http://localhost:8765
```

## 使用流程（待前端接上後適用）

1. 啟動網頁預覽。
2. 啟動本機 OCR 服務。
3. 在網頁上傳 PDF、圖片或 TXT。
4. PDF / 圖片會在本機轉文字，不送到 Gemini。
5. Gemini 只保留給後續產生簽、函、擬辦內容。

## 健康檢查

開啟：

```text
http://localhost:8766/health
```

若看到 `tesseract: true` 和 `pypdfium2: true`，代表本機 OCR 可用。

直接測試辨識（不必等前端）：

```bash
curl -F "file=@來文.pdf;type=application/pdf" http://127.0.0.1:8766/ocr
curl -F "file=@來文.png;type=image/png" http://127.0.0.1:8766/ocr
```

## Groq 撰稿（待前端接上後適用）

1. 到 `https://console.groq.com/keys` 建立 Groq API Key。
2. 在系統的「設定」頁，把 AI 供應商切到 `Groq`。
3. 貼上 Groq API Key，選擇模型後儲存。
4. 撰稿時仍要保持本機服務 `http://localhost:8766` 開啟。

建議先用 `Qwen3 32B` 測試中文公文撰稿；若速度優先，可改用 `GPT-OSS 20B`。
