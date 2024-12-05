from __future__ import annotations

import asyncio
from datetime import timedelta
from time import time
from typing import Iterable, override, TYPE_CHECKING

from nextcord import Embed
from sortedcontainers import SortedList

from faz.bot.app.discord.embed.builder.description_builder import DescriptionBuilder
from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder
from faz.bot.app.discord.embed.director._base_table_embed_director import BaseTableEmbedDirector
from faz.bot.app.discord.view._view_utils import ViewUtils

if TYPE_CHECKING:
    from datetime import datetime

    from faz.bot.database.fazwynn.model.guild_info import GuildInfo
    from faz.bot.database.fazwynn.model.player_activity_history import PlayerActivityHistory

    from faz.bot.app.discord.view.wynn_history.guild_activity_view import GuildActivityView


class GuildActivityEmbedDirector(BaseTableEmbedDirector):
    def __init__(
        self,
        view: GuildActivityView,
        guild: GuildInfo,
        period_begin: datetime,
        period_end: datetime,
        show_inactive: bool,
    ) -> None:
        self._period_begin = period_begin
        self._period_end = period_end
        self._guild = guild
        self._show_inactive = show_inactive

        begin_ts = int(period_begin.timestamp())
        end_ts = int(period_end.timestamp())

        self._desc_builder = DescriptionBuilder([("Period", f"<t:{begin_ts}:R> to <t:{end_ts}:R>")])
        self._embed_builder = EmbedBuilder(
            view.interaction, Embed(title=f"Guild Member Activity ({guild.name})")
        )

        self._db = view.bot.app.create_fazwynn_db()

        super().__init__(self._embed_builder, item_header=["#", "Username", "Activity"])

    @override
    async def setup(self) -> None:
        start = time()
        await self._fetch_data()
        self._add_query_duration_footer(time() - start)
        self._parse_items()

    def _parse_items(self) -> None:
        parsed_items = [
            (n, item.username, item.playtime_string) for n, item in enumerate(self._activities, 1)
        ]
        self.set_items(parsed_items)

    async def _fetch_data(self) -> None:
        await self._guild.awaitable_attrs.members

        self._activities: Iterable[_ActivityResult] = SortedList()
        for player in self._guild.members:
            entities = await self._db.player_activity_history.get_activities_between_period(
                player.uuid, self._period_begin, self._period_end
            )
            playtime = self._get_activity_time(entities, self._period_begin, self._period_end)
            activity_result = _ActivityResult(player.latest_username, playtime)
            if not self._show_inactive and activity_result.playtime.total_seconds() < 60:
                continue
            self._activities.add(activity_result)

    @staticmethod
    def _get_activity_time(
        entities: Iterable[PlayerActivityHistory],
        period_begin: datetime,
        period_end: datetime,
    ) -> timedelta:
        res = 0
        begin_ts = period_begin.timestamp()
        end_ts = period_end.timestamp()
        for e in entities:
            on_ts = e.logon_datetime.timestamp()
            off_ts = e.logoff_datetime.timestamp()
            on = begin_ts if on_ts <= begin_ts else on_ts
            off = end_ts if off_ts >= end_ts else off_ts
            res += off - on
        ret = timedelta(seconds=res)
        return ret


class _ActivityResult:
    def __init__(self, username: str, playtime: timedelta) -> None:
        self._username = username
        self._playtime = playtime
        self._playtime_string = ViewUtils.format_timedelta(playtime)

    @property
    def username(self) -> str:
        return self._username

    @property
    def playtime(self) -> timedelta:
        return self._playtime

    @property
    def playtime_string(self) -> str:
        return self._playtime_string

    def __lt__(self, other: int) -> bool:
        if isinstance(other, _ActivityResult):
            return self.playtime < other.playtime
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _ActivityResult):
            return self.playtime == other.playtime
        return NotImplemented
