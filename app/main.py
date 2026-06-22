from __future__ import annotations

import base64
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .history import add_history_item, clear_history, load_history
from .links import load_links
from .openai_client import call_openai_image, call_openai_parse, call_openai_text
from .parser import parse_url


app = FastAPI(title="Конкурентный анализ", version="0.1.0")


class TextAnalysisRequest(BaseModel):
    text: str


class ParseRequest(BaseModel):
    url: str


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    html_path = Path(__file__).resolve().parent.parent / "static" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Static UI not found")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.post("/analyze_text")
async def analyze_text(request: TextAnalysisRequest) -> dict[str, str]:
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    result = call_openai_text(request.text)
    item = {
        "type": "text",
        "input": request.text,
        "output": result,
    }
    add_history_item(item)
    return {"result": result}


@app.post("/analyze_image")
async def analyze_image(description: str = Form(""), image: UploadFile = File(...)) -> dict[str, str]:
    content_type = image.content_type or ""
    if content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Only images are allowed")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    image_base64 = base64.b64encode(image_bytes).decode("ascii")
    result = call_openai_image(image_base64, mime_type=content_type)
    item = {
        "type": "image",
        "input": description or f"Uploaded image: {image.filename}",
        "filename": image.filename,
        "output": result,
    }
    add_history_item(item)
    return {"result": result}


@app.post("/parse_demo")
async def parse_demo(request: ParseRequest) -> dict[str, object]:
    if not request.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        parsed = await parse_url(request.url)
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Не удалось загрузить страницу: {error}")
    result = call_openai_parse(parsed)
    item = {
        "type": "parse",
        "input": request.url,
        "parsed": parsed,
        "output": result,
    }
    add_history_item(item)
    return {"parsed": parsed, "result": result}


@app.post("/analyze_links")
async def analyze_links() -> dict[str, object]:
    links = load_links()
    if not links:
        raise HTTPException(status_code=404, detail="No links found in data/Links.txt")

    analysis = []
    for url in links:
        try:
            parsed = await parse_url(url)
            result = call_openai_parse(parsed)
            result_json = None
            try:
                result_json = json.loads(result)
            except Exception:
                pass
            analysis.append({
                "url": url,
                "parsed": parsed,
                "result_text": result,
                "result_json": result_json,
            })
        except Exception as error:
            analysis.append({"url": url, "error": str(error)})

    add_history_item({
        "type": "links_batch",
        "input": "data/Links.txt",
        "output": f"Analyzed {len(links)} links",
    })

    return {"links": links, "analysis": analysis}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/history")
async def history() -> dict[str, list[dict[str, str]]]:
    return {"history": load_history()}


@app.delete("/history")
async def delete_history() -> dict[str, str]:
    clear_history()
    return {"status": "cleared"}


@app.get("/links")
async def links() -> dict[str, list[str]]:
    return {"links": load_links()}
