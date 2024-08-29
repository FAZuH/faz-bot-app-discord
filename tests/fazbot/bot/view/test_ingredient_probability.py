from decimal import Decimal
from typing import override
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from fazbot.bot.view.ingredient_probability_view import IngredientProbabilityView


class TestIngredientProbability(IsolatedAsyncioTestCase):

    @override
    async def asyncSetUp(self) -> None:
        self.interaction = AsyncMock()
        self.asset = MagicMock()
        with patch("fazbot.bot.bot.Bot", autospec=True) as mock_bot:
            self.mock_bot = mock_bot
        self.obj = IngredientProbabilityView(
            self.mock_bot, self.interaction, "1/1000", 500, 100
        )
        self.obj.set_assets(self.asset)

    # async def test_run(self) -> None:
    #     await self.obj.run()
    #     self.interaction.assert_called_once()

    def test_parse_base_chance(self) -> None:
        test1 = self.obj._parse_base_chance("10%")
        self.assertAlmostEqual(test1, Decimal(0.1))

        test2 = self.obj._parse_base_chance("10.5%")
        self.assertAlmostEqual(test2, Decimal("0.105"))

        test3 = self.obj._parse_base_chance("1/100")
        self.assertAlmostEqual(test3, Decimal(1) / Decimal(100))

        test4 = self.obj._parse_base_chance("1.5/100")
        self.assertAlmostEqual(test4, Decimal("0.015"))

        test5 = self.obj._parse_base_chance("1/100.5")
        self.assertAlmostEqual(test5, Decimal(1) / Decimal("100.5"))

        test6 = self.obj._parse_base_chance("0.1")
        self.assertAlmostEqual(test6, Decimal("0.1"))

    def tearDown(self) -> None:
        pass