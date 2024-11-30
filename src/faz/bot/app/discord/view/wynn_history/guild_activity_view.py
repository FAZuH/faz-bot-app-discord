from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from typing import Any, override, Sequence, TYPE_CHECKING

from faz.bot.database.fazwynn.model.player_activity_history import PlayerActivityHistory
from nextcord import Color
from sortedcontainers import SortedList
from tabulate import tabulate

from faz.bot.app.discord.embed_factory.pagination_embed_factory import PaginationEmbedFactory
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView
from faz.bot.app.discord.view._view_utils import ViewUtils

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
        super().__init__(bot, interaction, timeout=120)
        self._guild = guild
        self._period_begin = period_begin
        self._period_end = period_end
        self._show_inactive = show_inactive

        self._activity_res: SortedList = SortedList()

        begin_ts = int(self._period_begin.timestamp())
        end_ts = int(self._period_end.timestamp())

        title = f"Guild Members Activity ({guild.name})"
        desc = f"`Guild  : `{self._guild.name}\n"
        desc += f"`Period : `<t:{begin_ts}:R> to <t:{end_ts}:R>"

        self._embed: PaginationEmbedFactory[SortedList] = PaginationEmbedFactory(
            self._interaction,
            self._activity_res,
            title=title,
            color=Color.teal(),
            description=desc,
        )
        self.embed.get_embed_page = self._get_embed_page

    @override
    async def run(self) -> None:
        await self._guild.awaitable_attrs.members
        members = self._guild.members
        repo = self._bot.fazwynn_db.player_activity_history

        for player in members:
            entities = await repo.get_activities_between_period(
                player.uuid, self._period_begin, self._period_end
            )
            playtime = self._get_activity_time(entities, self._period_begin, self._period_end)
            activity_result = self.ActivityResult(player.latest_username, playtime)
            if not self._show_inactive and activity_result.playtime.total_seconds() < 60:
                continue
            self._activity_res.add(activity_result)

        embed = self.embed.get_embed_page(1)
        await self._interaction.send(embed=embed, view=self)

    def _get_embed_page(self, page: int = 1) -> PaginationEmbedFactory:
        embed = self.embed.get_base()
        items = embed.get_items(page)

        if len(items) == 0:
            embed.description = "```ml\nNo data found.\n```"
        else:
            embed.description += (
                "\n```ml\n"
                + tabulate(
                    [
                        [n, res.username, res.playtime_string]  # type: ignore
                        for n, res in enumerate(items, 1)
                    ],
                    headers=["No", "Username", "Activity"],
                    tablefmt="github",
                )
                + "\n```"
            )

        embed.finalize()
        return embed

    @property
    @override
    def embed(self) -> PaginationEmbedFactory[SortedList]:
        return self._embed

    @staticmethod
    def _get_activity_time(
        entities: Sequence[PlayerActivityHistory],
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

    class ActivityResult:
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
            if isinstance(other, GuildActivityView.ActivityResult):
                return self.playtime < other.playtime
            return NotImplemented

        def __eq__(self, other: object) -> bool:
            if isinstance(other, GuildActivityView.ActivityResult):
                return self.playtime == other.playtime
            return NotImplemented
