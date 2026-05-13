import io
import logging
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def generate_cv_docx(data: dict, full_name: str) -> bytes:
    doc = Document()

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    heading = doc.add_heading(full_name, level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    if data.get("summary"):
        doc.add_heading("Professional Summary", level=2)
        doc.add_paragraph(data["summary"])

    if data.get("experience"):
        doc.add_heading("Experience", level=2)
        for exp in data["experience"]:
            p = doc.add_paragraph()
            run = p.add_run(f"{exp.get('title', '')} — {exp.get('company', '')}")
            run.bold = True
            run.font.size = Pt(12)
            p.add_run(f"\n{exp.get('period', '')}")
            for bullet in exp.get("bullets", []):
                doc.add_paragraph(bullet, style="List Bullet")

    if data.get("skills"):
        doc.add_heading("Skills", level=2)
        doc.add_paragraph(", ".join(data["skills"]))

    if data.get("education"):
        doc.add_heading("Education", level=2)
        for edu in data["education"]:
            p = doc.add_paragraph()
            run = p.add_run(f"{edu.get('degree', '')} — {edu.get('institution', '')}")
            run.bold = True
            if edu.get("year"):
                p.add_run(f" ({edu['year']})")

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def generate_cover_letter_docx(content: str, full_name: str) -> bytes:
    doc = Document()

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    for paragraph in content.split("\n\n"):
        paragraph = paragraph.strip()
        if paragraph:
            doc.add_paragraph(paragraph)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def generate_cv_pdf(data: dict, full_name: str) -> bytes | None:
    try:
        from weasyprint import HTML

        html_parts = [
            "<html><head><style>",
            "body { font-family: Calibri, Arial, sans-serif; font-size: 11pt; margin: 40px; color: #333; }",
            "h1 { text-align: center; color: #2C3E50; margin-bottom: 5px; }",
            "h2 { color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 5px; margin-top: 20px; }",
            ".exp-header { font-weight: bold; font-size: 12pt; margin-bottom: 2px; }",
            ".exp-period { color: #666; margin-bottom: 8px; }",
            "ul { margin-top: 5px; }",
            "li { margin-bottom: 3px; }",
            ".skills { line-height: 1.6; }",
            "</style></head><body>",
            f"<h1>{full_name}</h1>",
        ]

        if data.get("summary"):
            html_parts.append("<h2>Professional Summary</h2>")
            html_parts.append(f"<p>{data['summary']}</p>")

        if data.get("experience"):
            html_parts.append("<h2>Experience</h2>")
            for exp in data["experience"]:
                html_parts.append(
                    f"<p class='exp-header'>{exp.get('title', '')} — {exp.get('company', '')}</p>"
                )
                html_parts.append(f"<p class='exp-period'>{exp.get('period', '')}</p>")
                html_parts.append("<ul>")
                for bullet in exp.get("bullets", []):
                    html_parts.append(f"<li>{bullet}</li>")
                html_parts.append("</ul>")

        if data.get("skills"):
            html_parts.append("<h2>Skills</h2>")
            html_parts.append(f"<p class='skills'>{', '.join(data['skills'])}</p>")

        if data.get("education"):
            html_parts.append("<h2>Education</h2>")
            for edu in data["education"]:
                year = f" ({edu['year']})" if edu.get("year") else ""
                html_parts.append(
                    f"<p><strong>{edu.get('degree', '')} — {edu.get('institution', '')}</strong>{year}</p>"
                )

        html_parts.append("</body></html>")
        html_content = "\n".join(html_parts)

        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except Exception:
        logger.exception("Failed to generate PDF")
        return None


def generate_cover_letter_pdf(content: str, full_name: str) -> bytes | None:
    try:
        from weasyprint import HTML

        paragraphs = "".join(
            f"<p>{p.strip()}</p>" for p in content.split("\n\n") if p.strip()
        )
        html_content = (
            "<html><head><style>"
            "body { font-family: Calibri, Arial, sans-serif; font-size: 11pt; margin: 40px; color: #333; line-height: 1.6; }"
            "p { margin-bottom: 12px; }"
            "</style></head><body>"
            f"{paragraphs}"
            "</body></html>"
        )
        return HTML(string=html_content).write_pdf()
    except Exception:
        logger.exception("Failed to generate cover letter PDF")
        return None
