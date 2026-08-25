from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from jobly.bot.handlers.preferences import EditPrefState, on_edit_loc_done, on_edit_locations
from tests.factories import MemoryFSMContext, make_callback


def _result_with_scalars(items):
    scalars = Mock()
    scalars.all.return_value = items
    result = Mock()
    result.scalars.return_value = scalars
    return result


@pytest.mark.asyncio
async def test_on_edit_locations_preloads_existing_locations(mock_session):
    state = MemoryFSMContext()
    cb = make_callback(data="edit_loc")
    db_user = SimpleNamespace(id=123)

    mock_session.execute.side_effect = [
        _result_with_scalars([SimpleNamespace(location_id=2)]),
        _result_with_scalars([SimpleNamespace(id=2, city="Jakarta Barat")]),
    ]

    await on_edit_locations(cb, state, mock_session, db_user, "en")

    assert await state.get_state() == EditPrefState.locations.state
    data = await state.get_data()
    assert data["selected_locations"] == {2}
    reply_markup = cb.message.edit_text.call_args.kwargs["reply_markup"]
    assert any(button.text.startswith("✅ ") for row in reply_markup.inline_keyboard for button in row)


@pytest.mark.asyncio
async def test_on_edit_loc_done_preserves_existing_and_new_locations(mock_session):
    state = MemoryFSMContext()
    await state.set_state(EditPrefState.locations)
    await state.set_data({"selected_locations": {2, 3}})
    cb = make_callback(data="loc_done")
    db_user = SimpleNamespace(id=123)

    mock_session.execute.side_effect = [
        None,
        _result_with_scalars(
            [
                SimpleNamespace(id=2, city="Jakarta Barat"),
                SimpleNamespace(id=3, city="Jakarta Timur"),
            ]
        ),
    ]
    mock_session.add = Mock()

    await on_edit_loc_done(cb, state, mock_session, db_user, "en")

    assert mock_session.add.call_count == 2
    assert await state.get_state() == EditPrefState.choosing.state
