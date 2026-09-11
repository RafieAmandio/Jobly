import io
import logging
import re
from html import escape
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

# Layout mirrors the owner's master CV exactly: centred serif header with a rule
# under the contact line, an un-headed justified summary, then navy uppercase
# section titles each preceded by a horizontal rule. Education puts the period on
# its own line; work/volunteer entries right-align the period beside the org.
NAVY = RGBColor(0x1F, 0x4E, 0x79)
RULE_COLOR = "999999"
BULLET = "●"  # ●
RIGHT_TAB_INCHES = 7.15

# Order matters — this is the master CV's section order.
def _volunteer_key(data: dict) -> str:
    """PR #12 renamed this section's key; read whichever the AI produced."""
    return "leadership" if data.get("leadership") else "volunteer"


LIST_SECTIONS = (
    ("extra_miles", "Extra Miles"),
    ("certifications", "Certifications"),
    ("awards", "Awards"),
    ("projects", "Stem Projects"),
)

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)


def _display_name(data: dict, fallback_full_name: str) -> str:
    return str(data.get("display_name") or fallback_full_name).strip()


def _contact_line(contact: dict | None) -> list[str]:
    """Ordered, non-empty contact fields for the centred header line."""
    if not contact:
        return []
    parts = []
    for key in ("location", "email", "phone", "portfolio", "linkedin"):
        value = contact.get(key)
        if value:
            parts.append(str(value).strip())
    return parts


def _header_line(data: dict, fallback_full_name: str) -> str:
    name = _display_name(data, fallback_full_name)
    parts = [name] if name else []
    for part in _contact_line(data.get("contact")):
        if part not in parts:
            parts.append(part)
    return " | ".join(parts)


def _split_bold(text: str) -> list[tuple[str, bool]]:
    """Split text on **bold** markers into (chunk, is_bold) pairs."""
    out: list[tuple[str, bool]] = []
    pos = 0
    for m in _BOLD_RE.finditer(text):
        if m.start() > pos:
            out.append((text[pos : m.start()], False))
        out.append((m.group(1), True))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], False))
    return out or [(text, False)]


# --------------------------------------------------------------------------- #
# DOCX helpers
# --------------------------------------------------------------------------- #
def _rule(paragraph, position: str = "top") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    edge = OxmlElement(f"w:{position}")
    edge.set(qn("w:val"), "single")
    edge.set(qn("w:sz"), "6")
    edge.set(qn("w:space"), "4")
    edge.set(qn("w:color"), RULE_COLOR)
    borders.append(edge)
    p_pr.append(borders)


def _runs(paragraph, text: str, italic: bool = False, size: float | None = None):
    for chunk, bold in _split_bold(text):
        run = paragraph.add_run(chunk)
        run.bold = bold
        run.italic = italic
        if size:
            run.font.size = Pt(size)


def _section(doc, title: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(title.upper())
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = NAVY
    _rule(p, "top")
    return p


def _bullet(doc, text: str):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.50)
    pf.first_line_indent = Inches(-0.25)
    pf.space_after = Pt(1)
    pf.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    marker = p.add_run(f"{BULLET}  ")
    marker.font.size = Pt(8.5)
    _runs(p, text)
    return p


