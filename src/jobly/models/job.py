import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jobly.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(500))
    company: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    work_arrangement: Mapped[str | None] = mapped_column(String(50))
    salary_min: Mapped[int | None] = mapped_column(BigInteger)
    salary_max: Mapped[int | None] = mapped_column(BigInteger)
    salary_text: Mapped[str | None] = mapped_column(String(255))
    experience_level: Mapped[str | None] = mapped_column(String(50))
    url: Mapped[str] = mapped_column(String(1000))
    posted_at: Mapped[datetime | None]
    scraped_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    expires_at: Mapped[datetime | None]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fingerprint: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

    categories: Mapped[list["JobCategory"]] = relationship(cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_jobs_scraped_at", "scraped_at"),
    )


class JobCategory(Base):
    __tablename__ = "job_categories"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), primary_key=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
