import pytest

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
