from __future__ import annotations

import traceback
from typing import Any, TYPE_CHECKING

from loguru import logger
from nextcord import Activity
from nextcord import ActivityType
from nextcord import ApplicationCheckFailure
from nextcord import Colour
from nextcord import errors
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands import BucketType
from nextcord.ext.commands import Cooldown
from nextcord.ext.commands import CooldownMapping

from faz.bot.app.discord.bot.errors import ApplicationException
from faz.bot.app.discord.embed_factory.custom_embed_factory import CustomEmbedFactory

if TYPE_CHECKING:
    from faz.bot.app.discord.bot.bot import Bot


class Events:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._cooldown = CooldownMapping(Cooldown(1, 3.0), BucketType.user)
        self._ready = False
        self.load_events()

    def load_events(self) -> None:
        """Loads events to the client."""
        self._bot.client.add_listener(self.on_ready)
        self._bot.client.add_listener(self.on_application_command_completion)
        self._bot.client.add_listener(self.on_application_command_error)
        self._bot.client.application_command_before_invoke(self.before_application_invoke)

    async def on_ready(self) -> None:
        if self._bot.client.user is not None:
            logger.success("Started Discord Client")

        await self._bot.client.change_presence(
            activity=Activity(type=ActivityType.playing, name="/help")
        )

        # on_ready can be called multiple times. don't setup cogs more than once
        if not self._ready:
            # Loads all cogs and commands to the client
            await self._bot.on_ready_setup()

    async def on_application_command_completion(self, interaction: Interaction[Any]) -> None:
        await self._log_event(interaction, self.on_application_command_completion.__name__)

    async def on_application_command_error(self, intr: Interaction[Any], error: Exception) -> None:
        await self._log_event(intr, self.on_application_command_error.__name__)
        # NOTE: Error is being wrapped by ApplicationInvokeError. Unwrap is first
        if isinstance(error, errors.ApplicationInvokeError) and isinstance(
            error.original, ApplicationException
        ):
            error = error.original
        if isinstance(error, ApplicationCheckFailure):
            await self._send_check_error(intr, error)
        elif isinstance(error, ApplicationException):
            await self._send_expected_error(intr, error)
        else:
            await self._send_unexpected_error(intr, error)

    async def before_application_invoke(self, interaction: Interaction[Any]) -> None:
        # await self.__log_event(interaction, self.before_application_invoke.__name__)
        self._ratelimit(interaction)

    def _ratelimit(self, interaction: Interaction[Any]) -> None:
        if not interaction.message:
            return

        bucket: commands.Cooldown = self._cooldown.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after, self._cooldown.type)  # type: ignore

    async def _log_event(self, intr: Interaction[Any], event: str = "") -> None:
        if not intr.application_command:
            return
        cmdname = intr.application_command.name
        author = intr.user.display_name if intr.user else None
        guildname = intr.guild.name if intr.guild else None
        channelname = (
            intr.channel.name  # type: ignore
            if intr.channel and hasattr(intr.channel, "name")
            else None
        )
        data = intr.data
        args = []
        if data and "options" in data:
            for opt in data["options"]:
                if "options" in opt:
                    # Convert to string to avoid potential formatting issues
                    args.append(str(opt["options"]))

        message_parts = [f"fired event {event}", f"name={cmdname}", f"author={author}"]
        if guildname:
            message_parts.append(f"guild={guildname}")
        if channelname:
            message_parts.append(f"channel={channelname}")

        message_parts.append(f"args={args}")
        message = ", ".join(message_parts).replace("{", "{{").replace("}", "}}")

        logger.info(message, discord=True)

    async def _send_unexpected_error(
        self, interaction: Interaction[Any], exception: Exception
    ) -> None:
        description = f"An unexpected error occurred while executing the command: \n**{exception}**"
        embed = CustomEmbedFactory(
            interaction,
            title="Unexpected Error",
            description=description,
            color=Colour.dark_red(),
        )
        embed.finalize()
        is_admin = await self._bot.checks.is_admin(interaction)
        if is_admin:
            tb = traceback.format_exception(exception)
            tb_msg = f"{'\n'.join(tb)}"[:1000]
            tb_msg = f"```{tb_msg}```"
            embed.add_field(name="Traceback", value=tb_msg, inline=False)
        await interaction.send(embed=embed)
        logger.opt(exception=exception).error(description)

    async def _send_expected_error(
        self, interaction: Interaction[Any], exception: ApplicationException
    ) -> None:
        description = f"**{exception}**"
        embed = CustomEmbedFactory(
            interaction, title="Error", description=description, color=Colour.red()
        )
        embed.finalize()
        await interaction.send(embed=embed)
        logger.opt(exception=exception).warning(description, discord=True)

        # await interaction.send(
        #     "You do not have sufficient permission to use this command.",
        #     ephemeral=True,
        # )

    async def _send_check_error(
        self, interaction: Interaction[Any], exception: ApplicationCheckFailure
    ) -> None:
        description = f"**{exception}**"
        embed = CustomEmbedFactory(
            interaction,
            title="Error",
            description=description,
            color=Colour.dark_teal(),
        )
        embed.finalize()
        await interaction.send(embed=embed)
        logger.opt(exception=exception).warning(description, discord=True)
