from types import SimpleNamespace

from jobly.services.cv_tailor import apply_cv_rules


def test_apply_cv_rules_normalizes_financial_light_structure():
    user = SimpleNamespace(email="user@example.com", phone="08123456789")
    data = {
        "contact": {"location": "Jakarta Selatan, DKI Jakarta", "linkedin": "https://linkedin.com/in/test"},
        "experience": [
            {"company": "A", "title": "Role", "period": "2024", "bullets": ["1", "2", "3", "4"]}
        ],
        "leadership": [
            {"organization": "BEM UI", "title": "Lead", "period": "2023", "bullets": ["a", "b", "c", "d"]}
        ],
        "awards": ["Award A"],
        "projects": ["Project B"],
        "certifications": ["Cert C"],
        "skills": ["Python", "SQL", "Excel"],
    }

    normalized = apply_cv_rules(data, user)

    phone = normalized["contact"]["phone"]
    assert phone.startswith("+62")
    assert phone.endswith("6789")
    assert normalized["contact"]["email"] == "user@example.com"
    assert normalized["contact"]["portfolio"] == "https://linkedin.com/in/test"
    assert normalized["contact"]["location"] == "Jakarta Selatan"
    assert len(normalized["experience"][0]["bullets"]) == 3
    assert len(normalized["leadership"][0]["bullets"]) == 3
    assert normalized["extra_miles"] == ["Award A", "Project B", "Cert C"]
    assert normalized["skills"] == {
        "technical": ["Python", "SQL", "Excel"],
        "soft": [],
        "tools": [],
    }
