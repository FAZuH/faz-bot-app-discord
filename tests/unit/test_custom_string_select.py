from __future__ import annotations

from enum import Enum
from typing import override
from unittest import TestCase
from unittest.mock import MagicMock

from faz.bot.app.discord.select.custom_string_select import CustomStringSelect


class TestCustomStringSelect(TestCase):
    @override
    def setUp(self) -> None:
        self.select = self._MockCustomStringSelect()
        return super().setUp()

    # def test_view_init(self):
    #     # Prepare
    #     view = MagicMock()
    #     # Act
    #     self._MockCustomStringSelect(view=view)
    #     # Assert
    #     view.add_item.assert_called_once()

    def test_callback_init(self):
        # Prepare
        callback = MagicMock()
        # Act
        obj = self._MockCustomStringSelect(callback)
        # Assert
        self.assertEqual(obj.callback, callback)

    def test_data_type_select_initialization(self):
        # Assert
        for option, data_option in zip(self.select.options, self._MockOptions):
            self.assertEqual(option.label, data_option.value)
            self.assertEqual(option.value, data_option.name)

    def test_data_type_select_get_selected_option_none(self):
        # Prepare
        self.select._selected_values = []
        # Act, Assert
        with self.assertRaises(ValueError):
            self.select.get_selected_option()

    def test_data_type_select_get_selected_option_valid(self):
        # Prepare
        self.select._selected_values = [self._MockOptions.OPTION1.name]
        # Act
        ret = self.select.get_selected_option()
        # Assert
        self.assertEqual(ret, self._MockOptions.OPTION1)

    def test_data_type_select_get_selected_option_invalid(self):
        # Prepare
        self.select._selected_values = ["INVALID_OPTION"]
        # Act, Assert
        with self.assertRaises(ValueError):
            self.select.get_selected_option()

    class _MockOptions(Enum):
        OPTION1 = "OPTION1"
        OPTION2 = "OPTION2"

    class _MockCustomStringSelect(CustomStringSelect[_MockOptions]):
        @property
        @override
        def option_enum(self) -> type[TestCustomStringSelect._MockOptions]:
            return TestCustomStringSelect._MockOptions
