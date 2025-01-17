from __future__ import annotations

from datetime import datetime
from typing import Any, override, TYPE_CHECKING

from nextcord import Interaction

from faz.bot.app.discord.embed.director.guild_activity_embed_director import (
    GuildActivityEmbedDirector,
)
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.guild_info import GuildInfo
    from nextcord import Interaction

    from faz.bot.app.discord.bot.bot import Bot


class GuildActivityView(BasePaginationView):
    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        guild: GuildInfo,
        period_begin: datetime,
        period_end: datetime,
        show_inactive: bool = False,
    ) -> None:
        self._bot = bot
        self._interaction = interaction
        self._guild = guild
        self._period_begin = period_begin
        self._period_end = period_end

        self._embed_director = GuildActivityEmbedDirector(
            self, guild, period_begin, period_end, show_inactive
        )
        super().__init__(bot, interaction, self._embed_director)

    @override
    async def run(self) -> None:
        await self._embed_director.setup()
        await self._initial_send_message()
