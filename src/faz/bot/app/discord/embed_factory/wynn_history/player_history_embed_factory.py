from __future__ import annotations

from datetime import datetime
from typing import override, TYPE_CHECKING
from uuid import UUID

from faz.bot.database.fazwynn.model.player_info import PlayerInfo
from nextcord import Colour
import pandas as pd

from faz.bot.app.discord.embed_factory.wynn_history._base_wynn_history_embed_factory import (
    BaseWynnHistoryEmbedFactory,
)
from faz.bot.app.discord.parser.player_history_field_parser import PlayerHistoryFieldParser
from faz.bot.app.discord.select.player_history_data_option import PlayerHistoryDataOption

if TYPE_CHECKING:
    from faz.bot.app.discord.view.wynn_history.player_history_view import PlayerHistoryView


class PlayerHistoryEmbedFactory(BaseWynnHistoryEmbedFactory):
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

        title = f"Player History ({player.latest_username})"
        desc = f"`Period   : ` <t:{begin_ts}:R> to <t:{end_ts}:R>"

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
        await self._player.awaitable_attrs.characters
        await self._fetch_data()

    @override
    async def setup_fields(self, character_uuid: str | None, data: PlayerHistoryDataOption) -> None:
        if character_uuid is None:
            char_df = self._char_df
        else:
            char_df = self._char_df[self._char_df["character_uuid"] == UUID(character_uuid).bytes]

        fields = PlayerHistoryFieldParser(
            data, self._player_df, char_df, self._character_labels
        ).get_fields()

        self.items = fields or [self.get_empty_field_embed(data.value.value)]

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
