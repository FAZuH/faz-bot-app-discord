from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from nextcord import Interaction
from sortedcontainers.sortedlist import Sequence

from faz.bot.app.discord.view.wynn_history.guild_activity_view import GuildActivityView


class TestHistoryGuildActivityView(IsolatedAsyncioTestCase):
    @staticmethod
    async def _mock_awaitable_attr() -> None: ...

    @patch("faz.bot.app.discord.view.wynn_history.guild_activity_view.PaginationEmbedFactory")
    async def test_run_not_empty(self, mock_embed: MagicMock) -> None:
        # Prepare
        mock_bot = MagicMock()
        mock_interaction = create_autospec(Interaction, spec_set=True)

        mock_guild_info = MagicMock()
        mock_guild_info.members = self._get_mock_player_infos()
        mock_guild_info.name = "MockGuild"
        mock_guild_info.awaitable_attrs.members = self._mock_awaitable_attr()

        mock_repo = mock_bot.fazwynn_db.player_activity_history.get_activities_between_period = (
            AsyncMock()
        )
        mock_repo.side_effect = self._get_mock_player_activity()

        embed = mock_embed.return_value.get_base.return_value

        view = GuildActivityView(
            mock_bot,
            mock_interaction,
            mock_guild_info,
            datetime.fromtimestamp(100),
            datetime.fromtimestamp(300),
        )

        embed.get_items.return_value = view._activity_res

        # Act
        await view.run()

        # Assert
        # self.assertMultiLineEqual(
        #     embed.description,
        #     "`Guild  : `MockGuild\n"
        #     "`Period : `<t:100:R> to <t:300:R>\n"
        #     "```ml\n"
        #     "|   No | Username   | Activity   |\n"
        #     "|------|------------|------------|\n"
        #     "|    1 | e          | 3m         |\n"
        #     "|    2 | d          | 3m         |\n"
        #     "|    3 | c          | 3m         |\n"
        #     "|    4 | b          | 3m         |\n"
        #     "|    5 | a          | 3m         |\n```",
        # )
        mock_interaction.send.assert_awaited_once_with(embed=embed, view=view)

    @staticmethod
    def _get_mock_player_infos() -> Sequence[MagicMock]:
        return [MagicMock(latest_username=letter) for letter in "abcde"]

    @staticmethod
    def _get_mock_player_activity() -> Sequence[Sequence[MagicMock]]:
        ret = []
        getts = lambda x: datetime.fromtimestamp(x)
        ret.append([MagicMock(logon_datetime=getts(50), logoff_datetime=getts(350))])
        ret.append([MagicMock(logon_datetime=getts(50), logoff_datetime=getts(350))])
        ret.append([MagicMock(logon_datetime=getts(50), logoff_datetime=getts(350))])
        ret.append([MagicMock(logon_datetime=getts(50), logoff_datetime=getts(350))])
        ret.append([MagicMock(logon_datetime=getts(50), logoff_datetime=getts(350))])
        return ret
