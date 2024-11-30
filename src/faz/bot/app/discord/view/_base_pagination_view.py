from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any, TYPE_CHECKING

from nextcord import ButtonStyle
from nextcord import Interaction
from nextcord.ui import Button
from nextcord.ui import button

from faz.bot.app.discord.view._base_view import BaseView

if TYPE_CHECKING:
    from faz.bot.app.discord.embed_factory.pagination_embed_factory import PaginationEmbedFactory


class BasePaginationView[T](BaseView, ABC):
    """Base class for pagination views in a Discord bot using Nextcord.

    This class provides a base structure for pagination views that allow users to navigate
    through multiple pages of an embed message. It includes buttons for first, previous,
    next, last, and stop controls.

    Attributes:
        _embed (PaginationEmbed): The embed object that represents the paginated content.
    """

    @button(style=ButtonStyle.blurple, emoji="⏮️")
    async def first_page_callback(self, button: Button[Any], interaction: Interaction[Any]) -> None:
        """Handles the callback for the 'First Page' button.

        This method sets the embed to the first page and updates the message.

        Args:
            button (Button[Any]): The button instance that triggered the callback.
            interaction (Interaction[Any]): The interaction object from Discord.
        """
        await interaction.response.defer()
        self.embed.current_page = 1
        embed = self.embed.get_embed_page(self.embed.current_page)
        await interaction.edit_original_message(embed=embed)

    @button(style=ButtonStyle.blurple, emoji="◀️")
    async def previous_page_callback(
        self, button: Button[Any], interaction: Interaction[Any]
    ) -> None:
        """Handles the callback for the 'Previous Page' button.

        This method navigates to the previous page of the embed. If the current page
        is the first page, it loops around to the last page.

        Args:
            button (Button[Any]): The button instance that triggered the callback.
            interaction (Interaction[Any]): The interaction object from Discord.
        """
        await interaction.response.defer()
        self.embed.current_page -= 1
        if self.embed.current_page == 0:
            self.embed.current_page = self.embed.page_count
        embed = self.embed.get_embed_page(self.embed.current_page)
        await interaction.edit_original_message(embed=embed)

    @button(style=ButtonStyle.red, emoji="⏹️")
    async def stop_callback(self, button: Button[Any], interaction: Interaction[Any]) -> None:
        """Handles the callback for the 'Stop' button.

        This method stops the pagination by calling the `on_timeout` method, which
        effectively disables the view.

        Args:
            button (Button[Any]): The button instance that triggered the callback.
            interaction (Interaction[Any]): The interaction object from Discord.
        """
        await self.on_timeout()

    @button(style=ButtonStyle.blurple, emoji="▶️")
    async def next_page_callback(self, button: Button[Any], interaction: Interaction[Any]) -> None:
        """Handles the callback for the 'Next Page' button.

        This method navigates to the next page of the embed. If the current page is
        the last page, it loops around to the first page.

        Args:
            button (Button[Any]): The button instance that triggered the callback.
            interaction (Interaction[Any]): The interaction object from Discord.
        """
        await interaction.response.defer()
        self.embed.current_page += 1
        if self.embed.current_page == (self.embed.page_count + 1):
            self.embed.current_page = 1
        embed = self.embed.get_embed_page(self.embed.current_page)
        await interaction.edit_original_message(embed=embed)

    @button(style=ButtonStyle.blurple, emoji="⏭️")
    async def last_page_callback(self, button: Button[Any], interaction: Interaction[Any]) -> None:
        """Handles the callback for the 'Last Page' button.

        This method sets the embed to the last page and updates the message.

        Args:
            button (Button[Any]): The button instance that triggered the callback.
            interaction (Interaction[Any]): The interaction object from Discord.
        """
        await interaction.response.defer()
        self.embed.current_page = self.embed.page_count
        embed = self.embed.get_embed_page(self.embed.current_page)
        await interaction.edit_original_message(embed=embed)

    @property
    @abstractmethod
    def embed(self) -> PaginationEmbedFactory[T]: ...
