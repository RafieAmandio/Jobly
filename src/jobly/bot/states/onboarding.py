from aiogram.fsm.state import State, StatesGroup


class OnboardingState(StatesGroup):
    language = State()
    name = State()
    email = State()
    phone = State()
    categories = State()
    experience = State()
    locations = State()
    work_arrangement = State()
    salary = State()
    cv_upload = State()
    confirm = State()
