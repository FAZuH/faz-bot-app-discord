from __future__ import annotations

from datetime import timezone
from typing import Any, Literal, override, TYPE_CHECKING

from nextcord import Color
from tabulate import tabulate

from faz.bot.app.discord.embed_factory.pagination_embed_factory import PaginationEmbedFactory
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView
from faz.bot.app.discord.view._view_utils import ViewUtils

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.worlds import Worlds
    from nextcord import Interaction

    from faz.bot.app.discord.bot.bot import Bot


class WorldlistView(BasePaginationView):
    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        sort_by: Literal["Player Count", "Time Created"],
    ) -> None:
        self._sort_by: Literal["player", "time"] = "player" if sort_by == "Player Count" else "time"
        super().__init__(bot, interaction)

        self._embed: PaginationEmbedFactory[Worlds] = PaginationEmbedFactory(
            self._interaction, title="World List", color=Color.dark_teal()
        )
        self.embed.get_embed_page = self._get_embed_page

    @override
    async def run(self):
        items = await self._bot.fazwynn_db.worlds.get_worlds(self._sort_by)
        self.embed.items = items
        await self._interaction.send(embed=self._get_embed_page(1), view=self)

    def _get_embed_page(self, page: int) -> PaginationEmbedFactory:
        embed = self._embed.get_base()
        embed.current_page = page
        worlds = embed.get_items(page)
        worldlist = [
            [
                n,
                world.name,
                world.player_count,
                ViewUtils.format_timedelta(
                    self._interaction.created_at - world.time_created.replace(tzinfo=timezone.utc)
                ),
            ]
            for n, world in enumerate(
                worlds, start=1 + embed.items_per_page * (embed.current_page - 1)
            )
        ]
        embed.description = (
            "```ml\n"
            + tabulate(
                worldlist,
                headers=["No", "World", "Players", "Uptime"],
                tablefmt="github",
            )
            + "\n```"
        )
        embed.finalize()
        return embed

    @property
    @override
    def embed(self) -> PaginationEmbedFactory:
        return self._embed
