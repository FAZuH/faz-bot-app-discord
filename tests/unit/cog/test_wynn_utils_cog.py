from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock

from faz.bot.app.discord.bot.errors import InvalidArgumentException
from faz.bot.app.discord.bot.errors import ParseException
from faz.bot.app.discord.cog.wynn_utils_cog import WynnUtilsCog


class TestWynnUtilsCog(TestCase):
    def setUp(self) -> None:
        self._mock_interaction = MagicMock()
        self._mock_interaction.created_at = datetime.now()
        self._mock_bot = MagicMock()
        self._wynn_utils = WynnUtilsCog(self._mock_bot)
        self._parse_ing = self._wynn_utils._parse_ings_str
        self._parse_chance = self._wynn_utils._parse_base_chance

    def test_parse_ing_valid_two_values(self):
        result = self._wynn_utils._parse_ings_str("1,5")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].min_value, 1)
        self.assertEqual(result[0].max_value, 5)
        self.assertEqual(result[0].boost, 0)

    def test_parse_ing_valid_three_values(self):
        result = self._wynn_utils._parse_ings_str("1,5,2")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].min_value, 1)
        self.assertEqual(result[0].max_value, 5)
        self.assertEqual(result[0].boost, 2)

    def test_parse_ing_invalid_format(self):
        with self.assertRaises(InvalidArgumentException):
            self._wynn_utils._parse_ings_str("1")

    def test_parse_ing_non_integer_values(self):
        with self.assertRaises(ParseException):
            self._wynn_utils._parse_ings_str("one,5,2")

    def test_parse_ing_skip_default_value(self):
        result = self._wynn_utils._parse_ings_str("0,0,0")
        self.assertEqual(len(result), 0)

    def test_parse_ing_ingredient_field_errors(self):
        with self.assertRaises(InvalidArgumentException):
            self._wynn_utils._parse_ings_str("5,1")

    def test_parse_chance_percentage(self) -> None:
        test1 = self._parse_chance("10%")
        self.assertAlmostEqual(test1, Decimal(0.1))

    def test_parse_chance_floating_percentage(self) -> None:
        test2 = self._parse_chance("10.5%")
        self.assertAlmostEqual(test2, Decimal("0.105"))

    def test_parse_chance_fractions(self) -> None:
        test3 = self._parse_chance("1/100")
        self.assertAlmostEqual(test3, Decimal(1) / Decimal(100))

    def test_parse_chance_fraction_floating_numerator(self) -> None:
        test4 = self._parse_chance("1.5/100")
        self.assertAlmostEqual(test4, Decimal("0.015"))

    def test_parse_chance_fraction_floating_denominator(self) -> None:
        test5 = self._parse_chance("1/100.5")
        self.assertAlmostEqual(test5, Decimal(1) / Decimal("100.5"))

    def test_parse_chance_float(self) -> None:
        test6 = self._parse_chance("0.1")
        self.assertAlmostEqual(test6, Decimal("0.1"))

    def test_parse_chance_invalid_argument(self) -> None:
        with self.assertRaises(InvalidArgumentException):
            self._parse_chance("abc")
