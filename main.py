import base64
import io
import os
from typing import Optional

import fitz  # PyMuPDF
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="pdf-text-extractor", version="1.0.0")

MAX_PDF_BYTES = int(os.getenv("MAX_PDF_BYTES", str(20 * 1024 * 1024)))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", str(300_000)))


class ExtractRequest(BaseModel):
    file_name: Optional[str] = Field(default="document.pdf")
    pdf_base64: str = Field(..., description="PDF file encoded as base64")


class ExtractResponse(BaseModel):
    ok: bool
    file_name: Optional[str]
    method: str
    num_pages: int
    text: str
    text_length: int
    truncated: bool


@app.get("/health")
def health():
    return {"ok": True, "service": "pdf-text-extractor"}


@app.post("/extract-pdf-text", response_model=ExtractResponse)
def extract_pdf_text(payload: ExtractRequest):
    pdf_bytes = _decode_pdf(payload.pdf_base64)

    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail=f"PDF too large. Max bytes: {MAX_PDF_BYTES}")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")

    try:
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        text = "\n".join(pages)
    finally:
        doc.close()

    truncated = False
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]
        truncated = True

    return ExtractResponse(
        ok=True,
        file_name=payload.file_name,
        method="native_pdf_text_pymupdf",
        num_pages=len(pages),
        text=text,
        text_length=len(text),
        truncated=truncated,
    )


def _decode_pdf(pdf_base64: str) -> bytes:
    try:
        return base64.b64decode(pdf_base64, validate=True)
    except Exception:
        # Accept data URL format too
        if "," in pdf_base64:
            try:
                return base64.b64decode(pdf_base64.split(",", 1)[1], validate=True)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 PDF payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid base64 PDF payload")
