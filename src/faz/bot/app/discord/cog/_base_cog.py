from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Iterable, TYPE_CHECKING

from loguru import logger
from nextcord import Colour
from nextcord import Interaction
from nextcord.ext import commands

from faz.bot.app.discord.embed_factory.custom_embed_factory import CustomEmbedFactory

if TYPE_CHECKING:
    from faz.bot.database.fazcord.fazcord_database import FazcordDatabase
    from faz.bot.database.fazwynn.fazwynn_database import FazwynnDatabase
    from sqlalchemy.ext.asyncio import AsyncSession

    from faz.bot.app.discord.bot.bot import Bot


class CogBase(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self._bot = bot
        self._utils = self._bot.utils

    def setup(self, whitelisted_guild_ids: Iterable[int]) -> None:
        """Adds cog to the bot."""
        self._bot.client.add_cog(self)
        self._setup(whitelisted_guild_ids)

        logger.info(
            f"Added cog {self.__class__.__qualname__} "
            f"with {len(self.application_commands)} application commands"
        )

    async def _respond_successful(self, interaction: Interaction[Any], message: str) -> None:
        embed = CustomEmbedFactory(
            interaction, title="Success", description=message, color=Colour.dark_green()
        )
        embed.finalize()
        await interaction.send(embed=embed)

    @asynccontextmanager
    async def _enter_botdb_session(
        self,
    ) -> AsyncGenerator[tuple[FazcordDatabase, AsyncSession], None]:
        db = self._bot.fazcord_db
        async with db.enter_async_session() as session:
            yield db, session

    @asynccontextmanager
    async def _enter_fazwynn_session(
        self,
    ) -> AsyncGenerator[tuple[FazwynnDatabase, AsyncSession], None]:
        db = self._bot.fazwynn_db
        async with db.enter_async_session() as session:
            yield db, session

    def _setup(self, whitelisted_guild_ids: Iterable[int]) -> None:
        """Method to run on cog setup.
        By default, this adds whitelisted_guild_ids into
        guild rollouts into all command in the cog."""
        for app_cmd in self.application_commands:
            for guild_id in whitelisted_guild_ids:
                app_cmd.add_guild_rollout(guild_id)
                # app_cmd.guild_ids.add(guild_id)
            self._bot.client.add_application_command(app_cmd, overwrite=True, use_rollout=True)
