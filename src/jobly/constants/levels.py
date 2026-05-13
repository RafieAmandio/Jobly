EXPERIENCE_LEVELS = [
    {"slug": "internship", "label_id": "Magang", "label_en": "Internship"},
    {"slug": "fresh_graduate", "label_id": "Fresh Graduate", "label_en": "Fresh Graduate"},
    {"slug": "junior", "label_id": "Junior (1-3 tahun)", "label_en": "Junior (1-3 years)"},
    {"slug": "mid", "label_id": "Mid-Level (3-5 tahun)", "label_en": "Mid-Level (3-5 years)"},
    {"slug": "senior", "label_id": "Senior (5-10 tahun)", "label_en": "Senior (5-10 years)"},
    {"slug": "lead", "label_id": "Lead/Supervisor", "label_en": "Lead/Supervisor"},
    {"slug": "manager", "label_id": "Manajer", "label_en": "Manager"},
    {"slug": "senior_manager", "label_id": "Manajer Senior", "label_en": "Senior Manager"},
    {"slug": "director", "label_id": "Direktur", "label_en": "Director"},
    {"slug": "vp", "label_id": "VP", "label_en": "VP"},
    {"slug": "c_level", "label_id": "C-Level (CEO/CTO/CFO)", "label_en": "C-Level (CEO/CTO/CFO)"},
    {"slug": "freelance", "label_id": "Freelance/Kontrak", "label_en": "Freelance/Contract"},
]

SALARY_RANGES = [
    {"slug": "below_5m", "label": "< Rp 5 juta", "min": 0, "max": 5_000_000},
    {"slug": "5m_10m", "label": "Rp 5 - 10 juta", "min": 5_000_000, "max": 10_000_000},
    {"slug": "10m_15m", "label": "Rp 10 - 15 juta", "min": 10_000_000, "max": 15_000_000},
    {"slug": "15m_25m", "label": "Rp 15 - 25 juta", "min": 15_000_000, "max": 25_000_000},
    {"slug": "25m_40m", "label": "Rp 25 - 40 juta", "min": 25_000_000, "max": 40_000_000},
    {"slug": "40m_60m", "label": "Rp 40 - 60 juta", "min": 40_000_000, "max": 60_000_000},
    {"slug": "60m_100m", "label": "Rp 60 - 100 juta", "min": 60_000_000, "max": 100_000_000},
    {"slug": "above_100m", "label": "> Rp 100 juta", "min": 100_000_000, "max": None},
    {"slug": "negotiable", "label": "Negotiable", "min": None, "max": None},
]

WORK_ARRANGEMENTS = [
    {"name": "wfo", "label_id": "WFO (Work From Office)", "label_en": "On-site"},
    {"name": "wfh", "label_id": "WFH (Work From Home)", "label_en": "Remote"},
    {"name": "hybrid", "label_id": "Hybrid", "label_en": "Hybrid"},
    {"name": "flexible", "label_id": "Fleksibel", "label_en": "Flexible"},
    {"name": "freelance", "label_id": "Freelance", "label_en": "Freelance"},
    {"name": "contract", "label_id": "Kontrak", "label_en": "Contract"},
    {"name": "internship", "label_id": "Magang", "label_en": "Internship"},
]

CREDIT_PACKAGES = [
    {"name": "starter", "credits": 5, "price_idr": 25_000, "label": "Starter"},
    {"name": "popular", "credits": 15, "price_idr": 60_000, "label": "Popular"},
    {"name": "pro", "credits": 50, "price_idr": 150_000, "label": "Pro"},
    {"name": "bulk", "credits": 100, "price_idr": 250_000, "label": "Bulk"},
]
