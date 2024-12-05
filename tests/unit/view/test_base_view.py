from typing import override
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from nextcord import Button

from faz.bot.app.discord.view._base_view import BaseView


class _MockView(BaseView):
    @override
    async def run(self) -> None: ...


class TestBaseView(IsolatedAsyncioTestCase):
    @override
    async def asyncSetUp(self) -> None:
        self._mock_bot = MagicMock()
        self._mock_interaction = MagicMock()
        self._view = _MockView(self._mock_bot, self._mock_interaction)

    def test_click_button(self) -> None:
        # Prepare
        mock_button = MagicMock(spec=Button, disabled=False)
        mock_button_other = [
            MagicMock(spec=Button, disabled=False),
            MagicMock(spec=Button, disabled=False),
            MagicMock(spec=Button, disabled=False),
            MagicMock(spec=Button, disabled=False),
            MagicMock(spec=Button, disabled=False),
        ]
        self._view.children = [
            mock_button,
            *mock_button_other,
            MagicMock(spec=MagicMock),
        ]
        # Act
        self._view._click_button(mock_button)
        # Assert
        self.assertTrue(mock_button.disabled)
        for button in mock_button_other:
            self.assertFalse(button.disabled)
