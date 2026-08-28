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


def test_generate_cv_docx_uses_master_cv_format():
    """The renderer must keep the owner's master-CV look, not a sans-serif house style."""
    import io

    from docx import Document

    data = {
        "contact": {
            "location": "Jakarta Selatan",
            "email": "rafie@example.com",
            "phone": "+62 813 0000 0000",
        },
        "summary": "Finance-focused operator.",
        "experience": [
            {
                "company": "Financial Light",
                "title": "Analyst",
                "period": "Jan 2024 - Present",
                "bullets": ["Improved conversion by 22%."],
            }
        ],
        # PR #12's renamed keys must still render.
        "leadership": [
            {
                "company": "BEM UI",
                "title": "Treasurer",
                "period": "2023 - 2024",
                "bullets": ["Managed Rp 120M budget."],
            }
        ],
        "extra_miles": ["1st Place, Galaxy Hackathon"],
    }

    result = generate_cv_docx(data, "Rafie Amandio Fauzan")
    parsed = Document(io.BytesIO(result))
    text = [p.text for p in parsed.paragraphs]

    assert parsed.styles["Normal"].font.name == "Times New Roman"
    assert round(parsed.styles["Normal"].font.size.pt) == 10
    assert "WORK EXPERIENCES" in text
    # PR #12's renamed keys must still reach the page.
    assert "VOLUNTEER & LEADERSHIP EXPERIENCES" in text
    assert "EXTRA MILES" in text
    assert any("Managed Rp 120M budget." in t for t in text)
    assert any("1st Place, Galaxy Hackathon" in t for t in text)
