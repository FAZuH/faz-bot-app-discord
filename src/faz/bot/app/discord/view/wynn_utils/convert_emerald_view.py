from __future__ import annotations

from typing import Any, override, TYPE_CHECKING

from faz.bot.wynn.util.emerald_util import EmeraldUtil
from faz.bot.wynn.util.emeralds import Emeralds
from nextcord import Embed
from nextcord import Interaction

from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder
from faz.bot.app.discord.embed.embed_field import EmbedField
from faz.bot.app.discord.view._base_view import BaseView

if TYPE_CHECKING:
    from faz.bot.app.discord.bot.bot import Bot


class ConvertEmeraldView(BaseView):
    _THUMBNAIL_URL = "https://static.wikia.nocookie.net/wynncraft_gamepedia_en/images/8/8c/Experience_bottle.png/revision/latest?cb=20190118234414"

    def __init__(self, bot: Bot, interaction: Interaction[Any], emerald_string: str) -> None:
        super().__init__(bot, interaction)
        self._emerald_string = emerald_string
        self._emeralds = Emeralds.from_string(emerald_string)
        self._emeralds.simplify()

    @override
    async def run(self) -> None:
        embed = self._get_embed()
        await self._interaction.send(embed=embed, view=self)

    def _get_embed(self) -> Embed:
        set_price_tm, set_price_silverbull = EmeraldUtil.get_set_price(self._emeralds)
        embed = (
            EmbedBuilder(self.interaction)
            .set_title("Emerald Convertor")
            .set_colour(8894804)
            .set_thumbnail(self._THUMBNAIL_URL)
            .set_description(
                f"Converted: **{self._emeralds}**\n" f"Emeralds Total: **{self._emeralds.total}e**"
            )
            .add_field(name="TM Set Price", value=f"{set_price_tm.emeralds}", inline=True)
            .add_field(
                name="Silverbull Set Price",
                value=f"{set_price_silverbull.emeralds}",
                inline=True,
            )
            .build()
        )
        return embed
