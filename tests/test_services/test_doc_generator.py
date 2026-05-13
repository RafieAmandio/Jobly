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


def test_generate_cover_letter_docx():
    content = "Dear Hiring Manager,\n\nI am writing to express my interest.\n\nBest regards,\nJohn"
    result = generate_cover_letter_docx(content, "John Doe")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:2] == b"PK"
