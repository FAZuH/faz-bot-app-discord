from __future__ import annotations

from typing import Any, override, TYPE_CHECKING

from faz.bot.wynn.util.emerald_util import EmeraldUtil
from faz.bot.wynn.util.emeralds import Emeralds
from nextcord import Embed
from nextcord import Interaction

from faz.bot.app.discord.embed_factory.custom_embed_factory import CustomEmbedFactory
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
        self._embed = CustomEmbedFactory(
            interaction,
            title="Emerald Convertor",
            color=8894804,
            thumbnail_url=self._THUMBNAIL_URL,
        )

    @override
    async def run(self):
        embed = self._get_embed(self._emeralds)
        await self._interaction.send(embed=embed)

    def _get_embed(self, emeralds: Emeralds) -> Embed:
        set_price_tm, set_price_silverbull = EmeraldUtil.get_set_price(emeralds)
        embed = self._embed.get_base()
        embed.description = f"Converted: **{emeralds}**\n" f"Emeralds Total: **{emeralds.total}e**"
        embed.add_field(name="TM Set Price", value=f"{set_price_tm.emeralds}", inline=True)
        embed.add_field(
            name="Silverbull Set Price",
            value=f"{set_price_silverbull.emeralds}",
            inline=True,
        )
        embed.finalize()
        return embed
