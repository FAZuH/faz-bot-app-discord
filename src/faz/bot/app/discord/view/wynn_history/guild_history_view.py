from __future__ import annotations

from datetime import datetime
from typing import Any, override, TYPE_CHECKING

from faz.bot.app.discord.embed_factory.wynn_history.guild_history_embed_factory import (
    GuildHistoryEmbedFactory,
)
from faz.bot.app.discord.select.guild_history_data_options import GuildHistoryDataOption
from faz.bot.app.discord.select.guild_history_data_select import GuildHistoryDataSelect
from faz.bot.app.discord.select.guild_history_mode_options import GuildHistoryModeOptions
from faz.bot.app.discord.select.guild_history_mode_select import GuildHistoryModeSelect
from faz.bot.app.discord.view._base_pagination_view import BasePaginationView

if TYPE_CHECKING:
    from faz.bot.database.fazwynn.model.guild_info import GuildInfo
    from nextcord import Interaction

    from faz.bot.app.discord.bot.bot import Bot


class GuildHistoryView(BasePaginationView):
    """View for history guild_history command.

    ## Data

    - Member list
    - Guild level
    - Territories (Future)

    ## Command parameters

    - guild: str
    - period: str

    ## Further options

    - Mode (StringSelect)
        - Overall: Earliest vs latest
        - Historical: Show stat for each data point

    - Data (StringSelect) (For Historical mode)
        - Member list
        - Guild level
        - Territories (Future)
    """

    def __init__(
        self,
        bot: Bot,
        interaction: Interaction[Any],
        guild: GuildInfo,
        period_begin: datetime,
        period_end: datetime,
    ) -> None:
        super().__init__(bot, interaction)
        self._guild = guild
        self._period_begin = period_begin
        self._period_end = period_end

        self._embed = GuildHistoryEmbedFactory(
            self,
            self._guild,
            self._period_begin,
            self._period_end,
        )

        self._options: str | None = None
        self._selected_mode: GuildHistoryModeOptions = GuildHistoryModeOptions.OVERALL
        self._selected_data: GuildHistoryDataOption = GuildHistoryDataOption.MEMBER_LIST

        self._mode_select = GuildHistoryModeSelect(self._mode_select_callback)
        self._data_select = GuildHistoryDataSelect(self._data_select_callback)

    @override
    async def run(self) -> None:
        """Initial method to setup and run the view."""
        self.add_item(self._mode_select)

        await self.embed.setup()
        embed = await self._get_embed_page()
        await self._interaction.send(embed=embed, view=self)

    async def _mode_select_callback(self, interaction: Interaction) -> None:
        """Callback for mode selection."""
        # Length of values is always 1
        self._selected_mode = self._mode_select.get_selected_option()
        if self._selected_mode == GuildHistoryModeOptions.OVERALL:
            self.remove_item(self._data_select)
        elif self._data_select not in self.children:
            self.add_item(self._data_select)
        embed = await self._get_embed_page()
        await interaction.edit(embed=embed, view=self)

    async def _data_select_callback(self, interaction: Interaction) -> None:
        """Callback for data selection."""
        # Length of values is always 1
        self._selected_data = self._data_select.get_selected_option()
        embed = await self._get_embed_page()
        await interaction.edit(embed=embed, view=self)

    async def _get_embed_page(self) -> GuildHistoryEmbedFactory:
        await self.embed.setup_fields(self._selected_data, self._selected_mode)
        embed = self.embed.get_embed_page()
        return embed

    @property
    @override
    def embed(self) -> GuildHistoryEmbedFactory:
        """The embed property."""
        return self._embed
