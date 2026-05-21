import io
from types import SimpleNamespace
from unittest.mock import AsyncMock


class MockBot:
    def __init__(self):
        self.sent_messages: list[dict] = []
        self.sent_documents: list[dict] = []
        self.id = 999999

    async def send_message(self, chat_id, text, **kwargs):
        msg = {"chat_id": chat_id, "text": text, **kwargs}
        self.sent_messages.append(msg)
        return SimpleNamespace(message_id=len(self.sent_messages))

    async def download(self, file):
        return io.BytesIO(b"mock pdf content")

    async def session_close(self):
        pass


class MemoryFSMContext:
    def __init__(self):
        self._state = None
        self._data: dict = {}

    async def set_state(self, state=None):
        self._state = state.state if state and hasattr(state, "state") else state

    async def get_state(self):
        return self._state

    async def get_data(self):
        return dict(self._data)

    async def update_data(self, **kwargs):
        self._data.update(kwargs)
        return dict(self._data)

    async def set_data(self, data: dict):
        self._data = dict(data)

    async def clear(self):
        self._state = None
        self._data = {}


def _make_from_user(user_id: int, username: str) -> SimpleNamespace:
    return SimpleNamespace(id=user_id, username=username, first_name="Test", last_name="User")


def make_message(
    text: str = "",
    user_id: int = 123456789,
    username: str = "testuser",
    chat_id: int = 123456789,
    bot: MockBot | None = None,
) -> AsyncMock:
    bot = bot or MockBot()
    msg = AsyncMock()
    msg.text = text
    msg.from_user = _make_from_user(user_id, username)
    msg.chat = SimpleNamespace(id=chat_id, type="private")
    msg.bot = bot
    msg.document = None
    return msg


def make_callback(
    data: str,
    user_id: int = 123456789,
    username: str = "testuser",
    bot: MockBot | None = None,
    message: AsyncMock | None = None,
) -> AsyncMock:
    bot = bot or MockBot()
    cb = AsyncMock()
    cb.data = data
    cb.from_user = _make_from_user(user_id, username)
    cb.message = message or make_message(bot=bot)
    return cb
