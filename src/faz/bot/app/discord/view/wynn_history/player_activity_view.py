from __future__ import annotations

from datetime import datetime
from typing import Any, override, TYPE_CHECKING

from nextcord import Color
from nextcord import Embed

from faz.bot.app.discord.embed_factory.custom_embed_factory import CustomEmbedFactory
from faz.bot.app.discord.view._base_view import BaseView
from faz.bot.app.discord.view._view_utils import ViewUtils

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.player_info import PlayerInfo
    from nextcord import Interaction

    from faz.bot.app.discord.bot.bot import Bot


class PlayerActivityView(BaseView):
    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        player: PlayerInfo,
        period_begin: datetime,
        period_end: datetime,
    ) -> None:
        super().__init__(bot, interaction)
        self._player = player
        self._period_begin = period_begin
        self._period_end = period_end

        self._repo = self._bot.fazwynn_db.player_activity_history

    @override
    async def run(self) -> None:
        embed = await self._get_embed()
        await self._interaction.send(embed=embed)

    async def _get_embed(self) -> Embed:
        begin_ts = int(self._period_begin.timestamp())
        end_ts = int(self._period_end.timestamp())
        assert self._interaction.user

        embed = CustomEmbedFactory(
            self._interaction,
            title=f"Player Activity ({self._player.latest_username})",
            color=Color.teal(),
        )
        time_period = await self._repo.get_playtime_between_period(
            self._player.uuid, self._period_begin, self._period_end
        )
        embed.description = f"`Playtime : ` {ViewUtils.format_timedelta(time_period)}"
        embed.description += f"\n`Period   : ` <t:{begin_ts}:R> to <t:{end_ts}:R>"
        embed.finalize()
        return embed
