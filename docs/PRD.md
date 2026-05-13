# Jobly — Product Requirements Document

**Version:** 1.0
**Date:** 2026-05-13
**Author:** Dio + Claude
**Status:** Draft

---

## 1. Product Overview

### 1.1 Vision
Jobly is a Telegram bot that helps Indonesian job seekers find relevant opportunities and generate tailored CVs and cover letters using AI. Users subscribe to job categories, receive real-time notifications when matching jobs are scraped, and can spend credits to tailor their CV or generate a cover letter for any specific job posting.

### 1.2 Problem Statement
Indonesian job seekers spend hours manually browsing multiple job boards (JobStreet, Glints, LinkedIn, etc.), and even more time customizing their CV for each application. Most apply with a generic CV, reducing their chances. Jobly consolidates job discovery across platforms and automates CV tailoring — saving time and improving application quality.

### 1.3 Target Market
- **Primary:** Indonesian job seekers (fresh graduates to senior level)
- **Geography:** Indonesia (Jabodetabek focus, expanding nationwide)
- **Languages:** Bahasa Indonesia and English
- **Platform:** Telegram (mobile-first, high adoption in Indonesia)

### 1.4 Key Differentiators
- Multi-source job aggregation in one Telegram chat
- AI-powered CV tailoring using Kimi 2.6 (cost-effective, high quality)
- Credit-based pay-as-you-go model (affordable for Indonesian market)
- Bilingual support (ID/EN)

---

## 2. User Personas

### Persona 1: Fresh Graduate Andi
- 22 years old, just graduated from UI (Universitas Indonesia)
- Looking for his first job in tech/data science
- Applies to 20+ jobs per week with the same generic CV
- Budget-conscious, prefers pay-per-use over subscriptions
- Heavy Telegram user

### Persona 2: Mid-Career Rina
- 30 years old, 6 years experience in marketing
- Wants to switch to a digital marketing role at a tech company
- Knows her CV needs tailoring but doesn't have time
- Willing to pay for tools that save her time
- Uses both Indonesian and English for job applications

### Persona 3: Senior Professional Budi
- 40 years old, engineering manager
- Selectively looking — only wants to be notified of director-level roles
- Values quality over quantity
- Needs bilingual CV output (Indonesian companies + multinational)

---

## 3. User Journey

```
┌─────────────────────────────────────────────────────────────┐
│                      USER JOURNEY                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. DISCOVERY                                               │
│     User finds Jobly bot on Telegram                        │
│     ↓                                                       │
│  2. REGISTRATION                                            │
│     /start → Collects name, phone (optional), email         │
│     ↓                                                       │
│  3. ONBOARDING                                              │
│     Step-by-step preference setup via inline keyboards:     │
│     → Job categories (multi-select)                         │
│     → Experience level                                      │
│     → Preferred locations                                   │
│     → Work arrangement (WFO/WFH/Hybrid)                     │
│     → Salary range expectation                              │
│     → Preferred language for notifications                  │
│     ↓                                                       │
│  4. CV UPLOAD                                               │
│     Upload PDF or paste plain text                          │
│     Bot parses and stores structured CV data                │
│     ↓                                                       │
│  5. PASSIVE JOB MATCHING                                    │
│     Scraper runs hourly → matches against preferences       │
│     → Sends notification with job summary                   │
│     → Inline buttons: [Tailor CV] [Cover Letter] [Details]  │
│     ↓                                                       │
│  6. CV TAILORING (1 credit)                                 │
│     User clicks "Tailor CV" on a job notification           │
│     → AI rewrites CV content to match job description       │
│     → Generates DOCX + PDF                                  │
│     → Sends files in chat                                   │
│     ↓                                                       │
│  7. COVER LETTER (1 credit)                                 │
│     User clicks "Cover Letter"                              │
│     → AI generates targeted cover letter                    │
│     → Generates DOCX + PDF                                  │
│     → Sends files in chat                                   │
│     ↓                                                       │
│  8. CREDIT TOP-UP                                           │
│     When credits run low → prompt to buy more               │
│     → Xendit payment (QRIS, GoPay, OVO, VA, etc.)           │
│     → Credits added after payment confirmation              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Feature Breakdown

### 4.1 Registration & Onboarding

| Feature | Description | Priority |
|---------|-------------|----------|
| `/start` command | Initiates registration flow | P0 |
| Name collection | Full name via text input | P0 |
| Email collection | Email for account recovery / receipts | P0 |
| Phone (optional) | Indonesian phone number | P1 |
| Job category selection | Multi-select from predefined list via paginated inline keyboard | P0 |
| Experience level | Single select (Internship → C-Level) | P0 |
| Location preference | Multi-select cities + "Remote/Anywhere" option | P0 |
| Work arrangement | Multi-select: WFO, WFH, Hybrid, Freelance, Contract | P0 |
| Salary range | Select from predefined IDR ranges | P1 |
| Language preference | ID / EN / Both — for notifications and document output | P0 |
| CV upload | Accept PDF file or plain text message | P0 |
| Onboarding completion | Summary of preferences + confirmation | P0 |

### 4.2 Profile & Preference Management

| Feature | Description | Priority |
|---------|-------------|----------|
| `/profile` | View current profile and preferences | P0 |
| `/edit_preferences` | Re-enter preference selection flow | P0 |
| `/upload_cv` | Upload a new CV (replaces existing) | P0 |
| `/view_cv` | View parsed CV summary | P1 |
| `/language` | Switch bot language (ID/EN) | P0 |
| `/delete_account` | Delete all data (GDPR-style compliance) | P1 |

### 4.3 Job Discovery & Notifications

| Feature | Description | Priority |
|---------|-------------|----------|
| Hourly job scraping | Scrape new jobs from all sources every hour | P0 |
| Job matching engine | Match scraped jobs against user preferences | P0 |
| Telegram notification | Send matched jobs with summary card | P0 |
| Job detail view | Inline button to expand full job details | P0 |
| Source link | Direct link to original job posting | P0 |
| Batch notifications | Group multiple matches into a single message (max 5 per batch) | P1 |
| `/browse` | Manually browse recent jobs matching preferences | P1 |
| Duplicate detection | Don't notify same job twice (cross-source dedup) | P0 |

**Job Notification Card Format:**
```
🏢 Software Engineer — Tokopedia
📍 Jakarta (Hybrid)
💰 IDR 15-25 juta/bulan
📅 Posted: 2 hours ago
🔗 Source: LinkedIn

