from typing import Any, Callable, override

from nextcord import SelectOption

from faz.bot.app.discord.select.custom_string_select import CustomStringSelect
from faz.bot.app.discord.select.player_history_data_option import PlayerHistoryDataOption


class PlayerHistoryDataSelect(CustomStringSelect[PlayerHistoryDataOption]):
    def __init__(
        self,
        callback: Callable[..., Any],
    ) -> None:
        super().__init__(placeholder="Select data")
        self.callback = callback

    @override
    def _get_select_options(self) -> list[SelectOption]:
        ret = [
            SelectOption(label=option.value.value, value=option.name) for option in self.option_enum
        ]
        return ret

    @property
    @override
    def option_enum(self) -> type[PlayerHistoryDataOption]:
        return PlayerHistoryDataOption
