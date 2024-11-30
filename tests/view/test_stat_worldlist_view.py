from collections.abc import Sequence
from datetime import datetime
from datetime import timezone
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from nextcord import Interaction

from faz.bot.app.discord.view.wynn_stat.worldlist_view import WorldlistView


class TestStatWorldlistView(IsolatedAsyncioTestCase):
    @patch("faz.bot.app.discord.view.wynn_stat.worldlist_view.PaginationEmbedFactory")
    async def test_run(self, mock_embed: MagicMock) -> None:
        # Prepare
        mock_bot = MagicMock()
        mock_interaction = create_autospec(Interaction, spec_set=True)
        mock_interaction.created_at = datetime.fromtimestamp(600).replace(tzinfo=timezone.utc)
        mock_bot.fazwynn_db.worlds.get_worlds = AsyncMock(return_value=self._get_mock_worlds())
        view = WorldlistView(mock_bot, mock_interaction, "Player Count")
        embed = MagicMock()
        embed.get_items.return_value = self._get_mock_worlds()
        mock_embed.return_value.get_base.return_value = embed
        # Act
        await view.run()
        # Assert
        self.assertMultiLineEqual(
            embed.description,
            "```ml\n"
            "|   No | World   |   Players | Uptime   |\n"
            "|------|---------|-----------|----------|\n"
            "|    1 | WC10    |        10 | 10m      |\n"
            "|    2 | WC11    |        20 | 9m       |\n"
            "|    3 | WC12    |        30 | 8m       |\n"
            "|    4 | WC13    |        40 | 7m       |\n"
            "|    5 | WC14    |        50 | 6m       |\n"
            "```",
        )
        self.assertEqual(embed.current_page, 1)
        embed.finalize.assert_called_once()
        mock_interaction.send.assert_awaited_once_with(embed=embed, view=view)

    def _get_mock_worlds(self) -> Sequence[MagicMock]:
        ret = []
        ts = lambda t: datetime.fromtimestamp(t)
        ret.append(self._create_mock_world("WC10", 10, ts(0)))
        ret.append(self._create_mock_world("WC11", 20, ts(60)))
        ret.append(self._create_mock_world("WC12", 30, ts(120)))
        ret.append(self._create_mock_world("WC13", 40, ts(180)))
        ret.append(self._create_mock_world("WC14", 50, ts(240)))
        return ret

    @staticmethod
    def _create_mock_world(name: str, player_count: int, time_created: datetime) -> MagicMock:
        mock = MagicMock()
        mock.name = name
        mock.player_count = player_count
        mock.time_created = time_created
        return mock