Brief description (2-3 lines)...

[📄 Tailor CV — 1 credit] [✉️ Cover Letter — 1 credit]
[🔗 View Original] [❌ Not Interested]
```

### 4.4 CV Tailoring

| Feature | Description | Priority |
|---------|-------------|----------|
| One-click tailor | Triggered from job notification button | P0 |
| AI rewriting | Kimi 2.6 rewrites CV bullets, summary, and skills to match JD | P0 |
| DOCX generation | Professional CV template as .docx | P0 |
| PDF generation | Same CV rendered as .pdf | P0 |
| Credit deduction | 1 credit per tailoring | P0 |
| Insufficient credit handling | Prompt to top up if balance = 0 | P0 |
| Tailoring history | `/history` to view past tailored CVs | P2 |
| Template selection | Multiple CV templates to choose from | P2 |

### 4.5 Cover Letter Generation

| Feature | Description | Priority |
|---------|-------------|----------|
| One-click generate | Triggered from job notification button | P0 |
| AI generation | Kimi 2.6 generates cover letter matching JD + user background | P0 |
| DOCX output | Professional cover letter as .docx | P0 |
| PDF output | Same cover letter as .pdf | P0 |
| Credit deduction | 1 credit per cover letter | P0 |
| Tone selection | Formal / Semi-formal / Casual | P2 |
| Language choice | Generate in ID or EN regardless of bot language setting | P1 |

### 4.6 Credit & Payment System

| Feature | Description | Priority |
|---------|-------------|----------|
| `/credits` | View current credit balance | P0 |
| `/topup` | Show available credit packages | P0 |
| Xendit integration | Payment via Indonesian methods | P0 |
| Webhook handling | Auto-credit after successful payment | P0 |
| Payment receipt | Send confirmation message with details | P0 |
| Transaction history | `/transactions` to view payment + usage history | P1 |
| Free welcome credits | 3 free credits on registration | P0 |
| Referral credits | Earn 2 credits for each referred user who registers | P2 |

### 4.7 Admin Features

| Feature | Description | Priority |
|---------|-------------|----------|
| User analytics | Total users, active users, conversion rates | P1 |
| Scraper monitoring | Job counts, error rates, source health | P1 |
| Revenue dashboard | Credits sold, revenue, popular packages | P1 |
| Manual credit adjustment | Admin can add/remove credits for support cases | P1 |
| Broadcast message | Send announcement to all users | P2 |
| Job source management | Enable/disable scrapers per source | P1 |

---

## 5. Credit & Pricing Model (Mock)

### 5.1 Credit Actions

| Action | Cost |
|--------|------|
| Tailor CV to a job | 1 credit |
| Generate cover letter | 1 credit |

### 5.2 Credit Packages

| Package | Credits | Price (IDR) | Per Credit | Savings |
|---------|---------|-------------|------------|---------|
| Starter | 5 | 25,000 | 5,000 | — |
| Popular | 15 | 60,000 | 4,000 | 20% |
| Pro | 50 | 150,000 | 3,000 | 40% |
| Bulk | 100 | 250,000 | 2,500 | 50% |

### 5.3 Free Credits
- **Welcome bonus:** 3 credits on registration (enough to try the service)
- **Referral bonus:** 2 credits per successful referral (referred user must complete onboarding)

### 5.4 Payment Methods (via Xendit)
- QRIS (all e-wallets)
- GoPay
- OVO
- ShopeePay
- Bank Transfer (Virtual Account — BCA, BNI, BRI, Mandiri, Permata)
- Credit/Debit Card
- Alfamart/Indomaret (retail)

---

## 6. Technical Architecture

### 6.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         JOBLY ARCHITECTURE                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐     ┌──────────────────┐     ┌──────────────────┐      │
│  │Telegram  │────▶│  aiogram v3       │────▶│  Supabase        │      │
│  │  Users   │◀────│  (Bot Server)     │◀────│  (PostgreSQL)    │      │
│  └─────────┘     │                    │     │                  │      │
│                  │  Handlers          │     │  Users           │      │
│                  │  Middlewares       │     │  Jobs            │      │
│                  │  FSM States        │     │  Credits         │      │
│                  │  Inline Keyboards  │     │  Transactions    │      │
│                  └────────┬───────────┘     │  CVs             │      │
│                           │                 │  Preferences     │      │
│                           │                 │  Notifications   │      │
│                  ┌────────▼───────────┐     └──────────────────┘      │
│                  │  Background Workers │                              │
│                  │  (arq + Redis)      │     ┌──────────────────┐     │
│                  │                     │────▶│  Kimi 2.6 API    │     │
│                  │  • Job scraping     │     │  (CV/CL gen)     │     │
│                  │  • Job matching     │     └──────────────────┘     │
│                  │  • CV tailoring     │                              │
│                  │  • Doc generation   │     ┌──────────────────┐     │
│                  │  • Notifications    │────▶│  Xendit API      │     │
│                  └────────┬───────────┘     │  (Payments)      │     │
│                           │                 └──────────────────┘     │
│                  ┌────────▼───────────┐                              │
│                  │  Scheduled Tasks    │     ┌──────────────────┐     │
│                  │  (APScheduler)      │────▶│  Job Sources     │     │
│                  │                     │     │  • SerpAPI       │     │
│                  │  • Hourly scrape    │     │  • Direct scrape │     │
│                  │  • Match & notify   │     │  • APIs          │     │
│                  │  • Stale job cleanup│     └──────────────────┘     │
│                  └────────────────────┘                               │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │  Supabase Storage │  │  Redis            │                        │
│  │  (CV files)       │  │  (FSM, cache,     │                        │
│  │                   │  │   job queue)       │                        │
│  └──────────────────┘  └──────────────────┘                         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 6.2 Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Bot Framework** | aiogram v3 | Async-native, first-class FSM, middleware, routers. Production standard for Python Telegram bots |
| **Language** | Python 3.12+ | Ecosystem, AI library support |
| **Package Manager** | uv | Fastest modern Python tool — handles venvs, lockfiles, deps. Replaced Poetry in 2025 |
| **Database** | PostgreSQL via Supabase | Managed, free tier available, built-in auth & storage |
| **DB Access** | SQLAlchemy 2.0 (async) + asyncpg | Full SQL power, migrations via Alembic, type-safe ORM |
| **Cache/Queue** | Redis | FSM state storage, arq job queue, scrape caching |
| **Task Queue** | arq | Lightweight async Redis queue for heavy jobs (doc gen, scraping) |
| **Scheduler** | APScheduler v4 | Async-native scheduled tasks (hourly scraping) |
| **AI Model** | Kimi 2.6 (Moonshot AI) | OpenAI-compatible API, cost-effective, good multilingual support |
| **AI SDK** | openai Python SDK | Kimi 2.6 API is OpenAI-compatible — just change base_url |
| **Payments** | Xendit REST API | Dominant Indonesian payment gateway, supports all local methods |
| **HTTP Client** | httpx | Async HTTP for Xendit API, scraping |
| **DOCX Generation** | python-docx | Full control over Word document formatting |
| **PDF Generation** | WeasyPrint | HTML/CSS to PDF — professional, pixel-perfect CV rendering |
| **CV Parsing** | pdfplumber | Extract text from uploaded PDF CVs |
| **Web Scraping** | Apify + httpx + BeautifulSoup4 | Apify actors for LinkedIn/Indeed/Glassdoor; direct scraping for local boards. Provider-agnostic adapter pattern |
| **Deployment** | VPS (Ubuntu) + Docker Compose | Simple, cost-effective for Indonesia-region hosting |
| **Reverse Proxy** | Nginx | Webhook endpoint, SSL termination |
| **Monitoring** | Sentry + structured logging | Error tracking, performance monitoring |

### 6.3 Project Structure

```
jobly/
├── src/
│   └── jobly/
│       ├── __init__.py
│       ├── main.py                    # Entry point
│       ├── config.py                  # Settings via pydantic-settings
│       ├── bot/
│       │   ├── __init__.py
│       │   ├── handlers/
│       │   │   ├── __init__.py
│       │   │   ├── start.py           # /start, registration
│       │   │   ├── onboarding.py      # Preference setup FSM
│       │   │   ├── profile.py         # /profile, /edit_preferences
│       │   │   ├── cv.py              # /upload_cv, /view_cv
│       │   │   ├── credits.py         # /credits, /topup
│       │   │   ├── jobs.py            # /browse, job callbacks
│       │   │   ├── tailor.py          # CV tailoring callback
│       │   │   ├── cover_letter.py    # Cover letter callback
│       │   │   └── admin.py           # Admin commands
│       │   ├── keyboards/
│       │   │   ├── __init__.py
│       │   │   ├── onboarding.py      # Category/location/etc keyboards
│       │   │   ├── jobs.py            # Job card action buttons
│       │   │   └── payments.py        # Credit package selection
│       │   ├── middlewares/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py            # User registration check
│       │   │   ├── i18n.py            # Language middleware
│       │   │   └── throttle.py        # Rate limiting
│       │   ├── states/
│       │   │   ├── __init__.py
│       │   │   ├── onboarding.py      # Onboarding FSM states
│       │   │   └── cv_upload.py       # CV upload FSM states
│       │   └── filters/
│       │       ├── __init__.py
│       │       └── admin.py           # Admin-only filter
│       ├── services/
│       │   ├── __init__.py
│       │   ├── user.py                # User CRUD
│       │   ├── cv_parser.py           # PDF text extraction
│       │   ├── cv_tailor.py           # AI CV tailoring orchestration
│       │   ├── cover_letter.py        # AI cover letter generation
│       │   ├── doc_generator.py       # DOCX + PDF file generation
│       │   ├── job_matcher.py         # Match jobs to user preferences
│       │   ├── credit.py              # Credit balance management
│       │   ├── payment.py             # Xendit payment creation + webhook
│       │   └── notification.py        # Send job notifications to users
│       ├── scrapers/
│       │   ├── __init__.py
│       │   ├── base.py                # JobProvider protocol + JobResult schema
│       │   ├── registry.py            # Provider registry + factory
│       │   ├── providers/
│       │   │   ├── __init__.py
│       │   │   ├── apify.py           # Apify adapter (LinkedIn, Indeed, Glassdoor, JobStreet)
│       │   │   └── direct.py          # Direct scrape adapter (Glints, Kalibrr, Karir.com)
│       │   ├── parsers/
│       │   │   ├── __init__.py
│       │   │   ├── glints.py          # Glints HTML parser
│       │   │   ├── kalibrr.py         # Kalibrr HTML parser
│       │   │   └── karir.py           # Karir.com HTML parser
│       │   └── dedup.py               # Cross-source deduplication
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py                # User SQLAlchemy model
│       │   ├── job.py                 # Job listing model
│       │   ├── cv.py                  # CV data model
│       │   ├── credit.py              # Credit + transaction models
│       │   ├── preference.py          # User preference model
│       │   └── notification.py        # Notification log model
│       ├── db/
│       │   ├── __init__.py
│       │   ├── session.py             # Async SQLAlchemy session
│       │   └── migrations/            # Alembic migrations
│       ├── workers/
│       │   ├── __init__.py
│       │   ├── scrape.py              # Job scraping worker
│       │   ├── match.py               # Job matching worker
│       │   ├── tailor.py              # CV tailoring worker
│       │   └── notify.py              # Notification dispatch worker
│       ├── templates/
│       │   ├── cv/                    # HTML/CSS CV templates
│       │   └── cover_letter/          # HTML/CSS cover letter templates
│       ├── i18n/
│       │   ├── id.py                  # Indonesian strings
│       │   └── en.py                  # English strings
│       └── constants/
│           ├── __init__.py
│           ├── categories.py          # Job category definitions
│           ├── locations.py           # City/region definitions
│           └── levels.py              # Experience level definitions
├── tests/
│   ├── conftest.py
│   ├── test_services/
│   ├── test_scrapers/
│   └── test_handlers/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

