from datetime import datetime
from datetime import timedelta
import unittest
from unittest.mock import AsyncMock
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from faz.bot.app.discord.bot._utils import Utils
from faz.bot.app.discord.bot.errors import InvalidArgumentException
from faz.bot.app.discord.bot.errors import ParseException
from faz.bot.app.discord.cog.wynn_history_cog import WynnHistoryCog


class TestWynnHistoryCog(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.intr = MagicMock()
        self.intr.response.defer = AsyncMock()
        self.intr.created_at = datetime.now()
        self.bot = MagicMock()
        self.utils = create_autospec(Utils, spec_set=True)
        self.bot.utils = self.utils
        self.wynn_history = WynnHistoryCog(self.bot)

    @patch(
        "faz.bot.app.discord.cog.wynn_history_cog.PlayerActivityView",
        autospec=True,
    )
    async def test_activity_command(self, mock_invoke: MagicMock) -> None:
        mock_player = MagicMock()
        self.utils.must_get_wynn_player = AsyncMock(return_value=mock_player)

        await self.wynn_history.player_activity(self.intr, "a", "10")

        mock_invoke.return_value.run.assert_awaited_once()
        mock_invoke.assert_called_once_with(
            self.bot,
            self.intr,
            mock_player,
            self.intr.created_at - timedelta(hours=10),
            self.intr.created_at,
        )

    @patch(
        "faz.bot.app.discord.cog.wynn_history_cog.GuildActivityView",
        autospec=True,
    )
    async def test_guild_activity_command(self, mock_invoke: MagicMock) -> None:
        mock_guild = MagicMock()
        self.utils.must_get_wynn_guild = AsyncMock(return_value=mock_guild)

        await self.wynn_history.guild_activity(self.intr, "a", "10")

        mock_invoke.return_value.run.assert_awaited_once()
        mock_invoke.assert_called_once_with(
            self.bot,
            self.intr,
            mock_guild,
            self.intr.created_at - timedelta(hours=10),
            self.intr.created_at,
            False,
        )

    def test_parse_period_valid_period_dates(self):
        # Test with a valid date range
        result = self.wynn_history._parse_period(self.intr, "2024-01-01--2024-01-31")
        self.assertEqual(result[0], datetime(2024, 1, 1))
        self.assertEqual(result[1], datetime(2024, 1, 31))

    def test_parse_period_valid_period_hours(self):
        # Test with a valid period in hours
        result = self.wynn_history._parse_period(self.intr, "48")
        self.assertEqual(result[0], self.intr.created_at - timedelta(hours=48))
        self.assertEqual(result[1], self.intr.created_at)

    def test_parse_period_invalid_period_format(self):
        # Test with an invalid date format
        with self.assertRaises(ParseException):
            self.wynn_history._parse_period(self.intr, "invalid--period")

    def test_parse_period_period_exceeds_six_months(self):
        # Test with a period that exceeds 6 months
        with self.assertRaises(InvalidArgumentException):
            self.wynn_history._parse_period(self.intr, "2023-01-01--2023-12-31")

    # def test_parse_period_period_with_nonexistent_date(self):
    #     # Test with a date that does not exist
    #     with self.assertRaises(ParseFailure):
    #         WynnHistoryCog._parse_period(self.intr, "2024-13-01--2024-01-31")

    # def test_parse_period_period_in_future(self):
    #     # Test with a period in the future
    #     with self.assertRaises(BadArgument):
    #         WynnHistoryCog._parse_period(self.intr, "2024-12-01--2025-01-01")

    def test_parse_period_period_without_separator(self):
        # Test with missing separator in period string
        with self.assertRaises(ParseException):
            self.wynn_history._parse_period(self.intr, "20240101--20240201")

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()
