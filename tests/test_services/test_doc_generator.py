from io import BytesIO
from zipfile import ZipFile

from docx import Document

from jobly.services.doc_generator import generate_cover_letter_docx, generate_cv_docx


def test_generate_cv_docx():
    data = {
        "summary": "Experienced software engineer with 5 years in fintech.",
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Gojek",
                "period": "2021-present",
                "bullets": [
                    "Led migration to microservices",
                    "Reduced latency by 40%",
                ],
            }
        ],
        "skills": ["Python", "Go", "PostgreSQL", "Docker"],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "Universitas Indonesia",
                "year": "2019",
            }
        ],
    }

    result = generate_cv_docx(data, "John Doe")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:2] == b"PK"


def test_generate_cv_docx_minimal():
    result = generate_cv_docx({}, "Minimal User")
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_cv_docx_with_contact_and_extra_sections():
    data = {
        "contact": {
            "location": "Jakarta, Indonesia",
            "email": "rafie@example.com",
            "phone": "+62 813 0000 0000",
            "linkedin": "https://linkedin.com/in/rafie",
        },
        "summary": "Senior engineer.",
        "experience": [
            {
                "company": "REVALUE ACADEMY, Remote",
                "title": "Senior Software Engineer",
                "period": "March 2025 - Present",
                "bullets": ["Built the backend from scratch."],
            }
        ],
        "education": [
            {
                "institution": "UNIVERSITAS INDONESIA",
                "degree": "Computer Engineering",
                "year": "2021 - 2025",
            }
        ],
        "certifications": ["Cisco CCNA"],
        "awards": ["1st Place — Galaxy Hackathon"],
        "projects": ["ProjectXOXO — 90,000+ users"],
        "skills": ["Python", "Go"],
    }
    result = generate_cv_docx(data, "Rafie Amandio Fauzan")
    assert isinstance(result, bytes)
    assert result[:2] == b"PK"


def test_generate_cover_letter_docx():
    content = "Dear Hiring Manager,\n\nI am writing to express my interest.\n\nBest regards,\nJohn"
    result = generate_cover_letter_docx(content, "John Doe")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:2] == b"PK"


def test_generate_cv_docx_financial_light_sections_and_links():
    data = {
        "contact": {
            "location": "Jakarta Selatan",
            "email": "rafie@example.com",
            "phone": "+62 813 0000 0000",
            "portfolio": "https://portfolio.example.com",
        },
        "summary": "Finance-focused operator.",
        "experience": [
            {
                "company": "Financial Light",
                "title": "Analyst",
                "period": "Jan 2024 - Present",
                "bullets": ["Improved conversion by 22%.", "Built reporting.", "Owned ops.", "Extra bullet should not appear"],
            }
        ],
        "leadership": [
            {
                "organization": "BEM UI",
                "title": "Treasurer",
                "period": "2023 - 2024",
                "bullets": ["Managed Rp 120M budget.", "Ran 4 events.", "Led 12 members."],
                "brief": "Student executive body.",
            }
        ],
        "education": [
            {
                "institution": "Universitas Indonesia",
                "degree": "Accounting",
                "year": "2021 - 2025",
                "details": "Dean list.",
            }
        ],
        "extra_miles": ["Hackathon Winner - UI - 2024"],
        "skills": {
            "technical": ["Financial Modeling", "SQL"],
            "soft": ["Stakeholder Management"],
            "tools": ["Excel", "Power BI"],
        },
    }

    result = generate_cv_docx(data, "Rafie Amandio Fauzan")
    parsed = Document(BytesIO(result))
    xml = ZipFile(BytesIO(result)).read("word/document.xml").decode("utf-8")
    rels = ZipFile(BytesIO(result)).read("word/_rels/document.xml.rels").decode("utf-8")

    assert parsed.styles["Normal"].font.name == "Arial"
    assert round(parsed.styles["Normal"].font.size.pt) == 9
    assert "LEADERSHIP" in xml
    assert "EXTRA MILES" in xml
    assert "SKILL SHOWCASE" in xml
    assert "portfolio.example.com" in xml
    assert "mailto:rafie@example.com" in rels