---

## 7. Database Schema

### 7.1 Entity Relationship

```
users ──────────────┬── user_preferences
  │                 │
  ├── cvs           ├── user_categories (M2M)
  │                 │
  ├── credit_       ├── user_locations (M2M)
  │   transactions  │
  │                 └── user_work_arrangements (M2M)
  ├── tailoring_
  │   history
  │
  └── notification_
      log

jobs ──── job_categories (M2M)

categories (predefined)
locations (predefined)
```

### 7.2 Table Definitions

```sql
-- Users
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id     BIGINT UNIQUE NOT NULL,
    telegram_username VARCHAR(255),
    full_name       VARCHAR(255) NOT NULL,
    email           VARCHAR(255),
    phone           VARCHAR(20),
    language        VARCHAR(2) DEFAULT 'id',  -- 'id' or 'en'
    credit_balance  INTEGER DEFAULT 3,        -- welcome credits
    referral_code   VARCHAR(20) UNIQUE,
    referred_by     UUID REFERENCES users(id),
    onboarding_completed BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- User Preferences
CREATE TABLE user_preferences (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    experience_level VARCHAR(50),              -- 'fresh_graduate', 'junior', etc.
    salary_min      BIGINT,                    -- in IDR
    salary_max      BIGINT,
    notification_language VARCHAR(2) DEFAULT 'id',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Predefined Categories
CREATE TABLE categories (
    id              SERIAL PRIMARY KEY,
    name_id         VARCHAR(100) NOT NULL,     -- Indonesian name
    name_en         VARCHAR(100) NOT NULL,     -- English name
    slug            VARCHAR(100) UNIQUE NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE
);

-- User → Category (M2M)
CREATE TABLE user_categories (
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id     INTEGER REFERENCES categories(id),
    PRIMARY KEY (user_id, category_id)
);

-- Predefined Locations
CREATE TABLE locations (
    id              SERIAL PRIMARY KEY,
    city            VARCHAR(100) NOT NULL,
    region          VARCHAR(100),             -- e.g., 'Jabodetabek'
    is_active       BOOLEAN DEFAULT TRUE
);

-- User → Location (M2M)
CREATE TABLE user_locations (
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    location_id     INTEGER REFERENCES locations(id),
    PRIMARY KEY (user_id, location_id)
);

-- Work Arrangements
CREATE TABLE work_arrangements (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(50) UNIQUE NOT NULL   -- 'wfo', 'wfh', 'hybrid', etc.
);

-- User → Work Arrangement (M2M)
CREATE TABLE user_work_arrangements (
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    arrangement_id  INTEGER REFERENCES work_arrangements(id),
    PRIMARY KEY (user_id, arrangement_id)
);

-- CVs
CREATE TABLE cvs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    raw_text        TEXT NOT NULL,             -- extracted/pasted text
    file_path       VARCHAR(500),             -- Supabase Storage path (if PDF uploaded)
    parsed_data     JSONB,                    -- structured CV data from parsing
    is_current      BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs
CREATE TABLE jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id     VARCHAR(255),             -- ID from source platform
    source          VARCHAR(50) NOT NULL,      -- 'linkedin', 'jobstreet', etc.
    title           VARCHAR(500) NOT NULL,
    company         VARCHAR(255),
    description     TEXT,
    location        VARCHAR(255),
    work_arrangement VARCHAR(50),
    salary_min      BIGINT,
    salary_max      BIGINT,
    salary_text     VARCHAR(255),             -- raw salary string
    experience_level VARCHAR(50),
    url             VARCHAR(1000) NOT NULL,    -- original posting URL
    posted_at       TIMESTAMPTZ,
    scraped_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    fingerprint     VARCHAR(64) UNIQUE,       -- for deduplication (hash of title+company+location)
    raw_data        JSONB                     -- full scraped data for reference
);

CREATE INDEX idx_jobs_fingerprint ON jobs(fingerprint);
CREATE INDEX idx_jobs_scraped_at ON jobs(scraped_at);
CREATE INDEX idx_jobs_source ON jobs(source);

-- Job → Category (M2M)
CREATE TABLE job_categories (
    job_id          UUID REFERENCES jobs(id) ON DELETE CASCADE,
    category_id     INTEGER REFERENCES categories(id),
    confidence      FLOAT DEFAULT 1.0,        -- AI classification confidence
    PRIMARY KEY (job_id, category_id)
);

-- Credit Transactions
CREATE TABLE credit_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    amount          INTEGER NOT NULL,          -- positive = credit, negative = debit
    balance_after   INTEGER NOT NULL,
    type            VARCHAR(50) NOT NULL,      -- 'purchase', 'welcome', 'referral', 'tailor_cv', 'cover_letter', 'admin_adjustment'
    reference_id    VARCHAR(255),             -- Xendit invoice ID or job ID
    description     VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_credit_tx_user ON credit_transactions(user_id, created_at);

-- Payment Records (Xendit)
CREATE TABLE payments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    xendit_invoice_id VARCHAR(255) UNIQUE,
    xendit_external_id VARCHAR(255) UNIQUE,
    package_name    VARCHAR(50),
    credits         INTEGER NOT NULL,
    amount_idr      BIGINT NOT NULL,
    status          VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'paid', 'expired', 'failed'
    payment_method  VARCHAR(50),
    paid_at         TIMESTAMPTZ,
    xendit_callback_data JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tailoring History
CREATE TABLE tailoring_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id          UUID REFERENCES jobs(id),
    type            VARCHAR(20) NOT NULL,      -- 'cv' or 'cover_letter'
    output_docx_path VARCHAR(500),
    output_pdf_path VARCHAR(500),
    ai_prompt       TEXT,
    ai_response     TEXT,
    tokens_used     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Notification Log
CREATE TABLE notification_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    job_id          UUID REFERENCES jobs(id),
    sent_at         TIMESTAMPTZ DEFAULT NOW(),
    message_id      BIGINT,                   -- Telegram message ID
    UNIQUE(user_id, job_id)                   -- prevent duplicate notifications
);
```

