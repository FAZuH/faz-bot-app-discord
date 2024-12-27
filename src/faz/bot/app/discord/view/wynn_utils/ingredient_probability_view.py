from __future__ import annotations

from decimal import Decimal
from typing import Any, override, TYPE_CHECKING

from faz.bot.wynn.util.ingredient_drop_probability import IngredientDropProbability
from nextcord import Embed
from nextcord import Interaction

from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder
from faz.bot.app.discord.embed.embed_field import EmbedField
from faz.bot.app.discord.view._base_view import BaseView

if TYPE_CHECKING:
    from faz.bot.app.discord.bot.bot import Bot


class IngredientProbabilityView(BaseView):
    _THUMBNAIL_URL = "https://www.wynndata.tk/assets/images/items/v4//ingredients/heads/50d8ba53402f4cb0455067d068973b3d.png"

    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        base_chance: Decimal,
        loot_bonus: int,
        loot_quality: int,
    ) -> None:
        super().__init__(bot, interaction)
        self._base_chance = base_chance
        self._loot_bonus = loot_bonus
        self._loot_quality = loot_quality

        self._ing_util = IngredientDropProbability(
            self._base_chance, self._loot_quality, self._loot_bonus
        )
        self._embed_builder = (
            EmbedBuilder(
                self._interaction,
                # title="Ingredient Chance Calculator",
                # color=472931,
                # thumbnail_url=self._THUMBNAIL_URL,
            )
            .set_title("Ingredient Chance Calculator")
            .set_colour(472931)
            .set_thumbnail(self._THUMBNAIL_URL)
        )

    @override
    async def run(self) -> None:
        await self._interaction.send(embed=self._get_embed(self._ing_util))

    def _get_embed(self, ing_util: IngredientDropProbability) -> Embed:
        desc = (
            f"` Drop Chance  :` **{ing_util.base_probability:.2%}**\n"
            f"` Loot Bonus   :` **{ing_util.loot_bonus}%**\n"
            f"` Loot Quality :` **{ing_util.loot_quality}%**\n"
            f"` Loot Boost   :` **{ing_util.loot_boost}%**"
        )
        one_in_n = 1 / ing_util.boosted_probability
        embed = (
            self._embed_builder.add_field(
                name="Boosted Drop Chance",
                value=f"**{ing_util.boosted_probability:.2%}** OR **1 in {one_in_n:.2f}** mobs",
            )
            .set_description(desc)
            .build()
        )
        return embed
