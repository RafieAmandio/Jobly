from types import SimpleNamespace

from jobly.services.cv_tailor import apply_cv_rules


def test_apply_cv_rules_normalizes_financial_light_structure():
    user = SimpleNamespace(email="user@example.com", phone="08123456789", full_name="Dharma Setiawan")
    data = {
        "contact": {"location": "Jakarta Selatan, DKI Jakarta", "linkedin": "https://linkedin.com/in/test"},
        "summary": "Experienced finance operator. " * 40,
        "experience": [
            {
                "company": "A",
                "title": "Role",
                "period": "2024",
                "bullets": ["managed reporting for SQL dashboards.", "2", "3", "4"],
            },
            {"company": "B", "title": "Role", "period": "2023", "bullets": ["owned fintech operations"]},
            {"company": "C", "title": "Role", "period": "2022", "bullets": ["built automation"]},
            {"company": "D", "title": "Role", "period": "2021", "bullets": ["improved turnaround time"]},
            {"company": "E", "title": "Role", "period": "2020", "bullets": ["extra role"]},
        ],
        "leadership": [
            {
                "organization": "BEM UI",
                "title": "Lead",
                "period": "2023",
                "bullets": ["organized mentoring program", "b", "c", "d"],
            },
            {"organization": "Volunteer Org", "title": "Coordinator", "period": "2022", "bullets": ["led 20 volunteers"]},
            {"organization": "Extra Org", "title": "Chair", "period": "2021", "bullets": ["should be trimmed"]},
        ],
        "education": [
            {
                "institution": "CUHK Shenzhen",
                "degree": "BSc Data Science",
                "gpa": "3.78/4.00",
                "year": "2020 - 2024",
                "details": ["Dean's List"],
                "coursework": ["Machine Learning", "Data Mining"],
            }
        ],
        "awards": ["Award A"],
        "projects": ["Fintech Automation Project"],
        "certifications": ["SQL Certification"],
        "additional_info": {"Languages": ["English.", "Indonesian."]},
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
        source_cv_text="Dharma\nHong Kong SAR | dharma@example.com",
    )

    phone = normalized["contact"]["phone"]
    assert phone.startswith("+62")
    assert phone.endswith("6789")
    assert normalized["display_name"] == "Dharma"
    assert normalized["contact"]["email"] == "user@example.com"
    assert normalized["contact"]["portfolio"] == "https://linkedin.com/in/test"
    assert normalized["contact"]["location"] == "Jakarta Selatan"
    assert len(normalized["summary"]) <= 450
    assert len(normalized["experience"]) == 4
    assert len(normalized["leadership"]) == 2
    assert len(normalized["experience"][0]["bullets"]) == 3
    assert len(normalized["leadership"][0]["bullets"]) == 3
    assert normalized["experience"][0]["bullets"][0] == "Managed reporting for SQL dashboards"
    assert normalized["leadership"][0]["bullets"][0] == "Organized mentoring program"
    assert normalized["education"][0]["gpa"] == "3.78/4.00"
    assert normalized["education"][0]["bullets"] == [
        "Dean's List",
        "Relevant coursework: Machine Learning",
        "Relevant coursework: Data Mining",
    ]
    assert normalized["additional_info"] == {"Languages": ["English", "Indonesian"]}
    assert normalized["extra_miles"] == ["Fintech Automation Project", "SQL Certification", "Award A"]
    assert normalized["skills"]["technical"] == ["SQL", "Financial Modeling", "Excel"]


def test_apply_cv_rules_uses_present_tense_for_current_roles_and_moves_project_roles():
    user = SimpleNamespace(email=None, phone=None, full_name="Dharma Setiawan")
    data = {
        "experience": [
            {
                "company": "DBS Bank HK Limited",
                "title": "Management Associate",
                "period": "Jul 2024 - Present",
                "bullets": [
                    "Led AI roadmap execution.",
                    "Directed the full project lifecycle—including data pipeline design, feature engineering, and operational integration.",
                ],
            },
            {
                "company": "Dana Indonesia",
                "title": "Project Machine Learning Lead — Bangkit by Google, Traveloka, GoTo",
                "period": "Mar 2023 - Jun 2023",
                "bullets": ["Built fraud model for payment use cases."],
            },
        ],
        "skills": {"technical": [], "soft": [], "tools": []},
    }

    normalized = apply_cv_rules(
        data,
        user,
        job_title="AI Product Analyst",
        company="Acme",
        job_description="Need AI roadmap and machine learning experience.",
    )

    assert normalized["experience"][0]["bullets"] == [
        "Lead AI roadmap execution",
        "Direct the full project lifecycle, including data pipeline design, feature engineering, and operational integration",
    ]
    assert len(normalized["experience"]) == 1
    assert any("Project Machine Learning Lead" in item for item in normalized["extra_miles"])