---

## 8. API Integrations

### 8.1 Kimi 2.6 (Moonshot AI)

**Endpoint:** `https://api.moonshot.cn/v1` (OpenAI-compatible)
**Auth:** API key via `Authorization: Bearer <key>`
**Usage:** Via `openai` Python SDK with custom `base_url`

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="sk-...",
    base_url="https://api.moonshot.cn/v1",
)

response = await client.chat.completions.create(
    model="kimi-2.6",
    messages=[
        {"role": "system", "content": TAILOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"CV:\n{cv_text}\n\nJob Description:\n{jd_text}"},
    ],
    temperature=0.7,
)
```

**Prompts will be designed for:**
1. CV tailoring — rewrite bullets, summary, skills to match JD
2. Cover letter generation — professional, personalized
3. Job category classification — classify scraped jobs into categories
4. CV parsing — structure raw CV text into sections

### 8.2 Xendit Payment

**Endpoint:** `https://api.xendit.co`
**Auth:** Basic auth with secret key

**Flow:**
1. User selects credit package → bot calls Xendit Create Invoice API
2. Xendit returns invoice URL → bot sends payment link to user
3. User pays via preferred method
4. Xendit sends webhook to our endpoint (`POST /webhooks/xendit`)
5. We verify callback token, credit user's balance, send confirmation

