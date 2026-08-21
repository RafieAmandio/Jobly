import io

import pdfplumber
from docx import Document

PDF_MIME_TYPE = "application/pdf"
DOCX_MIME_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
SUPPORTED_CV_MIME_TYPES = {PDF_MIME_TYPE, DOCX_MIME_TYPE}


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_docx(docx_bytes: bytes) -> str:
    doc = Document(io.BytesIO(docx_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_upload(file_bytes: bytes, mime_type: str) -> str:
    if mime_type == PDF_MIME_TYPE:
        return extract_text_from_pdf(file_bytes)
    if mime_type == DOCX_MIME_TYPE:
        return extract_text_from_docx(file_bytes)
    raise ValueError(f"Unsupported CV upload mime type: {mime_type}")
