import io
import logging
from html import escape
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

# ATS-friendly format: sans-serif body, simple headings, no tables/graphics.
NAVY = RGBColor(0x1F, 0x4E, 0x79)
LINK_BLUE = RGBColor(0x05, 0x63, 0xC1)
RIGHT_TAB_INCHES = 7.0
BODY_FONT = "Arial"
BODY_FONT_SIZE = Pt(9)


def _contact_line(contact: dict | None) -> list[str]:
    """Ordered, non-empty contact fields for the centred header line."""
    if not contact:
        return []
    parts = []
    for key in ("location", "email", "phone", "portfolio", "linkedin"):
        value = contact.get(key)
        if value:
            parts.append(str(value).strip())
    deduped = []
    seen = set()
    for part in parts:
        lower = part.lower()
        if lower not in seen:
            seen.add(lower)
            deduped.append(part)
    return deduped


# --------------------------------------------------------------------------- #
# DOCX helpers
# --------------------------------------------------------------------------- #
def _set_bottom_border(paragraph, size: int = 6, color: str = "BFBFBF") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    p_pr.append(borders)


def _section_heading(doc, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11.5)
    run.font.color.rgb = NAVY
    _set_bottom_border(p)


def _entry_header(doc, org: str, period: str) -> None:
    """Org bold on the left, period right-aligned on the same line."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(RIGHT_TAB_INCHES), WD_TAB_ALIGNMENT.RIGHT
    )
    org_run = p.add_run(org)
    org_run.bold = True
    if period:
        p.add_run(f"\t{period}")


def _write_bullets(doc, bullets: list[str]) -> None:
    for bullet in bullets[:3]:
        b = doc.add_paragraph(bullet, style="List Bullet")
        b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        b.paragraph_format.space_after = Pt(1)


def _add_hyperlink(paragraph, text: str, url: str) -> None:
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")

    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    r_pr.append(color)

    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.append(underline)

    run.append(r_pr)
    text_elem = OxmlElement("w:t")
    text_elem.text = text
    run.append(text_elem)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def _add_contact_line(paragraph, contact: dict | None) -> None:
    if not contact:
        return

    parts: list[tuple[str, str | None]] = []
    location = contact.get("location")
    email = contact.get("email")
    phone = contact.get("phone")
    portfolio = contact.get("portfolio") or contact.get("linkedin")

    if location:
        parts.append((str(location).strip(), None))
    if email:
        email_text = str(email).strip()
        parts.append((email_text, f"mailto:{email_text}"))
    if phone:
        parts.append((str(phone).strip(), None))
    if portfolio:
        portfolio_text = str(portfolio).strip()
        href = portfolio_text if portfolio_text.startswith("http") else f"https://{portfolio_text}"
        parts.append((portfolio_text, href))

    first = True
    for text, href in parts:
        if not first:
            paragraph.add_run(" | ")
        first = False
        if href:
            _add_hyperlink(paragraph, text, href)
        else:
            paragraph.add_run(text)


def _build_cv_header(doc, full_name: str, contact: dict | None) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(1.15)
    section.header_distance = Inches(0.25)
    header = section.header
    header.is_linked_to_previous = False

    name_p = header.paragraphs[0]
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_p.paragraph_format.space_after = Pt(2)
    name_run = name_p.add_run(full_name)
    name_run.bold = True
    name_run.font.size = Pt(17)

    contact_parts = _contact_line(contact)
    if contact_parts:
        contact_p = header.add_paragraph()
        contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_p.paragraph_format.space_after = Pt(2)
        _add_contact_line(contact_p, contact)
        _set_bottom_border(contact_p, color="000000")


def _skill_groups(data: dict) -> list[tuple[str, list[str]]]:
    skills = data.get("skills") or {}
    if isinstance(skills, list):
        skills = {"technical": skills, "soft": [], "tools": []}
    return [
        ("Technical", [str(item).strip() for item in skills.get("technical", []) if str(item).strip()]),
        ("Soft Skills", [str(item).strip() for item in skills.get("soft", []) if str(item).strip()]),
        ("Tools", [str(item).strip() for item in skills.get("tools", []) if str(item).strip()]),
    ]


# --------------------------------------------------------------------------- #
# CV — DOCX
# --------------------------------------------------------------------------- #
def generate_cv_docx(data: dict, full_name: str) -> bytes:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1.15)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.63)
        section.right_margin = Inches(0.63)

    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = BODY_FONT_SIZE
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.line_spacing = 1.05

    _build_cv_header(doc, full_name, data.get("contact"))

    if data.get("summary"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(6)
        p.add_run(data["summary"])

    if data.get("experience"):
        _section_heading(doc, "Experience")
        for exp in data["experience"]:
            _entry_header(doc, exp.get("company", ""), exp.get("period", ""))
            if exp.get("title"):
                role_p = doc.add_paragraph()
                role_p.paragraph_format.space_after = Pt(2)
                role_run = role_p.add_run(exp["title"])
                role_run.italic = True
            _write_bullets(doc, exp.get("bullets", []))

    if data.get("leadership"):
        _section_heading(doc, "Leadership")
        for item in data["leadership"]:
            _entry_header(doc, item.get("organization", ""), item.get("period", ""))
            if item.get("title"):
                role_p = doc.add_paragraph()
                role_p.paragraph_format.space_after = Pt(2)
                role_p.add_run(item["title"]).italic = True
            if item.get("brief"):
                brief_p = doc.add_paragraph()
                brief_p.paragraph_format.space_after = Pt(2)
                brief_p.add_run(item["brief"])
            _write_bullets(doc, item.get("bullets", []))

    if data.get("education"):
        _section_heading(doc, "Education")
        for edu in data["education"]:
            org = edu.get("institution", "")
            _entry_header(doc, org, edu.get("year", ""))
            if edu.get("degree"):
                deg_p = doc.add_paragraph()
                deg_p.paragraph_format.space_after = Pt(2)
                deg_p.add_run(edu["degree"]).italic = True
            if edu.get("details"):
                details_p = doc.add_paragraph()
                details_p.paragraph_format.space_after = Pt(2)
                details_p.add_run(edu["details"])

    extra_miles = data.get("extra_miles") or data.get("awards") or data.get("projects")
    if extra_miles:
        _section_heading(doc, "Extra Miles")
        for item in extra_miles:
            b = doc.add_paragraph(str(item), style="List Bullet")
            b.paragraph_format.space_after = Pt(1)

    skill_groups = [(heading, items) for heading, items in _skill_groups(data) if items]
    if skill_groups:
        _section_heading(doc, "Skill Showcase")
        for heading, items in skill_groups:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            label = p.add_run(f"{heading}: ")
            label.bold = True
            p.add_run(", ".join(items))

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def generate_cover_letter_docx(
    content: str, full_name: str, contact: dict | None = None
) -> bytes:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.paragraph_format.line_spacing = 1.15

    name_p = doc.add_paragraph()
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_p.paragraph_format.space_after = Pt(2)
    name_run = name_p.add_run(full_name)
    name_run.bold = True
    name_run.font.size = Pt(18)

    contact_parts = _contact_line(contact)
    if contact_parts:
        contact_p = doc.add_paragraph()
        contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_p.paragraph_format.space_after = Pt(8)
        run = contact_p.add_run(" | ".join(contact_parts))
        run.font.size = Pt(9.5)
        _set_bottom_border(contact_p, color="000000")

    for paragraph in content.split("\n\n"):
        paragraph = paragraph.strip()
        if paragraph:
            p = doc.add_paragraph(paragraph)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(8)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# --------------------------------------------------------------------------- #
# CV — PDF (WeasyPrint)
# --------------------------------------------------------------------------- #
_CV_CSS = """
@page {
  size: A4;
  margin: 2.6cm 1.4cm 1.2cm 1.4cm;
  @top-center { content: element(cv-header); }
}
body { font-family: Arial, Helvetica, sans-serif; font-size: 9pt; color: #000; line-height: 1.2; }
.cv-header { position: running(cv-header); text-align: center; }
.cv-header .name { font-size: 17pt; font-weight: bold; margin: 0 0 2px; }
.cv-header .contact { font-size: 9pt; margin: 0 0 5px; padding-bottom: 5px; border-bottom: 1px solid #000; }
.cv-header .contact a { color: #0563C1; text-decoration: none; }
.summary { text-align: justify; margin: 5px 0 3px; }
h2.section { font-size: 10pt; font-weight: bold; color: #1F4E79; text-transform: uppercase;
             letter-spacing: .3px; border-bottom: 1.2px solid #BFBFBF; padding-bottom: 2px; margin: 9px 0 4px; }
.entry-head { display: flex; justify-content: space-between; align-items: baseline; margin-top: 3px; }
.entry-org { font-weight: bold; }
.entry-period { white-space: nowrap; padding-left: 10px; }
.entry-role { font-style: italic; margin: 0 0 2px; }
p { margin: 0 0 3px; }
ul { margin: 1px 0 3px; padding-left: 16px; }
li { margin-bottom: 1px; text-align: justify; }
.skills { text-align: justify; margin-top: 1px; }
"""


def _entry_head_html(org: str, period: str) -> str:
    return (
        "<div class='entry-head'>"
        f"<span class='entry-org'>{escape(org)}</span>"
        f"<span class='entry-period'>{escape(period)}</span>"
        "</div>"
    )


def _contact_html(contact: dict | None, *, class_name: str = "contact") -> str:
    parts = _contact_line(contact)
    if not parts:
        return ""
    rendered = []
    email = (contact or {}).get("email")
    portfolio = (contact or {}).get("portfolio") or (contact or {}).get("linkedin")
    phone = (contact or {}).get("phone")
    location = (contact or {}).get("location")

    if location:
        rendered.append(escape(str(location).strip()))
    if email:
        email_text = str(email).strip()
        rendered.append(f"<a href='mailto:{escape(email_text)}'>{escape(email_text)}</a>")
    if phone:
        rendered.append(escape(str(phone).strip()))
    if portfolio:
        portfolio_text = str(portfolio).strip()
        href = portfolio_text if portfolio_text.startswith("http") else f"https://{portfolio_text}"
        rendered.append(f"<a href='{escape(href)}'>{escape(portfolio_text)}</a>")

    return f"<p class='{class_name}'>{' | '.join(rendered)}</p>"


def generate_cv_pdf(data: dict, full_name: str) -> bytes | None:
    try:
        from weasyprint import HTML

        parts = [
            "<html><head><meta charset='utf-8'><style>",
            _CV_CSS,
            "</style></head><body>",
            "<div class='cv-header'>",
            f"<div class='name'>{escape(full_name)}</div>",
            _contact_html(data.get("contact"), class_name="contact"),
            "</div>",
        ]

        if data.get("summary"):
            parts.append(f"<p class='summary'>{escape(data['summary'])}</p>")

        if data.get("experience"):
            parts.append("<h2 class='section'>Experience</h2>")
            for exp in data["experience"]:
                parts.append(_entry_head_html(exp.get("company", ""), exp.get("period", "")))
                if exp.get("title"):
                    parts.append(f"<p class='entry-role'>{escape(exp['title'])}</p>")
                if exp.get("bullets"):
                    parts.append("<ul>")
                    parts.extend(f"<li>{escape(b)}</li>" for b in exp["bullets"][:3])
                    parts.append("</ul>")

        if data.get("leadership"):
            parts.append("<h2 class='section'>Leadership</h2>")
            for item in data["leadership"]:
                parts.append(_entry_head_html(item.get("organization", ""), item.get("period", "")))
                if item.get("title"):
                    parts.append(f"<p class='entry-role'>{escape(item['title'])}</p>")
                if item.get("brief"):
                    parts.append(f"<p>{escape(item['brief'])}</p>")
                if item.get("bullets"):
                    parts.append("<ul>")
                    parts.extend(f"<li>{escape(b)}</li>" for b in item["bullets"][:3])
                    parts.append("</ul>")

        if data.get("education"):
            parts.append("<h2 class='section'>Education</h2>")
            for edu in data["education"]:
                parts.append(_entry_head_html(edu.get("institution", ""), edu.get("year", "")))
                if edu.get("degree"):
                    parts.append(f"<p class='entry-role'>{escape(edu['degree'])}</p>")
                if edu.get("details"):
                    parts.append(f"<p>{escape(edu['details'])}</p>")

        extra_miles = data.get("extra_miles") or data.get("awards") or data.get("projects")
        if extra_miles:
            parts.append("<h2 class='section'>Extra Miles</h2><ul>")
            parts.extend(f"<li>{escape(str(item))}</li>" for item in extra_miles)
            parts.append("</ul>")

        skill_groups = [(heading, items) for heading, items in _skill_groups(data) if items]
        if skill_groups:
            parts.append("<h2 class='section'>Skill Showcase</h2>")
            for heading, items in skill_groups:
                parts.append(
                    f"<p class='skills'><strong>{escape(heading)}:</strong> {escape(', '.join(items))}</p>"
                )

        parts.append("</body></html>")
        return HTML(string="\n".join(parts)).write_pdf()
    except Exception:
        logger.exception("Failed to generate PDF")
        return None


def generate_cover_letter_pdf(
    content: str, full_name: str, contact: dict | None = None
) -> bytes | None:
    try:
        from weasyprint import HTML

        paragraphs = "".join(
            f"<p>{escape(p.strip())}</p>" for p in content.split("\n\n") if p.strip()
        )
        css = (
            "@page { size: A4; margin: 2cm 2.2cm; }"
            "body { font-family: 'Times New Roman', Georgia, serif; font-size: 11pt; color: #000; line-height: 1.5; }"
            ".name { text-align: center; font-size: 18pt; font-weight: bold; margin: 0 0 2px; }"
            ".contact { text-align: center; font-size: 9.5pt; margin: 0 0 14px; padding-bottom: 6px; border-bottom: 1px solid #000; }"
            "p { margin-bottom: 10px; text-align: justify; }"
        )
        html_content = (
            "<html><head><meta charset='utf-8'><style>"
            f"{css}</style></head><body>"
            f"<p class='name'>{escape(full_name)}</p>"
            f"{_contact_html(contact)}"
            f"{paragraphs}"
            "</body></html>"
        )
        return HTML(string=html_content).write_pdf()
    except Exception:
        logger.exception("Failed to generate cover letter PDF")
        return None
