from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import override, Self, TYPE_CHECKING
from uuid import UUID

from nextcord import Colour
import pandas as pd

from faz.bot.app.discord.embed_factory.wynn_history._base_wynn_history_embed_factory import (
    BaseWynnHistoryEmbedFactory,
)
from faz.bot.app.discord.parser.member_history_field_parser import MemberHistoryFieldParser

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.player_info import PlayerInfo

    from faz.bot.app.discord.select.member_history_data_option import MemberHistoryDataOption
    from faz.bot.app.discord.select.member_history_mode_option import MemberHistoryModeOption
    from faz.bot.app.discord.view.wynn_history.member_history_view import MemberHistoryView


class MemberHistoryEmbedFactory(BaseWynnHistoryEmbedFactory):
    def __init__(
        self,
        view: MemberHistoryView,
        player: PlayerInfo,
        period_begin: datetime,
        period_end: datetime,
    ) -> None:
        self._period_begin = period_begin
        self._period_end = period_end
        self._player = player

        begin_ts = int(period_begin.timestamp())
        end_ts = int(period_end.timestamp())
        title = f"Member History ({player.latest_username})"
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
        await self._player.awaitable_attrs.characters
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._fetch_data())
            tg.create_task(self._setup_parser())

    @override
    async def setup_fields(
        self,
        data: MemberHistoryDataOption,
        mode: MemberHistoryModeOption,
    ) -> None:
        # Prepare
        fields = MemberHistoryFieldParser(
            data, mode, self._char_df, self._member_df, self._character_labels
        ).get_fields()
        self.items = fields or [self.get_empty_field_embed(mode.value)]

    @override
    def get_embed_page(self, page: int | None = None) -> Self:
        embed = super().get_embed_page(page)
        return embed

    async def _fetch_data(self) -> None:
        self._char_df = pd.DataFrame()

        for ch in self._player.characters:
            df_char_ = self._db.character_history.select_between_period_as_dataframe(
                ch.character_uuid, self._period_begin, self._period_end
            )
            if df_char_.empty:
                continue
            self._char_df = pd.concat([self._char_df, df_char_])

        self._member_df = self._db.guild_member_history.select_between_period_as_dataframe(
            self._player.uuid, self._period_begin, self._period_end
        )

    async def _setup_parser(self) -> None:
        ch_counter = defaultdict(int)
        self._character_labels = {}
        for ch in self._player.characters:
            ch_hists = await self._db.character_history.select_between_period(
                ch.character_uuid, self._period_begin, self._period_end
            )
            if len(ch_hists) == 0:
                continue

            ch_counter[ch.type] += 1

            latest_ch_hist = max(ch_hists, key=lambda x: x.datetime)
            total_level = latest_ch_hist.get_total_level()

            label = f"{ch.type}{ch_counter[ch.type]} (Lv. {total_level})"
            uuid = str(UUID(bytes=ch.character_uuid))

            self._character_labels[uuid] = label
