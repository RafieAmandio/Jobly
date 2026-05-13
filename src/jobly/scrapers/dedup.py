import hashlib
import re

from jobly.scrapers.base import JobResult


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def compute_fingerprint(job: JobResult) -> str:
    parts = [
        normalize_text(job.title),
        normalize_text(job.company or ""),
        normalize_text(job.location or ""),
    ]
    key = "|".join(parts)
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def deduplicate_jobs(jobs: list[JobResult]) -> list[JobResult]:
    seen: set[str] = set()
    unique: list[JobResult] = []
    for job in jobs:
        fp = compute_fingerprint(job)
        if fp not in seen:
            seen.add(fp)
            unique.append(job)
    return unique
