from decimal import Decimal
from unittest import IsolatedAsyncioTestCase
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from nextcord import Interaction

from faz.bot.app.discord.view.wynn_utils.ingredient_probability_view import (
    IngredientProbabilityView,
)


class TestUtilsIngredientProbabilityView(IsolatedAsyncioTestCase):
    @patch("faz.bot.app.discord.view.wynn_utils.ingredient_probability_view.CustomEmbedFactory")
    async def test_run(self, mock_embed: MagicMock) -> None:
        mock_bot = MagicMock()
        mock_interaction = create_autospec(Interaction, spec_set=True)
        # Prepare
        view = IngredientProbabilityView(mock_bot, mock_interaction, Decimal(0.1), 500, 100)
        embed_ins = mock_embed.return_value.get_base.return_value
        # Act
        await view.run()
        # Assert
        self.assertMultiLineEqual(
            embed_ins.description,
            "` Drop Chance  :` **10.00%**\n"
            "` Loot Bonus   :` **500%**\n"
            "` Loot Quality :` **100%**\n"
            "` Loot Boost   :` **600%**",
        )
        embed_ins.add_field.assert_called_once_with(
            name="Boosted Drop Chance", value="**70.00%** OR **1 in 1.43** mobs"
        )
        mock_interaction.send.assert_awaited_once_with(embed=embed_ins)