**Key endpoints:**
- `POST /v2/invoices` — Create payment invoice
- Webhook: invoice status callback

### 8.3 Job Scraping — Provider-Agnostic Architecture

All scrapers implement a common `JobProvider` protocol. The job engine never talks to a specific
scraper — it talks to the protocol. Providers can be swapped, added, or removed via config without
touching the matching/notification layer.

```python
class JobResult(BaseModel):
    external_id: str
    source: str
    title: str
    company: str
    description: str
    location: str
    url: str
    salary_min: int | None
    salary_max: int | None
    work_arrangement: str | None
    posted_at: datetime | None

class JobProvider(Protocol):
    name: str
    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]: ...
    async def health_check(self) -> bool: ...
```

**Registered Providers:**

| Source | Provider | Method | Notes |
|--------|----------|--------|-------|
| LinkedIn | ApifyProvider | Apify actor `apify/linkedin-jobs-scraper` | Pay-per-use, reliable |
| Indeed | ApifyProvider | Apify actor `misceres/indeed-scraper` | Pay-per-use |
| Glassdoor | ApifyProvider | Apify actor `easyapi/glassdoor-jobs` | Pay-per-use |
| JobStreet | ApifyProvider | Apify actor or DirectScrapeProvider | Fallback to direct |
| Glints | DirectScrapeProvider | httpx + custom parser | Free, self-hosted |
| Kalibrr | DirectScrapeProvider | httpx + custom parser | Free, self-hosted |
| Karir.com | DirectScrapeProvider | httpx + custom parser | Free, self-hosted |

