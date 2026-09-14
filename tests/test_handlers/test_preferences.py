from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import pytest

from jobly.bot.handlers.preferences import (
    EditPrefState,
    cmd_edit_preferences,
    on_edit_arrangements,
    on_edit_categories,
    on_edit_loc_done,
    on_edit_locations,
    on_edit_phone,
    on_edit_phone_skip,
    on_edit_phone_submit,
)
from jobly.models.user import User
from tests.factories import MemoryFSMContext, make_callback, make_message


@pytest.mark.asyncio
async def test_cmd_edit_preferences_shows_phone_option(mock_user):
    state = MemoryFSMContext()
    msg = make_message(user_id=mock_user.telegram_id)

    await cmd_edit_preferences(msg, state, mock_user, "en")

    assert await state.get_state() == EditPrefState.choosing.state
    msg.answer.assert_called_once()
    keyboard = msg.answer.call_args.kwargs["reply_markup"]
    texts = [button.text for row in keyboard.inline_keyboard for button in row]
    assert "📱 Phone Number" in texts


@pytest.mark.asyncio
async def test_on_edit_phone_enters_phone_state():
    state = MemoryFSMContext()
    cb = make_callback(data="edit_phone")

    await on_edit_phone(cb, state, "en")

    assert await state.get_state() == EditPrefState.phone.state
    cb.message.edit_text.assert_called_once()
    assert "new phone number" in cb.message.edit_text.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_on_edit_phone_submit_updates_phone(mock_session, mock_user):
    state = MemoryFSMContext()
    await state.set_state(EditPrefState.phone)
    msg = make_message(text="08123456789", user_id=mock_user.telegram_id)

    await on_edit_phone_submit(msg, state, mock_session, mock_user, "en")

    assert mock_user.phone == "08123456789"
    mock_session.flush.assert_awaited_once()
    assert await state.get_state() == EditPrefState.choosing.state
    assert msg.answer.await_count == 2
    assert "phone number updated" in msg.answer.await_args_list[0].args[0].lower()


@pytest.mark.asyncio
async def test_on_edit_phone_skip_clears_phone(mock_session, mock_user):
    mock_user.phone = "08123456789"
    state = MemoryFSMContext()
    await state.set_state(EditPrefState.phone)
    msg = make_message(text="/skip", user_id=mock_user.telegram_id)

    await on_edit_phone_skip(msg, state, mock_session, mock_user, "en")

    assert mock_user.phone is None
    mock_session.flush.assert_awaited_once()
    assert await state.get_state() == EditPrefState.choosing.state
    assert msg.answer.await_count == 2
    assert "phone number removed" in msg.answer.await_args_list[0].args[0].lower()


def _result_with_scalars(items):
    scalars = Mock()
    scalars.all.return_value = items
    result = Mock()
    result.scalars.return_value = scalars
    return result


@pytest.mark.asyncio
async def test_on_edit_categories_preloads_existing_categories(mock_session):
    state = MemoryFSMContext()
    cb = make_callback(data="edit_cat")
    db_user = cast(User, SimpleNamespace(id=123))

    mock_session.execute.side_effect = [
        _result_with_scalars([SimpleNamespace(category_id=1)]),
        _result_with_scalars([SimpleNamespace(id=1, slug="data_science_ai")]),
    ]

    await on_edit_categories(cb, state, mock_session, db_user, "en")

    assert await state.get_state() == EditPrefState.categories.state
    data = await state.get_data()
    assert data["selected_categories"] == {1}
    reply_markup = cb.message.edit_text.call_args.kwargs["reply_markup"]
    assert any(button.text.startswith("✅ ") for row in reply_markup.inline_keyboard for button in row)


@pytest.mark.asyncio
async def test_on_edit_locations_preloads_existing_locations(mock_session):
    state = MemoryFSMContext()
    cb = make_callback(data="edit_loc")
    db_user = cast(User, SimpleNamespace(id=123))

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
async def test_on_edit_arrangements_preloads_existing_arrangements(mock_session):
    state = MemoryFSMContext()
    cb = make_callback(data="edit_arr")
    db_user = cast(User, SimpleNamespace(id=123))

    mock_session.execute.side_effect = [
        _result_with_scalars([SimpleNamespace(arrangement_id=3)]),
        _result_with_scalars([SimpleNamespace(id=3, name="hybrid")]),
    ]

    await on_edit_arrangements(cb, state, mock_session, db_user, "en")

    assert await state.get_state() == EditPrefState.arrangements.state
    data = await state.get_data()
    assert data["selected_arrangements"] == {"hybrid"}
    reply_markup = cb.message.edit_text.call_args.kwargs["reply_markup"]
    assert any(button.text.startswith("✅ ") for row in reply_markup.inline_keyboard for button in row)


@pytest.mark.asyncio
async def test_on_edit_loc_done_preserves_existing_and_new_locations(mock_session):
    state = MemoryFSMContext()
    await state.set_state(EditPrefState.locations)
    await state.set_data({"selected_locations": {2, 3}})
    cb = make_callback(data="loc_done")
    db_user = cast(User, SimpleNamespace(id=123))

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
