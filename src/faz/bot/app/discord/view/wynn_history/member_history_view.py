from __future__ import annotations

from datetime import datetime
from typing import Any, override, TYPE_CHECKING

from faz.bot.app.discord.embed_factory.wynn_history.member_history_embed_factory import (
    MemberHistoryEmbedFactory,
)
from faz.bot.app.discord.select.member_history_data_option import MemberHistoryDataOption
from faz.bot.app.discord.select.member_history_data_select import MemberHistoryDataSelect
from faz.bot.app.discord.select.member_history_mode_option import MemberHistoryModeOption
from faz.bot.app.discord.select.member_history_mode_select import MemberHistoryModeSelect
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.player_info import PlayerInfo
    from nextcord import Interaction

    from faz.bot.app.discord.bot.bot import Bot


class MemberHistoryView(BasePaginationView):
    """View for member_history command.

    ## Command parameters

    - member: Optional[str]
    - period: str

    ## Further options

    - Data
        - Wars
        - XP Contribution
    - Mode
        - Overall
        - Historical
    """

    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        player: PlayerInfo,
        period_begin: datetime,
        period_end: datetime,
    ) -> None:
        super().__init__(bot, interaction)
        self._player = player
        self._period_begin = period_begin
        self._period_end = period_end

        self._embed = MemberHistoryEmbedFactory(
            self,
            self._player,
            self._period_begin,
            self._period_end,
        )

        self._options: str | None = None
        self._selected_mode: MemberHistoryModeOption = MemberHistoryModeOption.OVERALL
        self._selected_data: MemberHistoryDataOption = MemberHistoryDataOption.WARS

        self._mode_select = MemberHistoryModeSelect(self._mode_select_callback)
        self._data_select = MemberHistoryDataSelect(self._data_select_callback)

    @override
    async def run(self) -> None:
        """Initial method to setup and run the view."""
        self.add_item(self._mode_select)
        self.add_item(self._data_select)

        await self.embed.setup()
        embed = await self._get_embed_page()
        await self._interaction.send(embed=embed, view=self)

    async def _mode_select_callback(self, interaction: Interaction) -> None:
        """Callback for mode selection."""
        # Length of values is always 1
        self._selected_mode = self._mode_select.get_selected_option()
        if self._selected_mode == MemberHistoryModeOption.OVERALL:
            self.remove_item(self._mode_select)
        elif self._mode_select not in self.children:
            self.add_item(self._mode_select)
        embed = await self._get_embed_page()
        await interaction.edit(embed=embed, view=self)

    async def _data_select_callback(self, interaction: Interaction) -> None:
        """Callback for data selection."""
        # Length of values is always 1
        self._selected_data = self._data_select.get_selected_option()
        embed = await self._get_embed_page()
        await interaction.edit(embed=embed, view=self)

    async def _get_embed_page(self) -> MemberHistoryEmbedFactory:
        """Sets PaginationEmbed items with fields based on selected options."""
        await self.embed.setup_fields(self._selected_data, self._selected_mode)
        embed = self.embed.get_embed_page()
        return embed

    @property
    @override
    def embed(self) -> MemberHistoryEmbedFactory:
        """The embed property."""
        return self._embed
