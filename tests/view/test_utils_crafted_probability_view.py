from decimal import Decimal
from typing import override
from unittest import IsolatedAsyncioTestCase
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from faz.bot.wynn.util.crafted_roll_probability import CraftedRollProbability
from nextcord import Interaction

from faz.bot.app.discord.view.wynn_utils.crafted_probability_view import CraftedProbabilityView


class TestUtilsCraftedProbabilityView(IsolatedAsyncioTestCase):
    @override
    async def asyncSetUp(self) -> None:
        self._mock_bot = MagicMock()
        self._mock_interaction = create_autospec(Interaction, spec_set=True)
        self._mock_button = MagicMock()
        self._mock_craftutil = self._get_mock_crafted_util()
        self._view = CraftedProbabilityView(
            self._mock_bot, self._mock_interaction, self._mock_craftutil
        )

    async def test_run(self) -> None:
        # Prepare
        mock_embed = self._view._get_craftprobs_embed = MagicMock()
        # Act
        await self._view.run()
        # Assert
        self._mock_interaction.send.assert_awaited_once_with(
            embed=mock_embed.return_value, view=self._view
        )

    @patch("faz.bot.app.discord.view.wynn_utils.crafted_probability_view.CustomEmbedFactory")
    async def test_get_base_embed(self, mock_embed: MagicMock) -> None:
        # Act
        self._view._get_base_embed()
        # Assert
        mock_embed.assert_called_once_with(
            self._mock_interaction,
            title="Crafteds Probabilites Calculator",
            color=8894804,
            thumbnail_url=self._view._THUMBNAIL_URL,
        )
        self.assertEqual(
            mock_embed.return_value.description,
            "Ingredients:\n"
            "- `[1]`: 1 to 2, 50% boost\n"
            "- `[2]`: 1 to 2, 50% boost\n"
            "- `[3]`: 1 to 2, 50% boost\n"
            "- `[4]`: 1 to 2, 50% boost",
        )

    @patch("faz.bot.app.discord.view.wynn_utils.crafted_probability_view.CustomEmbedFactory")
    async def test_get_craftprobs_embed(self, mock_embed: MagicMock) -> None:
        # Act
        self._view._get_craftprobs_embed()
        # Assert
        mock_embed.return_value.add_field.assert_called_once_with(
            name="Probabilities",
            value=(
                "Roll: **4**, Chance: **6.01%** (1 in 16.64)\n"
                "Roll: **6**, Chance: **24.50%** (1 in 4.08)\n"
                "Roll: **8**, Chance: **37.49%** (1 in 2.67)\n"
                "Roll: **10**, Chance: **25.50%** (1 in 3.92)\n"
                "Roll: **12**, Chance: **6.50%** (1 in 15.38)\n"
            ),
            inline=False,
        )

    @patch("faz.bot.app.discord.view.wynn_utils.crafted_probability_view.CustomEmbedFactory")
    async def test_get_atleast_embed(self, mock_embed: MagicMock) -> None:
        # Act
        self._view._get_atleast_embed()
        # Assert
        mock_embed.return_value.add_field.assert_called_once_with(
            name="Probabilities",
            value=(
                "Roll: **atleast 4**, Chance: **100.00%** (1 in 1.00)\n"
                "Roll: **atleast 6**, Chance: **93.99%** (1 in 1.06)\n"
                "Roll: **atleast 8**, Chance: **69.49%** (1 in 1.44)\n"
                "Roll: **atleast 10**, Chance: **32.00%** (1 in 3.12)\n"
                "Roll: **atleast 12**, Chance: **6.50%** (1 in 15.38)\n"
            ),
            inline=False,
        )

    @patch("faz.bot.app.discord.view.wynn_utils.crafted_probability_view.CustomEmbedFactory")
    async def test_get_atmost_getcraftprobs_embed(self, mock_embed: MagicMock) -> None:
        # Act
        self._view._get_atmost_embed()
        # Assert
        mock_embed.return_value.add_field.assert_called_once_with(
            name="Probabilities",
            value=(
                "Roll: **atmost 4**, Chance: **6.01%** (1 in 16.64)\n"
                "Roll: **atmost 6**, Chance: **30.51%** (1 in 3.28)\n"
                "Roll: **atmost 8**, Chance: **68.00%** (1 in 1.47)\n"
                "Roll: **atmost 10**, Chance: **93.50%** (1 in 1.07)\n"
                "Roll: **atmost 12**, Chance: **100.00%** (1 in 1.00)\n"
            ),
            inline=False,
        )

    @staticmethod
    def _get_mock_crafted_util() -> MagicMock:
        ret = create_autospec(CraftedRollProbability, spec_set=True)
        get_ingr = lambda x, y, z: MagicMock(min_value=x, max_value=y, boost=z)
        ret.ingredients = [
            get_ingr(1, 2, 50),
            get_ingr(1, 2, 50),
            get_ingr(1, 2, 50),
            get_ingr(1, 2, 50),
        ]
        ret.roll_pmfs.items.return_value = {
            4: Decimal("0.0601"),
            6: Decimal("0.2450"),
            8: Decimal("0.3749"),
            10: Decimal("0.2550"),
            12: Decimal("0.0650"),
        }.items()
        return ret
