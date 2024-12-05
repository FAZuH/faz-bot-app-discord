from __future__ import annotations

from time import time
from typing import override, Self, TYPE_CHECKING

from nextcord import Embed
import pandas as pd

from faz.bot.app.discord.embed.builder.description_builder import DescriptionBuilder
from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder
from faz.bot.app.discord.embed.builder.guild_history_field_builder import GuildHistoryFieldBuilder
from faz.bot.app.discord.embed.director._base_field_embed_director import BaseFieldEmbedDirector

if TYPE_CHECKING:
    from datetime import datetime

    from faz.bot.database.fazwynn.model.guild_info import GuildInfo

    from faz.bot.app.discord.select.guild_history_data_options import GuildHistoryDataOption
    from faz.bot.app.discord.select.guild_history_mode_options import GuildHistoryModeOptions
    from faz.bot.app.discord.view.wynn_history.guild_history_view import GuildHistoryView


class GuildHistoryEmbedDirector(BaseFieldEmbedDirector):
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

        self._desc_builder = DescriptionBuilder([("Period", f"<t:{begin_ts}:R> to <t:{end_ts}:R>")])
        self._embed_builder = EmbedBuilder(
            view.interaction, Embed(title=f"Guild History ({guild.name})")
        )
        self.field_builder = GuildHistoryFieldBuilder()

        self._db = view.bot.app.create_fazwynn_db()

        super().__init__(self._embed_builder, items_per_page=5)

    @override
    async def setup(self) -> None:
        start = time()
        await self._fetch_data()
        self._add_query_duration_footer(time() - start)
        self.field_builder.set_data(self._player_df, self._guild_df)

    def set_options(self, data: GuildHistoryDataOption, mode: GuildHistoryModeOptions) -> Self:
        fields = self.field_builder.set_data_option(data).set_mode_option(mode).build()
        self.set_items(fields)

        description = (
            self._desc_builder.reset()
            .add_line("Data", data.value)
            .add_line("Mode", mode.value)
            .build()
        )
        embed = self._embed_builder.reset().set_description(description).get_embed()
        self.embed_builder.set_builder_initial_embed(embed)

        return self

    async def _fetch_data(self) -> None:
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
