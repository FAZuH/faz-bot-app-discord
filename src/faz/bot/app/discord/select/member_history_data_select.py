from typing import Any, Callable, override

from faz.bot.app.discord.select.custom_string_select import CustomStringSelect
from faz.bot.app.discord.select.member_history_data_option import MemberHistoryDataOption


class MemberHistoryDataSelect(CustomStringSelect[MemberHistoryDataOption]):
    def __init__(self, callback: Callable[..., Any]) -> None:
        super().__init__(placeholder="Select data")
        self.callback = callback

    @property
    @override
    def option_enum(self) -> type[MemberHistoryDataOption]:
        return MemberHistoryDataOption