from types import SimpleNamespace

from jobly.services.cv_tailor import apply_cv_rules


def test_apply_cv_rules_normalizes_financial_light_structure():
    user = SimpleNamespace(email="user@example.com", phone="08123456789")
    data = {
        "contact": {"location": "Jakarta Selatan, DKI Jakarta", "linkedin": "https://linkedin.com/in/test"},
        "summary": "Experienced finance operator. " * 40,
        "experience": [
            {"company": "A", "title": "Role", "period": "2024", "bullets": ["managed reporting for SQL dashboards", "2", "3", "4"]},
            {"company": "B", "title": "Role", "period": "2023", "bullets": ["owned fintech operations"]},
            {"company": "C", "title": "Role", "period": "2022", "bullets": ["built automation"]},
            {"company": "D", "title": "Role", "period": "2021", "bullets": ["improved turnaround time"]},
            {"company": "E", "title": "Role", "period": "2020", "bullets": ["extra role"]},
        ],
        "leadership": [
            {"organization": "BEM UI", "title": "Lead", "period": "2023", "bullets": ["organized mentoring program", "b", "c", "d"]},
            {"organization": "Volunteer Org", "title": "Coordinator", "period": "2022", "bullets": ["led 20 volunteers"]},
            {"organization": "Extra Org", "title": "Chair", "period": "2021", "bullets": ["should be trimmed"]},
        ],
        "awards": ["Award A"],
        "projects": ["Fintech Automation Project"],
        "certifications": ["SQL Certification"],
        "skills": {
            "technical": ["Excel", "SQL", "Financial Modeling"],
            "soft": ["Communication", "Stakeholder Management"],
            "tools": ["Power BI", "Notion"],
        },
    }

    normalized = apply_cv_rules(
        data,
        user,
        job_title="Fintech Operations Analyst",
        company="Acme Fintech",
        job_description="Need SQL, fintech reporting, stakeholder management, and financial modeling.",
    )

    phone = normalized["contact"]["phone"]
    assert phone.startswith("+62")
    assert phone.endswith("6789")
    assert normalized["contact"]["email"] == "user@example.com"
    assert normalized["contact"]["portfolio"] == "https://linkedin.com/in/test"
    assert normalized["contact"]["location"] == "Jakarta Selatan"
    assert len(normalized["summary"]) <= 450
    assert len(normalized["experience"]) == 4
    assert len(normalized["leadership"]) == 2
    assert len(normalized["experience"][0]["bullets"]) == 3
    assert len(normalized["leadership"][0]["bullets"]) == 3
    assert normalized["experience"][0]["bullets"][0].lower().startswith("managed")
    assert normalized["experience"][1]["bullets"][0].lower().startswith("owned")
    assert normalized["leadership"][0]["bullets"][0].lower().startswith("delivered organized")
    assert normalized["extra_miles"] == ["Fintech Automation Project", "SQL Certification", "Award A"]
    assert normalized["skills"]["technical"] == ["SQL", "Financial Modeling", "Excel"]
