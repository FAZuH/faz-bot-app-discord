from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Self, Sequence, TYPE_CHECKING

from faz.bot.app.discord.embed.director._base_embed_director import BaseEmbedDirector
from faz.bot.app.discord.embed.embed_field import EmbedField

if TYPE_CHECKING:
    from nextcord import Embed

    from faz.bot.app.discord.embed.builder.embed_builder import EmbedBuilder


class BasePaginationEmbedDirector[T](BaseEmbedDirector, ABC):
    """Abstract base class that provides functionality for paginating items in an embed.

    Attributes:
        _items (Sequence[T]): The sequence of items to paginate.
        _items_per_page (int): The number of items to display per page.
        _current_page (int): The current page number.
    """

    def __init__(
        self,
        embed_builder: EmbedBuilder,
        *,
        items: Sequence[T] | None = None,
        items_per_page: int = 20,
    ) -> None:
        super().__init__(embed_builder)
        items = items or []
        self._items = items
        self._items_per_page = items_per_page
        self._current_page = 1

    @abstractmethod
    def _process_page_items(self, items: Sequence[T]) -> None:
        """Abstract method to process and add items to the embed builder.

        This method is responsible for transforming the given sequence of items into the embed
        content through the embed builder. Subclasses must implement this method to define how
        specific types of items are rendered in the embed.

        Args:
            items (Sequence[T]): A sequence of items for the current page to be processed.

        Raises:
            NotImplementedError: If not implemented by a subclass.

        Note:
            This method is typically called internally by `construct_page` method
            to populate the embed with the items for the current page.
        """
        ...

    def construct_page(self, page: int) -> Embed:
        """Construct an embed page.

        Args:
            page (int): Page of the embed to construct.

        Returns:
            Embed: Constructed embed.
        """
        self.embed_builder.reset()
        items = self.set_page(page).get_items()
        if len(items) == 0:
            self._add_empty_field("")
        else:
            self._process_page_items(items)
            if self.page_count > 1:
                self._add_page_field()
        embed = self.embed_builder.build()
        return embed

    def set_items(self, items: Sequence[T]) -> Self:
        """Set pagination items for the builder."""
        self._items = items
        return self

    def set_page(self, page: int) -> Self:
        """Set the current page for the builder.

        Args:
            page (int): Page number to set.

        Raises:
            ValueError: If the page number is invalid.

        Returns:
            Self: Returns self for method chaining.
        """
        if not self._check_page(page):
            raise ValueError(f"Invalid page number: {page}")
        self._current_page = page
        return self

    def get_items(self, page: int | None = None) -> Sequence[T]:
        """Retrieve a sequence of items for the specified page.

        Args:
            page (int | None): The page number to retrieve items from. If None, the current page is used.

        Returns:
            Sequence[T]: A sequence of items for the specified page.

        Raises:
            ValueError: If the specified page number is invalid.
        """
        page = page or self._current_page
        if not self._check_page(page):
            raise ValueError(f"Invalid page number: {page}")
        l_idx = self.items_per_page * (page - 1)
        r_idx = self.items_per_page * page
        return self.items[l_idx:r_idx]

    def _add_empty_field(self, name: str, inline: bool = False) -> Self:
        field = EmbedField(name=name, value="```No data found.\n```", inline=inline)
        self.embed_builder.add_field(field)
        return self

    def _add_page_field(self) -> Self:
        field = EmbedField("Page", f"({self._current_page} / {self.page_count})", False)
        self.embed_builder.add_field(field)
        return self

    def _add_query_duration_footer(self, duration: float) -> Self:
        embed = self._embed_builder.set_footer(f"Query took {duration:.2f}s").get_embed()
        self._embed_builder.set_builder_initial_embed(embed)
        return self

    def _check_page(self, page: int) -> bool:
        """Check if the page number is valid.

        Args:
            page (int): Page number to check.

        Returns:
            bool: True if the page number is valid. False otherwise.
        """
        return 1 <= page <= self.page_count

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def items(self) -> Sequence[T]:
        return self._items

    @property
    def items_per_page(self) -> int:
        return self._items_per_page

    @property
    def page_count(self) -> int:
        return max(1, -(-len(self._items) // self._items_per_page))
