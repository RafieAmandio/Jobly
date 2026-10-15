import re
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
                "location": "Hong Kong SAR",
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
    assert len(normalized["summary"]) <= 650
    assert len(normalized["experience"]) == 5
    assert len(normalized["leadership"]) == 2
    assert len(normalized["experience"][0]["bullets"]) == 3
    assert normalized["experience"][0]["location"] == "Hong Kong SAR"
    assert len(normalized["leadership"][0]["bullets"]) == 3
    assert normalized["experience"][0]["bullets"][0] == "Managed reporting for SQL dashboards"
    assert normalized["leadership"][0]["bullets"][0] == "Organized mentoring program"
    assert normalized["education"][0]["gpa"] == "3.78/4.00"
    assert normalized["education"][0]["coursework"] == ["Machine Learning", "Data Mining"]
    assert normalized["education"][0]["honors_awards"] == ["Dean's List"]
    assert normalized["education"][0]["bullets"] == []
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


def test_apply_cv_rules_cleans_tailored_cv_regressions():
    user = SimpleNamespace(email="dharma@example.com", phone="08123456789", full_name="Dharma Setiawan")
    data = {
        "contact": {
            "location": "Hong Kong SAR / Indonesia",
            "email": "dharma@example.com",
            "phone": "+628****6021",
            "linkedin": "https://linkedin.com/in/dharma-setiawan",
        },
        "summary": (
            "Detail-oriented data professional with bilingual Indonesian-English proficiency. "
            "Strong analytical foundation in data science. "
            "Experienced in remote content evaluation, QA, rubric-based workflows, "
            "and root cause analysis across financial services and technology projects. "
        ) * 4,
        "education": [
            {
                "institution": "CUHK Shenzhen",
                "degree": "BSc Data Science",
                "year": "2020 - 2024",
                "location": "Shenzhen, China",
                "rank": "First Honours GPA (Rank 10: 174)",
                "awards": ["Academic Scholarship Group C"],
                "activities": ["Teaching Assistant", "Research Assistant", "Mentor", "Student Representative", "USTF"],
                "coursework": ["Intro to Data Science", "Linear Algebra", "Numerical Methods", "Supply Chain"],
                "bullets": ["Dean's List 2020, 2021, 2022, 2023, 2023, 2024 (Top 15%)"],
            }
        ],
        "additional_info": {
            "Languages": ["Indonesian: Professional", "English: Professional (IELTS 7, SAT 1290)"],
            "Tests": ["IELTS 7, SAT 1290"],
        },
        "skills": {"technical": [], "soft": [], "tools": []},
    }

    normalized = apply_cv_rules(
        data,
        user,
        source_cv_text="Management Associate Business Analyst Project Manager cross-functional",
    )

    assert normalized["summary"].endswith(".")
    assert not normalized["summary"].endswith("remote")
    assert normalized["summary"].count(".") == 3
    assert "Management Trainee" in normalized["summary"]
    assert "PM/BA" in normalized["summary"]
    assert "cross-functional" in normalized["summary"]
    assert normalized["contact"]["location"] == "Hong Kong SAR"
    assert normalized["contact"]["phone"] == "+628123456789"
    education = normalized["education"][0]
    assert education["location"] == "Shenzhen, China"
    assert education["rank"] == "First Honours GPA (Rank 10: 174)"
    assert education["coursework"] == [
        "Intro to Data Science",
        "Linear Algebra",
        "Numerical Methods",
        "Supply Chain",
    ]
    assert education["honors_awards"] == [
        "Academic Scholarship Group C",
        "Dean's List Ranges: 2020-2021, 2022-2023, 2023-24 (Top 15%)",
    ]
    assert education["activities"] == [
        "Teaching Assistant",
        "Research Assistant",
        "Mentor",
        "Student Representative",
        "USTF",
    ]
    assert education["bullets"] == []
    assert normalized["additional_info"] == {
        "Languages": [
            "Indonesian: Professional",
            "English: Professional (IELTS 7, SAT 1290)",
        ]
    }


def test_apply_cv_rules_enforces_summary_style_and_length():
    user = SimpleNamespace(email=None, phone=None, full_name="Candidate")
    data = {
        "summary": (
            "I am a hardworking results-driven team player and Senior Data Analyst with 6+ years of experience. "
            "I have improved reporting speed by 40% and supported a $500k portfolio. "
            "My expertise includes SQL, Python, dashboarding, stakeholder management, and financial analysis. "
            "Additional sentence that may remain because summaries allow up to four sentences. "
            "This fifth sentence must be removed from the summary."
        ),
        "skills": {"technical": [], "soft": [], "tools": []},
    }

    normalized = apply_cv_rules(data, user)
    summary = normalized["summary"]

    assert 2 <= len(re.findall(r"[^.!?]+[.!?]", summary)) <= 4
    assert len(summary.split()) <= 100
    assert not re.search(r"\b(?:I|me|my)\b", summary, re.IGNORECASE)
    assert "hardworking" not in summary.lower()
    assert "team player" not in summary.lower()
    assert "results-driven" not in summary.lower()
    assert "40%" in summary
    assert "$500k" in summary
    assert "fifth sentence" not in summary.lower()


def test_apply_cv_rules_keeps_optional_education_fields_empty():
    user = SimpleNamespace(email=None, phone=None, full_name="Candidate")
    data = {
        "education": [
            {
                "institution": "Universitas Indonesia",
                "degree": "BSc Computer Science",
                "year": "2020 - 2024",
            }
        ],
        "skills": {"technical": [], "soft": [], "tools": []},
    }

    education = apply_cv_rules(data, user)["education"][0]

    assert education["location"] == ""
    assert education["gpa"] == ""
    assert education["rank"] == ""
    assert education["coursework"] == []
    assert education["honors_awards"] == []
    assert education["activities"] == []
