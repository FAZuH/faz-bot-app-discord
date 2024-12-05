from __future__ import annotations

from datetime import datetime
from time import time
from typing import override, Self, TYPE_CHECKING
from uuid import UUID

from faz.bot.database.fazwynn.model.player_info import PlayerInfo
from nextcord import Embed
import pandas as pd

from faz.bot.app.discord.embed.builder.description_builder import DescriptionBuilder
from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder
from faz.bot.app.discord.embed.builder.player_history_field_builder import PlayerHistoryFieldBuilder
from faz.bot.app.discord.embed.director._base_field_embed_director import BaseFieldEmbedDirector
from faz.bot.app.discord.select.player_history_data_option import PlayerHistoryDataOption

if TYPE_CHECKING:
    from faz.bot.app.discord.view.wynn_history.player_history_view import PlayerHistoryView


class PlayerHistoryEmbedDirector(BaseFieldEmbedDirector):
    def __init__(
        self,
        view: PlayerHistoryView,
        player: PlayerInfo,
        period_begin: datetime,
        period_end: datetime,
        character_labels: dict[str, str],
    ) -> None:
        self._character_labels = character_labels
        self._period_begin = period_begin
        self._period_end = period_end
        self._player = player

        begin_ts = int(period_begin.timestamp())
        end_ts = int(period_end.timestamp())
        initial_embed = Embed(title=f"Player History ({player.latest_username})")

        self._desc_builder = DescriptionBuilder([("Period", f"<t:{begin_ts}:R> to <t:{end_ts}:R>")])
        self._embed_builder = EmbedBuilder(view.interaction, initial_embed)
        self._field_builder = PlayerHistoryFieldBuilder().set_character_labels(character_labels)

        self._db = view.bot.app.create_fazwynn_db()

        super().__init__(self._embed_builder, items_per_page=5)

    @override
    async def setup(self) -> None:
        """Async initialization method. Must be run once."""
        start = time()
        await self._fetch_data()
        self._add_query_duration_footer(time() - start)
        self._field_builder.set_data(self._player_df, self._char_df)

    def set_options(self, data: PlayerHistoryDataOption, character_uuid: str | None = None) -> Self:
        if character_uuid is None:
            char_df = self._char_df
            char_label = "All characters"
        else:
            char_df: pd.DataFrame = self._char_df[  # type: ignore
                self._char_df["character_uuid"] == UUID(character_uuid).bytes
            ]
            char_label = self._character_labels[character_uuid]

        description = (
            self._desc_builder.reset()
            .add_line("Charater", char_label)
            .add_line("Data", data.value.value)
            .build()
        )
        self.embed_builder.reset().set_description(description)
        self._set_builder_initial_embed()

        fields = self._field_builder.set_data_option(data).set_character_data(char_df).build()
        self.set_items(fields)

        return self

    async def _fetch_data(self) -> None:
        await self._player.awaitable_attrs.characters

        self._char_df = pd.DataFrame()
        for ch in self._player.characters:
            df_char_ = self._db.character_history.select_between_period_as_dataframe(
                ch.character_uuid, self._period_begin, self._period_end
            )
            if df_char_.empty:
                continue
            self._char_df = pd.concat([self._char_df, df_char_])

        self._player_df = self._db.player_history.select_between_period_as_dataframe(
            self._player.uuid, self._period_begin, self._period_end
        )