**Provider config (in .env or DB):**
```json
{
  "providers": {
    "linkedin": { "type": "apify", "actor_id": "apify/linkedin-jobs-scraper", "enabled": true },
    "glints": { "type": "direct", "parser": "glints", "enabled": true }
  }
}
```

To swap a provider (e.g., move LinkedIn from Apify to RapidAPI), just create a new
`RapidAPIProvider` implementing `JobProvider` and update the config. Zero changes to
the rest of the codebase.

---

## 9. Predefined Lists

### 9.1 Job Categories (40)

| # | Slug | Indonesian | English |
|---|------|-----------|---------|
| 1 | technology | Teknologi/IT | Technology/IT |
| 2 | data_science_ai | Data Science/AI | Data Science/AI |
| 3 | software_engineering | Rekayasa Perangkat Lunak | Software Engineering |
| 4 | finance_accounting | Keuangan/Akuntansi | Finance/Accounting |
| 5 | banking | Perbankan | Banking |
| 6 | fintech | Fintech | Fintech |
| 7 | marketing | Pemasaran | Marketing |
| 8 | digital_marketing | Pemasaran Digital | Digital Marketing |
| 9 | sales | Penjualan | Sales |
| 10 | human_resources | Sumber Daya Manusia | Human Resources |
| 11 | customer_service | Layanan Pelanggan | Customer Service |
| 12 | administration | Administrasi/Sekretaris | Administration |
| 13 | engineering | Teknik (Sipil/Mesin/Elektro) | Engineering (Civil/Mech/Elec) |
| 14 | manufacturing | Manufaktur/Produksi | Manufacturing/Production |
| 15 | quality_assurance | Penjaminan Mutu | Quality Assurance |
| 16 | logistics | Logistik/Rantai Pasok | Logistics/Supply Chain |
| 17 | healthcare | Kesehatan/Medis | Healthcare/Medical |
| 18 | pharmaceutical | Farmasi | Pharmaceutical |
| 19 | education | Pendidikan/Pengajaran | Education/Teaching |
| 20 | research | Penelitian & Pengembangan | Research & Development |
| 21 | legal | Hukum | Legal |
| 22 | creative_design | Kreatif/Desain | Creative/Design |
| 23 | media | Media/Jurnalistik | Media/Journalism |
| 24 | hospitality | Perhotelan/Pariwisata | Hospitality/Tourism |
| 25 | food_beverage | Makanan & Minuman | Food & Beverage |
| 26 | retail | Ritel | Retail |
| 27 | ecommerce | E-commerce | E-commerce |
| 28 | real_estate | Properti/Real Estat | Real Estate/Property |
| 29 | construction | Konstruksi | Construction |
| 30 | telecommunications | Telekomunikasi | Telecommunications |
| 31 | automotive | Otomotif | Automotive |
| 32 | mining | Pertambangan/Migas | Mining/Oil & Gas |
| 33 | agriculture | Pertanian/Perkebunan | Agriculture/Plantation |
| 34 | environment | Lingkungan/Keberlanjutan | Environmental/Sustainability |
| 35 | insurance | Asuransi | Insurance |
| 36 | consulting | Konsultansi | Consulting |
| 37 | government | Pemerintahan/Sektor Publik | Government/Public Sector |
| 38 | social_ngo | Sosial/NGO | Social Work/NGO |
| 39 | fmcg | FMCG | FMCG |
| 40 | aviation | Penerbangan | Aviation/Airlines |

### 9.2 Experience Levels

| Slug | Indonesian | English |
|------|-----------|---------|
| internship | Magang | Internship |
| fresh_graduate | Fresh Graduate | Fresh Graduate |
| junior | Junior (1-3 tahun) | Junior (1-3 years) |
| mid | Mid-Level (3-5 tahun) | Mid-Level (3-5 years) |
| senior | Senior (5-10 tahun) | Senior (5-10 years) |
| lead | Lead/Supervisor | Lead/Supervisor |
| manager | Manajer | Manager |
| senior_manager | Manajer Senior | Senior Manager |
| director | Direktur | Director |
| vp | VP | VP |
| c_level | C-Level (CEO/CTO/CFO) | C-Level (CEO/CTO/CFO) |
| freelance | Freelance/Kontrak | Freelance/Contract |

### 9.3 Locations

| City | Region |
|------|--------|
| Jakarta Selatan | Jabodetabek |
| Jakarta Pusat | Jabodetabek |
| Jakarta Barat | Jabodetabek |
| Jakarta Timur | Jabodetabek |
| Jakarta Utara | Jabodetabek |
| Tangerang | Jabodetabek |
| Bekasi | Jabodetabek |
| Depok | Jabodetabek |
| Bogor | Jabodetabek |
| Bandung | Jawa Barat |
| Surabaya | Jawa Timur |
| Semarang | Jawa Tengah |
| Yogyakarta | DIY |
| Solo | Jawa Tengah |
| Malang | Jawa Timur |
| Medan | Sumatera Utara |
| Palembang | Sumatera Selatan |
| Makassar | Sulawesi Selatan |
| Denpasar/Bali | Bali |
| Balikpapan | Kalimantan Timur |
| Batam | Kepulauan Riau |
| Cikarang | Jabodetabek |
| Remote / Anywhere | — |

