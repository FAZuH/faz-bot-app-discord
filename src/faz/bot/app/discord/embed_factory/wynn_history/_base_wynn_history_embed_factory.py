from abc import ABC
from abc import abstractmethod

from faz.bot.app.discord.embed_factory._base_field_pagination_embed_factory import (
    BaseFieldPaginationEmbedFactory,
)


class BaseWynnHistoryEmbedFactory(BaseFieldPaginationEmbedFactory, ABC):
    @abstractmethod
    async def setup(self) -> None: ...

    @abstractmethod
    async def setup_fields(self) -> None: ...