def _entry_head(doc, left: str, right: str):
    """Org bold on the left, period right-aligned on the same line."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(RIGHT_TAB_INCHES), WD_TAB_ALIGNMENT.RIGHT
    )
    _runs(p, left)
    if right:
        p.add_run(f"\t{right}")
    return p


def _exp_entries(data: dict, key: str) -> list[dict]:
    items = data.get(key) or []
    return [e for e in items if isinstance(e, dict)]


def _org_label(exp: dict) -> str:
    company = (exp.get("company") or exp.get("organization") or "").strip()
    location = (exp.get("location") or "").strip()
    if company and location:
        return f"**{company}**, {location}"
    return f"**{company}**" if company else location


def _edu_label(edu: dict) -> str:
    bits = [b for b in (edu.get("degree"), edu.get("gpa")) if b]
    inst = (edu.get("institution") or "").strip()
    head = f"**{inst}**" if inst else ""
    if bits:
        joined = " | ".join(str(b).strip() for b in bits)
        return f"{head} | {joined}" if head else joined
    return head


def _additional_info(data: dict) -> list[tuple[str, str]]:
    """(label, value) rows for the ADDITIONAL INFORMATION block."""
    info = data.get("additional_info")
    rows: list[tuple[str, str]] = []
    if isinstance(info, dict):
        for label, value in info.items():
            if not value:
                continue
            text = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
            rows.append((str(label), text))
    if not rows and isinstance(data.get("skills"), dict):
        labels = {
            "technical": "Technical",
            "soft": "Soft Skills",
            "tools": "Tools",
        }
        for key, label in labels.items():
            values = [str(v).strip() for v in data["skills"].get(key, []) if str(v).strip()]
            if values:
                rows.append((label, ", ".join(values)))
    elif not rows and data.get("skills"):
        rows.append(("Skills", ", ".join(str(s) for s in data["skills"])))
    return rows


# --------------------------------------------------------------------------- #
# CV — DOCX
# --------------------------------------------------------------------------- #
def generate_cv_docx(data: dict, full_name: str) -> bytes:
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.45)
        section.left_margin = Inches(0.51)
        section.right_margin = Inches(0.51)
        header = section.header
        header_p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        header_p.paragraph_format.space_after = Pt(4)
        header_run = header_p.add_run(_header_line(data, full_name))
        header_run.bold = True
        header_run.font.size = Pt(9.5)
        _rule(header_p, "bottom")

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(10)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.line_spacing = 1.19

    if data.get("summary"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        _runs(p, data["summary"])

    education = _exp_entries(data, "education")
    if education:
        _section(doc, "Education")
    for edu in education:
        label = _edu_label(edu)
        if label:
            head = doc.add_paragraph()
            head.paragraph_format.space_before = Pt(2)
            head.paragraph_format.space_after = Pt(0)
            _runs(head, label)
        if edu.get("year"):
            period = doc.add_paragraph()
            period.paragraph_format.space_after = Pt(1)
            period.add_run(str(edu["year"]))
        for bullet in edu.get("bullets") or []:
            _bullet(doc, bullet)

    for key, heading in (("experience", "Work Experiences"), (_volunteer_key(data), "Volunteer & Leadership Experiences")):
        entries = _exp_entries(data, key)
        if not entries:
            continue
        _section(doc, heading)
        for exp in entries:
            _entry_head(doc, _org_label(exp), str(exp.get("period") or ""))
            if exp.get("title"):
                role = doc.add_paragraph()
                role.paragraph_format.space_after = Pt(1)
                _runs(role, str(exp["title"]), italic=True)
            for bullet in exp.get("bullets") or []:
                _bullet(doc, bullet)

    for key, heading in LIST_SECTIONS:
        items = data.get(key) or []
        if not items:
            continue
        _section(doc, heading)
        for item in items:
            _bullet(doc, str(item))

    rows = _additional_info(data)
    if rows:
        _section(doc, "Additional Information")
        for label, value in rows:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(1)
            p.add_run(f"{label}: ").bold = True
            _runs(p, value)

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
    name_p.paragraph_format.space_after = Pt(1)
    name_run = name_p.add_run(full_name)
    name_run.bold = True
    name_run.font.size = Pt(15)

    contact_parts = _contact_line(contact)
    if contact_parts:
        contact_p = doc.add_paragraph()
        contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_p.paragraph_format.space_after = Pt(10)
        contact_p.add_run(" | ".join(contact_parts)).font.size = Pt(10)
        _rule(contact_p, "bottom")

    for paragraph in content.split("\n\n"):
        paragraph = paragraph.strip()
        if paragraph:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(8)
            _runs(p, paragraph)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# --------------------------------------------------------------------------- #
# CV — PDF (WeasyPrint)
# --------------------------------------------------------------------------- #
_CV_CSS = """
@page {
  size: A4;
  margin: 0.78in 0.51in 0.5in;
  @top-center { content: element(cv-header); }
}
html, body { margin: 0; padding: 0; }
body { font-family: 'Times New Roman', 'Liberation Serif', Georgia, serif;
       font-size: 10pt; color: #000; line-height: 1.19; }
p { margin: 0; }
.running-header {
  position: running(cv-header);
  text-align: center;
  font-size: 9.5pt;
  font-weight: bold;
  border-bottom: 1px solid #888888;
  padding-bottom: 4px;
}
.contact a { color: #0563C1; }
.rule.pre-section { margin-top: 12px; }
.summary { text-align: justify; margin: 2px 0 0; }
h2.section { font-size: 12pt; font-weight: bold; color: #1F4E79; text-transform: uppercase;
             margin: 4px 0 2px; }
.entry-head { display: flex; justify-content: space-between; align-items: baseline; margin-top: 3px; }
.entry-org { font-weight: normal; }
.entry-period { white-space: nowrap; padding-left: 14px; }
.entry-role { font-style: italic; margin-bottom: 1px; }
.edu-period { margin: 1px 0 1px; }
ul { margin: 1px 0 3px; padding-left: 48px; list-style: none; }
li { position: relative; margin-bottom: 2px; text-align: justify; }
li::before { content: "\\25cf"; position: absolute; left: -24px; font-size: 8.5pt; top: 0.05em; }
.info-row { text-align: justify; margin-bottom: 1px; }
.info-label { font-weight: bold; }
"""

_RULE = "<div class='rule'></div>"
_RULE_SECTION = "<div class='rule pre-section'></div>"


def _inline(text: str) -> str:
    """Escape, then honour **bold** markers."""
    out = []
    for chunk, bold in _split_bold(str(text)):
        safe = escape(chunk)
        out.append(f"<b>{safe}</b>" if bold else safe)
    return "".join(out)


def _section_html(title: str) -> str:
    return f"{_RULE_SECTION}<h2 class='section'>{title}</h2>"


def _bullets_html(items) -> list[str]:
    if not items:
        return []
    parts = ["<ul>"]
    parts += [f"<li>{_inline(b)}</li>" for b in items]
    parts.append("</ul>")
    return parts


def _contact_html(contact: dict | None) -> str:
    parts = _contact_line(contact)
    if not parts:
        return ""
    rendered = []
    for part in parts:
        if part.startswith(("http://", "https://", "www.")):
            href = part if part.startswith("http") else f"https://{part}"
            rendered.append(f"<a href='{escape(href)}'>{escape(part)}</a>")
        else:
            rendered.append(escape(part))
    return f"<p class='contact'>{' | '.join(rendered)}</p>"


def _header_html(data: dict, full_name: str) -> str:
    rendered = []
    for part in _header_line(data, full_name).split(" | "):
        if part.startswith(("http://", "https://", "www.")):
            href = part if part.startswith("http") else f"https://{part}"
            rendered.append(f"<a href='{escape(href)}'>{escape(part)}</a>")
        else:
            rendered.append(escape(part))
    return f"<div class='running-header'>{' | '.join(rendered)}</div>"


def generate_cv_pdf(data: dict, full_name: str) -> bytes | None:
    try:
        from weasyprint import HTML

        parts = [
            "<html><head><meta charset='utf-8'><style>",
            _CV_CSS,
            "</style></head><body>",
            _header_html(data, full_name),
        ]

        if data.get("summary"):
            parts.append(f"<p class='summary'>{_inline(data['summary'])}</p>")

        education = _exp_entries(data, "education")
        if education:
            parts.append(_section_html("Education"))
            for edu in education:
                label = _edu_label(edu)
                if label:
                    parts.append(f"<p>{_inline(label)}</p>")
                if edu.get("year"):
                    parts.append(f"<p class='edu-period'>{escape(str(edu['year']))}</p>")
                parts += _bullets_html(edu.get("bullets"))

        for key, heading in (
            ("experience", "Work Experiences"),
            (_volunteer_key(data), "Volunteer &amp; Leadership Experiences"),
        ):
            entries = _exp_entries(data, key)
            if not entries:
                continue
            parts.append(_section_html(heading))
            for exp in entries:
                parts.append(
                    "<div class='entry-head'>"
                    f"<span class='entry-org'>{_inline(_org_label(exp))}</span>"
                    f"<span class='entry-period'>{escape(str(exp.get('period') or ''))}</span>"
                    "</div>"
                )
                if exp.get("title"):
                    parts.append(f"<p class='entry-role'>{escape(str(exp['title']))}</p>")
                parts += _bullets_html(exp.get("bullets"))

        for key, heading in LIST_SECTIONS:
            items = data.get(key) or []
            if items:
                parts.append(_section_html(heading))
                parts += _bullets_html(items)

        rows = _additional_info(data)
        if rows:
            parts.append(_section_html("Additional Information"))
            for label, value in rows:
                parts.append(
                    f"<p class='info-row'><span class='info-label'>{escape(label)}:</span> "
                    f"{_inline(value)}</p>"
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
            f"<p>{_inline(p.strip())}</p>" for p in content.split("\n\n") if p.strip()
        )
        css = (
            "@page { size: A4; margin: 0.8in 0.9in; }"
            "body { font-family: 'Times New Roman', Georgia, serif; font-size: 11pt; color: #000; line-height: 1.5; }"
            ".name { text-align: center; font-size: 15pt; font-weight: bold; margin: 0 0 1px; }"
            ".contact { text-align: center; font-size: 10pt; margin: 0 0 14px; padding-bottom: 4px; border-bottom: 1px solid #999; }"
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