### 9.4 Work Arrangements

| Slug | Indonesian | English |
|------|-----------|---------|
| wfo | WFO (Work From Office) | On-site |
| wfh | WFH (Work From Home) | Remote |
| hybrid | Hybrid | Hybrid |
| flexible | Fleksibel | Flexible |
| freelance | Freelance | Freelance |
| contract | Kontrak | Contract |
| internship | Magang | Internship |

### 9.5 Salary Ranges (IDR/month)

| Slug | Label |
|------|-------|
| below_5m | < Rp 5 juta |
| 5m_10m | Rp 5 - 10 juta |
| 10m_15m | Rp 10 - 15 juta |
| 15m_25m | Rp 15 - 25 juta |
| 25m_40m | Rp 25 - 40 juta |
| 40m_60m | Rp 40 - 60 juta |
| 60m_100m | Rp 60 - 100 juta |
| above_100m | > Rp 100 juta |
| negotiable | Negotiable |

---

## 10. AI Prompt Strategy

### 10.1 CV Tailoring Prompt (Kimi 2.6)

```
System: You are an expert CV writer specializing in the Indonesian job market.
You tailor CVs to match specific job descriptions while keeping the content
truthful to the candidate's actual experience.

Instructions:
1. Analyze the job description for key requirements, skills, and keywords
2. Rewrite the CV sections to emphasize relevant experience
3. Adjust the professional summary to align with the role
4. Reorder skills to prioritize those mentioned in the JD
5. Rephrase bullet points using action verbs and quantified achievements
6. Keep all factual information (dates, companies, degrees) unchanged
7. Output in {language} language

Output format: JSON with sections (summary, experience[], skills[], education[])
```

### 10.2 Cover Letter Prompt

```
System: You are an expert cover letter writer for the Indonesian job market.
Generate a professional, personalized cover letter.

Instructions:
1. Address the hiring manager (use "Yth. HRD {company}" if no name available)
2. Opening: hook that connects candidate's passion to the company/role
3. Body: 2-3 paragraphs mapping candidate's top achievements to JD requirements
4. Closing: call to action, availability, gratitude
5. Keep it to one page (~300-400 words)
6. Tone: {formal/semi-formal}
7. Language: {id/en}
```

### 10.3 Job Classification Prompt

```
System: Classify this job posting into one or more categories from the
predefined list. Return category slugs with confidence scores.

Input: Job title + description
Output: [{"slug": "technology", "confidence": 0.95}, ...]
```

---

## 11. Notification System

### 11.1 Flow

```
Hourly cron (APScheduler)
    ↓
Run all scrapers → new jobs
    ↓
Classify jobs into categories (Kimi 2.6 batch)
    ↓
Deduplicate (fingerprint check)
    ↓
Store new jobs in DB
    ↓
For each new job:
    Find users where:
      - user subscribed to matching category
      - user location preference matches (or "Remote/Anywhere")
      - user experience level matches
      - user hasn't been notified for this job
    ↓
    Queue notification (arq)
    ↓
    Send Telegram message with job card + action buttons
    ↓
    Log in notification_log
```

### 11.2 Rate Limiting
- Max 10 notifications per user per hour (prevent spam)
- If more than 10 matches, batch into a digest message with top 10
- Users can adjust notification frequency in `/settings` (P2)

---

## 12. Document Generation Pipeline

### 12.1 CV Tailoring Flow

```
User clicks [Tailor CV] button
    ↓
Check credit balance ≥ 1
    ↓ (if insufficient → show top-up prompt)
Deduct 1 credit (atomic transaction)
    ↓
Fetch user's current CV (parsed_data) + job description
    ↓
Send to Kimi 2.6 with tailoring prompt
    ↓
Receive structured JSON response
    ↓
Generate DOCX (python-docx with professional template)
    ↓
Generate PDF (render HTML template → WeasyPrint)
    ↓
Upload files to Supabase Storage
    ↓
Send both files to user in Telegram chat
    ↓
Save to tailoring_history
```

### 12.2 CV Templates
Start with 1 clean, professional template. Add more as P2:
- **Clean Modern** (default) — single column, sans-serif, subtle color accent
- **ATS-Friendly** — minimal formatting, maximum ATS parseability
- **Two-Column** — skills sidebar + experience main area

---

## 13. Security & Privacy

| Concern | Mitigation |
|---------|-----------|
| CV data (PII) | Encrypted at rest in Supabase, access only via authenticated queries |
| Xendit webhooks | Verify callback token on every webhook |
| Telegram bot token | Stored in env vars, never in code |
| API keys | All secrets in `.env`, never committed |
| Rate limiting | Per-user throttle middleware in aiogram |
| SQL injection | SQLAlchemy parameterized queries (never raw SQL with user input) |
| File uploads | Validate file type + size (max 10MB PDF) before processing |
| Data deletion | `/delete_account` purges all user data + files from storage |

---

## 14. Deployment

