from __future__ import annotations

from typing import Any, override, TYPE_CHECKING

from nextcord import BaseApplicationCommand
from nextcord import Colour
from nextcord import Interaction

from faz.bot.app.discord.embed_factory.pagination_embed_factory import PaginationEmbedFactory
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView

if TYPE_CHECKING:
    from faz.bot.app.discord.bot.bot import Bot


class HelpView(BasePaginationView):
    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        commands: list[BaseApplicationCommand],
    ) -> None:
        super().__init__(bot, interaction)
        self._commands = commands
        self._embed = PaginationEmbedFactory(
            self._interaction,
            commands,
            5,
            title="Commands List",
            color=Colour.dark_blue(),
        )
        self._embed.get_embed_page = self._get_embed_page

    @override
    async def run(self) -> None:
        await self._interaction.send(embed=self._get_embed_page(1), view=self)

    def _get_embed_page(self, page: int) -> PaginationEmbedFactory:
        """Generates embed page for page nth-page"""
        # title=f"Commands List : Page [{page}/{self._page_count}]",
        embed = self._embed.get_base()
        embed.set_footer(text="[text] means optional. <text> means required")
        for cmd in embed.get_items(page):
            embed.add_field(
                name=f"/{cmd.qualified_name}",
                value=cmd.description or "No brief description given",
                inline=False,
            )
        embed.finalize()
        return embed

    # def _get_parameters(self, parameters: dict[str, ApplicationCommandOption]) -> str:
    #     if not parameters:
    #         # NOTE: case no params
    #         return ""
    #     msglist: list[str] = []
    #     for name, p in parameters.items():
    #         # NOTE: case param disp name, param description
    #         p_msg = f"{name}: {p.description}"
    #         # NOTE: case param isrequired
    #         p_msg = f"<{p_msg}>" if p.required else f"[{p_msg}]"
    #         msglist.append(p_msg)

    @property
    @override
    def embed(self) -> PaginationEmbedFactory:
        return self._embed
