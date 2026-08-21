from unittest.mock import AsyncMock, patch

import pytest

from jobly.services.cv_input import prepare_cv_text


@pytest.mark.asyncio
async def test_prepare_cv_text_returns_plain_text_unchanged():
    text = "Experienced Python developer with 5 years in fintech."

    result = await prepare_cv_text(text)

    assert result == text


@pytest.mark.asyncio
@patch("jobly.services.cv_input._fetch_linkedin_profile_summary", new_callable=AsyncMock)
async def test_prepare_cv_text_enriches_linkedin_url(mock_fetch):
    mock_fetch.return_value = {
        "title": "John Doe - Senior Product Manager",
        "description": "Senior Product Manager at ExampleCo. Previously at Gojek and Tokopedia.",
    }

    result = await prepare_cv_text("https://www.linkedin.com/in/johndoe")

    assert "LinkedIn profile source" in result
    assert "https://www.linkedin.com/in/johndoe" in result
    assert "John Doe - Senior Product Manager" in result
    assert "Previously at Gojek and Tokopedia" in result


@pytest.mark.asyncio
@patch("jobly.services.cv_input._fetch_linkedin_profile_summary", new_callable=AsyncMock)
async def test_prepare_cv_text_falls_back_when_linkedin_fetch_fails(mock_fetch):
    mock_fetch.return_value = None

    result = await prepare_cv_text("linkedin.com/in/johndoe")

    assert "LinkedIn profile source" in result
    assert "linkedin.com/in/johndoe" in result