### 14.1 Infrastructure

```
VPS (e.g., IDCloudHost / DigitalOcean SGP region)
├── Docker Compose
│   ├── bot         (aiogram webhook server)
│   ├── worker      (arq workers)
│   ├── scheduler   (APScheduler)
│   ├── redis       (cache + queue)
│   └── nginx       (reverse proxy + SSL)
│
└── External
    ├── Supabase     (PostgreSQL + Storage)
    ├── Moonshot API (Kimi 2.6)
    ├── Xendit       (Payments)
    └── SerpAPI      (Job search)
```

### 14.2 Estimated Monthly Costs

| Service | Cost (USD) |
|---------|-----------|
| VPS (2 vCPU, 4GB RAM) | ~$12-20 |
| Supabase (Free → Pro) | $0-25 |
| Redis (on VPS) | $0 |
| Apify (pay-per-use) | ~$10-30 |
| Kimi 2.6 API | ~$20-50 (usage-based) |
| Xendit | 0.8% per transaction |
| Domain + SSL | ~$12/year |
| **Total** | **~$80-150/month** |

---

## 15. Development Roadmap

### Phase 1 — Foundation (Weeks 1-2)
- [ ] Project setup (uv, Docker, CI)
- [ ] Database schema + Alembic migrations
- [ ] aiogram bot skeleton with router structure
- [ ] User registration + onboarding FSM
- [ ] CV upload + parsing
- [ ] Profile management commands
- [ ] i18n setup (ID/EN)

### Phase 2 — Job Engine (Weeks 3-4)
- [ ] Scraper framework (base class + first 2 sources)
- [ ] Job deduplication logic
- [ ] AI job classification (Kimi 2.6)
- [ ] Job matching engine
- [ ] Notification system
- [ ] Hourly scheduler setup
- [ ] Remaining scrapers (5 more sources)

### Phase 3 — AI & Documents (Weeks 5-6)
- [ ] Kimi 2.6 integration for CV tailoring
- [ ] CV template design (HTML/CSS + python-docx)
- [ ] DOCX generation pipeline
- [ ] PDF generation pipeline (WeasyPrint)
- [ ] Cover letter generation
- [ ] Credit deduction logic
- [ ] File delivery via Telegram

### Phase 4 — Payments (Week 7)
- [ ] Xendit invoice creation
- [ ] Payment link delivery in bot
- [ ] Webhook endpoint + verification
- [ ] Credit top-up flow
- [ ] Transaction history
- [ ] Payment receipts

### Phase 5 — Polish & Launch (Week 8)
- [ ] Rate limiting + throttle middleware
- [ ] Error handling + Sentry integration
- [ ] Admin commands
- [ ] Monitoring + logging
- [ ] Load testing
- [ ] Beta testing with 20-50 users
- [ ] Production deployment

### Phase 6 — Post-Launch (Ongoing)
- [ ] Additional CV templates
- [ ] Referral system
- [ ] Job browsing command
- [ ] Notification frequency settings
- [ ] Analytics dashboard
- [ ] Additional job sources

---

## 16. Success Metrics

| Metric | Target (Month 1) | Target (Month 3) |
|--------|------------------|------------------|
| Registered users | 500 | 2,000 |
| Onboarding completion rate | >70% | >80% |
| Credits purchased | 1,000 | 10,000 |
| CV tailoring usage | 500 | 5,000 |
| Cover letter usage | 200 | 2,000 |
| Jobs scraped/day | 200+ | 500+ |
| User retention (7-day) | >40% | >50% |
| Avg credits/paying user | 15 | 20 |
| Revenue (IDR) | 5M | 30M |

---

## 17. Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| Job boards block scrapers | High | Medium | Use Apify actors (maintained by community), provider-agnostic adapter allows quick swap to alternatives, direct scrape as fallback |
| Kimi 2.6 API downtime | Medium | Low | Queue failed requests for retry, cache recent outputs |
| Low initial adoption | Medium | Medium | Free welcome credits, referral program, target university job fairs |
| CV quality issues | High | Medium | Template testing, user feedback loop, multiple template options |
| Xendit integration delays | Low | Low | Start integration early, use sandbox for testing |
| Telegram API rate limits | Medium | Low | Queue notifications, respect per-chat limits (30 msg/sec) |
| Scaling beyond single VPS | Low | Low (initially) | Docker Compose makes migration to cloud easy if needed |

---

## Appendix A: Telegram Bot Commands

```
/start          — Register and start onboarding
/profile        — View your profile
/edit_preferences — Change job preferences
/upload_cv      — Upload a new CV
/view_cv        — View your parsed CV
/credits        — Check credit balance
/topup          — Buy credits
/transactions   — View transaction history
/browse         — Browse recent matching jobs
/language       — Switch language (ID/EN)
/help           — Show help message
/delete_account — Delete your account and data
```

## Appendix B: Environment Variables

```bash
# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_URL=

# Database (Supabase)
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_SERVICE_KEY=

# Redis
REDIS_URL=redis://localhost:6379

# AI
MOONSHOT_API_KEY=
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=kimi-2.6

# Payments
XENDIT_SECRET_KEY=
XENDIT_WEBHOOK_TOKEN=

# Scraping
APIFY_API_TOKEN=

# App
APP_ENV=production
LOG_LEVEL=INFO
SENTRY_DSN=
ADMIN_TELEGRAM_IDS=123456789,987654321
```
