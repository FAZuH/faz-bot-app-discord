from __future__ import annotations

from typing import Any, Literal, override, TYPE_CHECKING

from faz.bot.app.discord.embed.director.worldlist_embed_director import WorldlistEmbedDirector
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView

if TYPE_CHECKING:
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

        self._embed_director = WorldlistEmbedDirector(self, self._sort_by)

    @override
    async def run(self):
        await self._embed_director.setup()
        await self._initial_send(self._embed_director.construct())

    @property
    @override
    def embed_director(self) -> WorldlistEmbedDirector:
        return self._embed_director
