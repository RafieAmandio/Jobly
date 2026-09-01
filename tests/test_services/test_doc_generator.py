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
                    "Lead migration to microservices",
                    "Reduce latency by 40%",
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
        "display_name": "Rafie",
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
                "bullets": ["Build the backend from scratch"],
            }
        ],
        "education": [
            {
                "institution": "UNIVERSITAS INDONESIA",
                "degree": "Computer Engineering",
                "gpa": "3.85/4.00",
                "year": "2021 - 2025",
                "bullets": ["Relevant coursework: Distributed Systems, Machine Learning"],
            }
        ],
        "certifications": ["Cisco CCNA"],
        "awards": ["1st Place, Galaxy Hackathon"],
        "projects": ["ProjectXOXO, 90,000+ users"],
        "additional_info": {
            "Languages": ["Indonesian", "English"],
            "Tests": ["IELTS 7.0"],
        },
        "skills": ["Python", "Go"],
    }
    result = generate_cv_docx(data, "Rafie Amandio Fauzan")
    parsed = Document(BytesIO(result))
    header_text = [p.text for p in parsed.sections[0].header.paragraphs]
    body_text = [p.text for p in parsed.paragraphs]

    assert isinstance(result, bytes)
    assert result[:2] == b"PK"
    assert any("Rafie | Jakarta, Indonesia | rafie@example.com" in text for text in header_text)
    assert any("3.85/4.00" in text for text in body_text)
    assert any("Relevant coursework: Distributed Systems, Machine Learning" in text for text in body_text)
    assert "ADDITIONAL INFORMATION" in body_text
    assert any("Languages: Indonesian, English" in text for text in body_text)
    assert any("Tests: IELTS 7.0" in text for text in body_text)


def test_generate_cover_letter_docx():
    content = "Dear Hiring Manager,\n\nI am writing to express my interest.\n\nBest regards,\nJohn"
    result = generate_cover_letter_docx(content, "John Doe")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:2] == b"PK"


def test_generate_cv_docx_uses_running_header_and_renders_leadership_org():
    data = {
        "display_name": "Dharma",
        "contact": {
            "location": "Hong Kong SAR",
            "email": "dharma@example.com",
            "phone": "+62 813 0000 0000",
        },
        "summary": "Finance-focused operator.",
        "experience": [
            {
                "company": "Financial Light",
                "title": "Analyst",
                "period": "Jan 2024 - Present",
                "bullets": ["Improve conversion by 22%"],
            }
        ],
        "leadership": [
            {
                "organization": "BEM UI",
                "title": "Treasurer",
                "period": "2023 - 2024",
                "bullets": ["Managed Rp 120M budget"],
            }
        ],
        "extra_miles": ["1st Place, Galaxy Hackathon"],
    }

    result = generate_cv_docx(data, "Dharma Setiawan")
    parsed = Document(BytesIO(result))
    text = [p.text for p in parsed.paragraphs]
    header_text = [p.text for p in parsed.sections[0].header.paragraphs]

    assert parsed.styles["Normal"].font.name == "Times New Roman"
    assert round(parsed.styles["Normal"].font.size.pt) == 10
    assert "WORK EXPERIENCES" in text
    assert "VOLUNTEER & LEADERSHIP EXPERIENCES" in text
    assert "EXTRA MILES" in text
    assert any("BEM UI" in t for t in text)
    assert any("Managed Rp 120M budget" in t for t in text)
    assert any("Dharma | Hong Kong SAR | dharma@example.com" in t for t in header_text)

    with ZipFile(BytesIO(result)) as zf:
        header_xml = zf.read("word/header1.xml").decode("utf-8")
    assert "Dharma | Hong Kong SAR | dharma@example.com" in header_xml
