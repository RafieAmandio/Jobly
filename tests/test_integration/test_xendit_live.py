import uuid

import httpx
import pytest

from jobly.config import settings


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_xendit_sandbox_invoice():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.xendit.co/v2/invoices",
            auth=(settings.xendit.secret_key, ""),
            json={
                "external_id": f"test-{uuid.uuid4().hex[:8]}",
                "amount": 25_000,
                "currency": "IDR",
                "description": "Test invoice — Jobly E2E",
            },
        )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "invoice_url" in data
    assert data["invoice_url"].startswith("https://")
    assert data["amount"] == 25_000
