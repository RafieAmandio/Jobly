import pytest
from sqlalchemy import select

from jobly.bot.handlers.start import (
    cmd_start,
    on_arrangement_done,
    on_arrangement_select,
    on_category_done,
    on_category_select,
    on_confirm,
    on_cv_text,
    on_email,
    on_experience,
    on_language,
    on_location_done,
    on_location_select,
    on_name,
    on_phone_skip,
    on_salary,
)
from jobly.bot.states.onboarding import OnboardingState
from jobly.models.cv import CV
from jobly.models.user import User, UserCategory, UserPreference
from tests.factories import MemoryFSMContext, MockBot, make_callback, make_message


@pytest.mark.asyncio
async def test_full_onboarding_flow(seeded_session):
    bot = MockBot()
    state = MemoryFSMContext()
    user_id = 999888777

    # Step 1: /start
    msg = make_message(text="/start", user_id=user_id, bot=bot)
    await cmd_start(msg, state, seeded_session)
    assert await state.get_state() == OnboardingState.language.state

    # Step 2: select language
    cb = make_callback(data="lang:en", user_id=user_id, bot=bot)
    await on_language(cb, state)
    assert await state.get_state() == OnboardingState.name.state
    data = await state.get_data()
    assert data["language"] == "en"

    # Step 3: enter name
    msg = make_message(text="John Doe", user_id=user_id, bot=bot)
    await on_name(msg, state)
    assert await state.get_state() == OnboardingState.email.state

    # Step 4: enter email
    msg = make_message(text="john@example.com", user_id=user_id, bot=bot)
    await on_email(msg, state)
    assert await state.get_state() == OnboardingState.phone.state

    # Step 5: skip phone
    msg = make_message(text="/skip", user_id=user_id, bot=bot)
    await on_phone_skip(msg, state)
    assert await state.get_state() == OnboardingState.categories.state

    # Step 6: select a category + done
    cb = make_callback(data="cat:0", user_id=user_id, bot=bot)
    await on_category_select(cb, state)
    data = await state.get_data()
    assert 0 in data["selected_categories"]

    cb = make_callback(data="cat_done", user_id=user_id, bot=bot)
    await on_category_done(cb, state)
    assert await state.get_state() == OnboardingState.experience.state

    # Step 7: select experience
    cb = make_callback(data="exp:mid", user_id=user_id, bot=bot)
    await on_experience(cb, state)
    assert await state.get_state() == OnboardingState.locations.state

    # Step 8: select a location + done
    cb = make_callback(data="loc:0", user_id=user_id, bot=bot)
    await on_location_select(cb, state)
    cb = make_callback(data="loc_done", user_id=user_id, bot=bot)
    await on_location_done(cb, state)
    assert await state.get_state() == OnboardingState.work_arrangement.state

    # Step 9: select arrangement + done
    cb = make_callback(data="arr:hybrid", user_id=user_id, bot=bot)
    await on_arrangement_select(cb, state)
    cb = make_callback(data="arr_done", user_id=user_id, bot=bot)
    await on_arrangement_done(cb, state)
    assert await state.get_state() == OnboardingState.salary.state

    # Step 10: select salary
    cb = make_callback(data="sal:15m_25m", user_id=user_id, bot=bot)
    await on_salary(cb, state)
    assert await state.get_state() == OnboardingState.cv_upload.state

    # Step 11: enter CV text
    cv_text = "Experienced Python developer with 5 years in fintech."
    msg = make_message(text=cv_text, user_id=user_id, bot=bot)
    await on_cv_text(msg, state)
    assert await state.get_state() == OnboardingState.confirm.state

    # Step 12: confirm
    cb = make_callback(data="onboard_confirm", user_id=user_id, bot=bot)
    cb.from_user.username = "johndoe"
    await on_confirm(cb, state, seeded_session)

    assert await state.get_state() is None

    # Verify DB state
    user = (
        await seeded_session.execute(select(User).where(User.telegram_id == user_id))
    ).scalar_one()
    assert user.full_name == "John Doe"
    assert user.email == "john@example.com"
    assert user.onboarding_completed is True
    assert user.credit_balance == 3
    assert user.language == "en"

    pref = (
        await seeded_session.execute(
            select(UserPreference).where(UserPreference.user_id == user.id)
        )
    ).scalar_one()
    assert pref.experience_level == "mid"

    cats = (
        await seeded_session.execute(
            select(UserCategory).where(UserCategory.user_id == user.id)
        )
    ).scalars().all()
    assert len(cats) == 1

    cv = (
        await seeded_session.execute(select(CV).where(CV.user_id == user.id))
    ).scalar_one()
    assert cv_text in cv.raw_text


@pytest.mark.asyncio
async def test_start_already_registered(seeded_session, test_user):
    bot = MockBot()
    state = MemoryFSMContext()

    test_user.onboarding_completed = True
    await seeded_session.flush()

    msg = make_message(text="/start", user_id=test_user.telegram_id, bot=bot)
    await cmd_start(msg, state, seeded_session)

    msg.answer.assert_called_once()
    call_text = msg.answer.call_args[0][0]
    assert "already registered" in call_text.lower() or "sudah terdaftar" in call_text.lower()
