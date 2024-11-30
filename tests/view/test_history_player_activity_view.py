from datetime import datetime
from datetime import timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from nextcord import Color
from nextcord import Interaction

from faz.bot.app.discord.view.wynn_history.player_activity_view import PlayerActivityView


class TestHistoryPlayerActivity(IsolatedAsyncioTestCase):
    @patch("faz.bot.app.discord.view.wynn_history.player_activity_view.CustomEmbedFactory")
    async def test_run(self, mock_embed: MagicMock) -> None:
        # Prepare
        mock_bot = MagicMock()
        mock_interaction = create_autospec(Interaction, spec_set=True)
        view = PlayerActivityView(
            mock_bot,
            mock_interaction,
            MagicMock(latest_username="Foo"),
            datetime.fromtimestamp(100),
            datetime.fromtimestamp(200),
        )
        view._repo.get_playtime_between_period = AsyncMock(return_value=timedelta(minutes=61))
        embed_ins = mock_embed.return_value
        # Act
        await view.run()
        # Assert
        mock_embed.assert_called_once_with(
            mock_interaction, title="Player Activity (Foo)", color=Color.teal()
        )
        self.assertEqual(
            embed_ins.description,
            "`Playtime : ` 1h 1m\n" "`Period   : ` <t:100:R> to <t:200:R>",
        )
        embed_ins.finalize.assert_called_once()
        mock_interaction.send.assert_awaited_once_with(embed=mock_embed.return_value)
