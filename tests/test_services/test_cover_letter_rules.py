from types import SimpleNamespace
from typing import cast

from jobly.models.job import Job
from jobly.services.cover_letter import apply_cover_letter_rules


def test_apply_cover_letter_rules_injects_guideline_structure_in_english():
    job = cast(Job, SimpleNamespace(title="Software Engineer", company="Tokopedia"))
    content = (
        "I recently led the rollout of scalable Python APIs serving high-growth products.\n\n"
        "My leadership experience in campus organizations strengthened my ability to collaborate across teams.\n\n"
        "I have already worked in professional environments through internships and project delivery."
    )

    normalized = apply_cover_letter_rules(content, job, lang="en", signer_name="John Doe")
    parts = normalized.split("\n\n")

    assert parts[0] == "Subject: Application for Software Engineer at Tokopedia"
    assert parts[1] == "Dear Hiring Manager at Tokopedia,"
    assert parts[-2] == "Sincerely,"
    assert parts[-1] == "John Doe"


def test_apply_cover_letter_rules_preserves_existing_subject_recipient_and_closing():
    job = cast(Job, SimpleNamespace(title="Data Analyst", company="Financial Light"))
    content = (
        "Perihal: Lamaran Data Analyst - Financial Light\n\n"
        "Yth. HRD Financial Light\n\n"
        "Saya tertarik melamar posisi ini karena pengalaman saya relevan.\n\n"
        "Hormat saya,\n\n"
        "Dharma"
    )

    normalized = apply_cover_letter_rules(content, job, lang="id", signer_name="Dharma")
    parts = normalized.split("\n\n")

    assert parts[0] == "Perihal: Lamaran Data Analyst - Financial Light"
    assert parts[1] == "Yth. HRD Financial Light"
    assert parts[-2] == "Hormat saya,"
    assert parts[-1] == "Dharma"
