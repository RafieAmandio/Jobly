import pytest

from jobly.services.notification import format_job_card


def test_format_job_card_id(mock_job):
    text = format_job_card(mock_job, "id")
    assert "Software Engineer" in text
    assert "Tokopedia" in text
    assert "Jakarta Selatan" in text
    assert "Rp 15-25 juta/bulan" in text
    assert "Linkedin" in text


def test_format_job_card_en(mock_job):
    text = format_job_card(mock_job, "en")
    assert "Software Engineer" in text
    assert "Tokopedia" in text


def test_format_job_card_no_salary(mock_job):
    mock_job.salary_text = None
    mock_job.salary_min = None
    mock_job.salary_max = None
    text = format_job_card(mock_job, "id")
    assert "Software Engineer" in text
    assert "💰" not in text


def test_format_job_card_no_company(mock_job):
    mock_job.company = None
    text = format_job_card(mock_job, "id")
    assert "Unknown" in text
