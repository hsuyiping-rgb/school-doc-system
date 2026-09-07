# 本機 OCR 使用說明

這個專案提供一個本機免費 OCR 服務，用 Tesseract 辨識 PDF / 圖片，不需要把檔案送到 Gemini API。
同一個本機服務也負責 Groq API 轉送，避免瀏覽器直接呼叫 Groq 時遇到 CORS 問題。

> ⚠️ **只有本機版（`http://localhost:8765`）能用。**
> 線上版是 https，瀏覽器會擋下 https 頁面呼叫 `http://localhost` 的請求。
> 線上版偵測不到本機服務時會自動退回 Gemini，不會壞掉，但也不會走本機 OCR。

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

## 使用流程

1. 啟動網頁預覽（`http://localhost:8765`）。
2. 啟動本機 OCR 服務（`http://localhost:8766`）。
3. 在網頁上傳 PDF、圖片或 TXT。
4. 系統會先探測本機服務：探測得到就在本機轉文字，檔名旁會顯示「已在本機辨識，未上傳雲端」，
   辨識結果同時填進「來文內容」框。
5. 之後的欄位解析與產稿只送這段文字，原始 PDF / 圖片不會外送。
6. 本機服務沒開、或辨識失敗時，會自動退回原本的 Gemini Vision（檔名旁會標示改用雲端）。

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

## Groq 撰稿

1. 到 `https://console.groq.com/keys` 建立 Groq API Key。
2. 在「⚙️ 設定」頁的「🖥️ 本機 OCR 與 AI 供應商」，把「撰稿使用的 AI」切到 `Groq`。
3. 貼上 Groq API Key，選擇模型後按「儲存」。
4. 撰稿時要保持本機服務開啟——瀏覽器直接呼叫 Groq 會被 CORS 擋下，一律經本機服務轉送。

Groq 沒有讀圖能力，所以用 Groq 時本機 OCR 是必要條件：上傳 PDF / 圖片而本機服務沒開，
系統會直接提示，不會把檔案送出去。

建議先用 `Qwen3 32B` 測試中文公文撰稿；若速度優先，可改用 `GPT-OSS 20B`。
