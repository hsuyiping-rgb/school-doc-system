#!/usr/bin/env python3
"""Local OCR bridge for the school document system.

The browser cannot directly call installed desktop OCR tools, so this tiny
localhost service receives a file upload and delegates OCR to free tools:

- PDF: pypdfium2 renders pages, then Tesseract performs OCR.
- Images: Tesseract directly.
- TXT: decoded locally.
"""

from __future__ import annotations

import json
import importlib.util
import mimetypes
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8766
LANG = os.environ.get("OCR_LANG", "chi_tra+eng")
DEFAULT_TESSDATA_DIR = Path(__file__).resolve().parent / "tessdata"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def add_common_tool_paths() -> None:
    program_files = [
        os.environ.get("ProgramFiles", ""),
        os.environ.get("ProgramW6432", ""),
        r"C:\Program Files",
    ]
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python314" / "Scripts",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python313" / "Scripts",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "Scripts",
    ]
    for root in program_files:
        if root:
            candidates.append(Path(root) / "Tesseract-OCR")
    existing = [str(path) for path in candidates if path.exists()]
    if existing:
        os.environ["PATH"] = os.pathsep.join(existing + [os.environ.get("PATH", "")])


class OcrError(RuntimeError):
    pass


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def decode_text(data: bytes) -> str:
    if not data:
        return ""
    for encoding in ("utf-8-sig", "utf-8", "cp950", "big5", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def require_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise OcrError(f"找不到 {name}，請先執行 tools/install_ocr_windows.ps1 安裝免費 OCR 工具。")
    return path


def run_command(args: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    try:
        # Tesseract 以 UTF-8 輸出中文；Windows 的 text=True 預設走 cp950，
        # 會在讀取時丟 UnicodeDecodeError 使 stdout 變成 None，故明確指定編碼。
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.CalledProcessError as exc:
        detail = safe_strip(exc.stderr or exc.stdout)
        raise OcrError(detail or f"{args[0]} 執行失敗。") from exc
    except subprocess.TimeoutExpired as exc:
        raise OcrError("OCR 處理逾時，請先確認 PDF 頁數或掃描品質。") from exc


def safe_strip(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def extract_pdf_text_layer(input_path: Path) -> str:
    """Read embedded/selectable PDF text before falling back to image OCR."""
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        return ""

    try:
        text = extract_text(str(input_path))
    except Exception:
        return ""

    return safe_strip(text)


def ocr_pdf(input_path: Path, work_dir: Path) -> str:
    text_layer = extract_pdf_text_layer(input_path)
    if text_layer:
        return text_layer

    require_command("tesseract")
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise OcrError("找不到 pypdfium2，請先執行 python -m pip install pypdfium2。") from exc

    pdf = pdfium.PdfDocument(str(input_path))
    page_count = len(pdf)
    if page_count == 0:
        raise OcrError("PDF 沒有可辨識的頁面。")

    chunks: list[str] = []
    try:
        for index in range(page_count):
            page = pdf[index]
            try:
                bitmap = page.render(scale=4)
                image = bitmap.to_pil()
                if image.mode != "RGB":
                    image = image.convert("RGB")
                image_path = work_dir / f"page-{index + 1}.png"
                image.save(image_path)
                page_text = ocr_image(image_path)
                if page_text:
                    chunks.append(page_text)
            finally:
                close = getattr(page, "close", None)
                if callable(close):
                    close()
    finally:
        close = getattr(pdf, "close", None)
        if callable(close):
            close()

    text = safe_strip("\n\n".join(chunk for chunk in chunks if chunk))
    if not text:
        raise OcrError("OCR 沒有辨識到文字，請確認 PDF 是否清晰，或改用較高解析度掃描。")
    return text


def ocr_image(input_path: Path) -> str:
    require_command("tesseract")
    args = ["tesseract", str(input_path), "stdout", "-l", LANG]
    tessdata_dir = Path(os.environ.get("TESSDATA_PREFIX", "")) if os.environ.get("TESSDATA_PREFIX") else DEFAULT_TESSDATA_DIR
    if tessdata_dir.exists():
        args.extend(["--tessdata-dir", str(tessdata_dir)])
    result = run_command(args, timeout=180)
    return safe_strip(result.stdout)


def extract_text(filename: str, content_type: str, data: bytes, work_dir: Path) -> str:
    filename = filename or "upload"
    content_type = content_type or ""
    data = data or b""
    suffix = Path(filename).suffix.lower()
    if not suffix:
        suffix = mimetypes.guess_extension(content_type or "") or ".bin"

    input_path = work_dir / f"upload{suffix}"
    input_path.write_bytes(data)

    if suffix == ".txt" or content_type.startswith("text/"):
        text = safe_strip(decode_text(data))
        if not text:
            raise OcrError("文字檔沒有可讀取的內容。")
        return text
    if suffix == ".pdf" or content_type == "application/pdf":
        return ocr_pdf(input_path, work_dir)
    if suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"} or content_type.startswith("image/"):
        text = ocr_image(input_path)
        if not text:
            raise OcrError("OCR 沒有辨識到文字，請確認圖片是否清晰，或改用較高解析度掃描。")
        return text

    raise OcrError("目前只支援 PDF、圖片與 TXT 檔。")


def parse_multipart(body: bytes, content_type: str) -> tuple[str, str, bytes]:
    message = BytesParser(policy=policy.default).parsebytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n"
        b"MIME-Version: 1.0\r\n\r\n"
        + body
    )
    if not message.is_multipart():
        raise OcrError("上傳格式錯誤。")

    for part in message.iter_parts():
        disposition = part.get_content_disposition()
        if disposition != "form-data":
            continue
        if part.get_param("name", header="content-disposition") != "file":
            continue
        filename = part.get_filename() or "upload"
        payload = part.get_payload(decode=True) or b""
        return filename, part.get_content_type() or "", payload

    raise OcrError("沒有收到檔案。")


def read_json_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length)
    if not body:
        return {}
    try:
        return json.loads(body.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise OcrError("請求編碼錯誤，請確認送出的 JSON 為 UTF-8。") from exc
    except json.JSONDecodeError as exc:
        raise OcrError("JSON 格式錯誤。") from exc


def call_groq(api_key: str, model: str, prompt: str) -> str:
    api_key = safe_strip(api_key)
    model = safe_strip(model) or "qwen/qwen3-32b"
    prompt = safe_strip(prompt)

    if not api_key:
        raise OcrError("缺少 Groq API Key。")
    if not prompt:
        raise OcrError("缺少撰稿內容。")

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "你是台灣國民小學行政公文撰稿助理，請使用繁體中文，格式務必清楚、正式、可直接交給學校行政人員修訂。",
            },
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        GROQ_API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            message = parsed.get("error", {}).get("message") or detail
        except json.JSONDecodeError:
            message = detail
        raise OcrError(f"Groq API 錯誤：{message}") from exc
    except urllib.error.URLError as exc:
        raise OcrError(f"無法連線到 Groq API：{exc.reason}") from exc

    parsed = json.loads(raw)
    return safe_strip(parsed.get("choices", [{}])[0].get("message", {}).get("content"))


class Handler(BaseHTTPRequestHandler):
    server_version = "LocalOCR/1.0"

    def log_message(self, format: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), format % args))

    def send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_json(200, {"ok": True})

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            self.send_json(
                200,
                {
                    "ok": True,
                    "lang": LANG,
                    "tesseract": bool(shutil.which("tesseract")),
                    "tessdata_dir": str(DEFAULT_TESSDATA_DIR),
                    "chi_tra": (DEFAULT_TESSDATA_DIR / "chi_tra.traineddata").exists(),
                    "pypdfium2": _has_module("pypdfium2"),
                },
            )
            return
        self.send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/ai/groq":
            try:
                payload = read_json_body(self)
                text = call_groq(
                    payload.get("apiKey", ""),
                    payload.get("model", ""),
                    payload.get("prompt", ""),
                )
                self.send_json(200, {"ok": True, "text": text})
            except OcrError as exc:
                self.send_json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:
                self.send_json(500, {"ok": False, "error": f"Groq 轉送服務發生錯誤：{exc}"})
            return

        if path != "/ocr":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            content_type = self.headers.get("Content-Type", "")
            body = self.rfile.read(length)
            filename, part_type, data = parse_multipart(body, content_type)
            with tempfile.TemporaryDirectory(prefix="school-doc-ocr-") as temp:
                text = extract_text(filename, part_type, data, Path(temp))
            self.send_json(200, {"ok": True, "filename": filename, "text": text})
        except OcrError as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # Keep browser errors readable.
            self.send_json(500, {"ok": False, "error": f"OCR 服務發生錯誤：{exc}"})


def main() -> None:
    add_common_tool_paths()
    print(f"Local OCR server listening at http://{HOST}:{PORT}")
    print(f"OCR language: {LANG}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
