from __future__ import annotations

from datetime import datetime
from typing import override, TYPE_CHECKING

from nextcord import Colour
import pandas as pd

from faz.bot.app.discord.embed_factory.wynn_history._base_wynn_history_embed_factory import (
    BaseWynnHistoryEmbedFactory,
)
from faz.bot.app.discord.parser.guild_history_field_parser import GuildHistoryFieldParser
from faz.bot.app.discord.select.guild_history_data_options import GuildHistoryDataOption

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.guild_info import GuildInfo

    from faz.bot.app.discord.select.guild_history_mode_options import GuildHistoryModeOptions
    from faz.bot.app.discord.view.wynn_history.guild_history_view import GuildHistoryView


class GuildHistoryEmbedFactory(BaseWynnHistoryEmbedFactory):
    def __init__(
        self,
        view: GuildHistoryView,
        guild: GuildInfo,
        period_begin: datetime,
        period_end: datetime,
    ) -> None:
        self._period_begin = period_begin
        self._period_end = period_end
        self._guild = guild

        begin_ts = int(period_begin.timestamp())
        end_ts = int(period_end.timestamp())

        title = f"Guild History ({guild.name})"
        desc = f"`Period : ` <t:{begin_ts}:R> to <t:{end_ts}:R>"

        super().__init__(
            view.interaction,
            items_per_page=4,
            title=title,
            description=desc,
            color=Colour.teal(),
        )

        self._db = view.bot.app.create_fazwynn_db()

    @override
    async def setup(self) -> None:
        await self._fetch_data()

    @override
    async def setup_fields(
        self, data: GuildHistoryDataOption, mode: GuildHistoryModeOptions
    ) -> None:
        fields = GuildHistoryFieldParser(mode, data, self._guild_df, self._player_df).get_fields()
        self.items = fields or [self.get_empty_field_embed(mode.value)]

    async def _fetch_data(self):
        await self._guild.awaitable_attrs.members

        self._player_df = pd.DataFrame()
        for member in self._guild.members:
            player_df_: pd.DataFrame = self._db.player_history.select_between_period_as_dataframe(
                member.uuid, self._period_begin, self._period_end
            )
            if player_df_.empty:
                continue
            self._player_df = pd.concat([self._player_df, player_df_])

        self._guild_df = self._db.guild_history.select_between_period_as_dataframe(
            self._guild.uuid, self._period_begin, self._period_end
        )
