from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jobly.services.credit import add_credit, deduct_credit


@pytest.mark.asyncio
async def test_deduct_credit_success(mock_user, mock_session):
    mock_user.credit_balance = 5
    result = await deduct_credit(mock_session, mock_user, 1, "tailor_cv", description="Test")
    assert result is True
    assert mock_user.credit_balance == 4
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_deduct_credit_insufficient(mock_user, mock_session):
    mock_user.credit_balance = 0
    result = await deduct_credit(mock_session, mock_user, 1, "tailor_cv")
    assert result is False
    assert mock_user.credit_balance == 0
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_add_credit(mock_user, mock_session):
    mock_user.credit_balance = 3
    new_balance = await add_credit(mock_session, mock_user, 5, "purchase", description="Top-up")
    assert new_balance == 8
    assert mock_user.credit_balance == 8
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_deduct_exact_balance(mock_user, mock_session):
    mock_user.credit_balance = 1
    result = await deduct_credit(mock_session, mock_user, 1, "cover_letter")
    assert result is True
    assert mock_user.credit_balance == 0
