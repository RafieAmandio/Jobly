import pytest

from jobly.scrapers.base import JobResult
from jobly.scrapers.dedup import compute_fingerprint, deduplicate_jobs


def _make_job(title: str, company: str, location: str, source: str = "test") -> JobResult:
    return JobResult(
        external_id=f"{source}-{hash(title)}",
        source=source,
        title=title,
        company=company,
        location=location,
        url=f"https://example.com/{hash(title)}",
    )


def test_compute_fingerprint_deterministic():
    job = _make_job("Software Engineer", "Tokopedia", "Jakarta")
    fp1 = compute_fingerprint(job)
    fp2 = compute_fingerprint(job)
    assert fp1 == fp2


def test_compute_fingerprint_case_insensitive():
    job1 = _make_job("Software Engineer", "Tokopedia", "Jakarta")
    job2 = _make_job("software engineer", "tokopedia", "jakarta")
    assert compute_fingerprint(job1) == compute_fingerprint(job2)


def test_compute_fingerprint_different_jobs():
    job1 = _make_job("Software Engineer", "Tokopedia", "Jakarta")
    job2 = _make_job("Data Scientist", "Gojek", "Bandung")
    assert compute_fingerprint(job1) != compute_fingerprint(job2)


def test_deduplicate_removes_duplicates():
    jobs = [
        _make_job("Software Engineer", "Tokopedia", "Jakarta", "linkedin"),
        _make_job("Software Engineer", "Tokopedia", "Jakarta", "indeed"),
        _make_job("Data Scientist", "Gojek", "Bandung", "linkedin"),
    ]
    unique = deduplicate_jobs(jobs)
    assert len(unique) == 2


def test_deduplicate_preserves_first():
    jobs = [
        _make_job("Software Engineer", "Tokopedia", "Jakarta", "linkedin"),
        _make_job("Software Engineer", "Tokopedia", "Jakarta", "indeed"),
    ]
    unique = deduplicate_jobs(jobs)
    assert unique[0].source == "linkedin"


def test_deduplicate_empty():
    assert deduplicate_jobs([]) == []
