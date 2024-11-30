from datetime import datetime
from typing import Any, Optional, override, Self, Sequence, Union

from nextcord import Colour
from nextcord import Interaction
from nextcord.types.embed import EmbedType

from faz.bot.app.discord.embed_factory.embed_field import EmbedField
from faz.bot.app.discord.embed_factory.pagination_embed_factory import PaginationEmbedFactory


class BaseFieldPaginationEmbedFactory(PaginationEmbedFactory[EmbedField]):
    def __init__(
        self,
        interaction: Interaction[Any],
        items: Sequence[EmbedField] | None = None,
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
            items,
            items_per_page,
            thumbnail_url=thumbnail_url,
            colour=colour,
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
        )

    def get_empty_field_embed(self, value: str, inline: bool = False) -> EmbedField:
        ret = EmbedField(value, "No data found within the selected period of time.", inline=inline)
        return ret

    @override
    def get_embed_page(self, page: int | None = None) -> Self:
        """Build specific page of the PaginationEmbed."""
        if page is None:
            page = self.current_page

        embed = self.get_base()

        fields = embed.get_items(page)
        if len(fields) == 0:
            embed.description = "```ml\nNo data found.\n```"
        else:
            for field in fields:
                embed.add_field(
                    name=field.name,
                    value=field.value,
                    inline=field.inline,
                )

        embed.finalize()
        return embed
