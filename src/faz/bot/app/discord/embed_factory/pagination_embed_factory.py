from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any, Optional, override, Sequence, Union

from nextcord import Colour
from nextcord import Interaction
from nextcord.types.embed import EmbedType

from faz.bot.app.discord.embed_factory.custom_embed_factory import CustomEmbedFactory


class PaginationEmbedFactory[T](CustomEmbedFactory):
    def __init__(
        self,
        interaction: Interaction[Any],
        items: Sequence[T] | None = None,
        items_per_page: int = 20,
        *,
        thumbnail_url: Optional[str] = None,
        colour: Optional[Union[int, Colour]] = None,
        color: Optional[Union[int, Colour]] = None,
        title: Optional[Any] = None,
        type: EmbedType = "rich",
        url: Optional[Any] = None,
        description: Optional[Any] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            interaction,
            thumbnail_url=thumbnail_url,
            colour=colour,
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )

        if items is None:
            items = []
        self._items = items
        self._items_per_page = items_per_page
        self._current_page: int = 1

    def get_items(self, page: int | None = None) -> Sequence[T]:
        page = page or self._current_page
        if page < 1 or page > self.page_count:
            raise ValueError(f"Invalid page number: {page}")
        l_idx = self._items_per_page * (page - 1)
        r_idx = self._items_per_page * page
        return self._items[l_idx:r_idx]

    def add_page_field(self) -> None:
        self.add_field(
            name="Page",
            value=f"{self._current_page} / {self.page_count}",
            inline=False,
        )

    @override
    def finalize(self) -> None:
        super().finalize()
        self.add_page_field()

    @property
    def items(self) -> Sequence[T]:
        return self._items

    @items.setter
    def items(self, items: Sequence[T]) -> None:
        self._items = items

    @property
    def items_per_page(self) -> int:
        return self._items_per_page

    @property
    def page_count(self) -> int:
        return max(1, -(-len(self._items) // self._items_per_page))

    @property
    def current_page(self) -> int:
        return self._current_page

    @current_page.setter
    def current_page(self, value):
        self._current_page = value

    @abstractmethod
    def get_embed_page(self, page: int) -> PaginationEmbedFactory:
        """Abstract method to get the embed for a specific page.

        This method must be implemented in subclasses to define how the embed content
        is generated for each page.

        Args:
            page (int): The page number to generate the embed for.

        Returns:
            Embed: The generated embed for the specified page.
        """
        ...
