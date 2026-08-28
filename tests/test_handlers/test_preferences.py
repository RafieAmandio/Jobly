import pytest

from jobly.bot.handlers.preferences import (
    EditPrefState,
    cmd_edit_preferences,
    on_edit_phone,
    on_edit_phone_skip,
    on_edit_phone_submit,
)
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
