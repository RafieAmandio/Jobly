from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from jobly.services.job_matcher import find_matching_users


def _result_with_scalars(items):
    scalars = Mock()
    scalars.all.return_value = items
    result = Mock()
    result.scalars.return_value = scalars
    return result


@pytest.mark.asyncio
async def test_find_matching_users_falls_back_to_job_category_rows_when_relationship_empty(
    mock_session,
):
    job_id = uuid4()
    user_id = uuid4()
    job = SimpleNamespace(id=job_id, categories=[])
    user = SimpleNamespace(id=user_id, is_active=True, onboarding_completed=True)

    mock_session.execute.side_effect = [
        _result_with_scalars([7]),
        _result_with_scalars([user_id]),
        _result_with_scalars([]),
        _result_with_scalars([user]),
    ]

    users = await find_matching_users(mock_session, job)

    assert users == [user]
