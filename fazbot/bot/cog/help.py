from typing import Any

import nextcord

from fazbot.bot.cog._cog_base import CogBase
from fazbot.bot.errors import ApplicationException
from fazbot.bot.view.help import InvokeHelp


class Help(CogBase):

    @nextcord.slash_command(name="help", description="Help command")
    async def _help(self, interaction: nextcord.Interaction[Any]) -> None:
        if not interaction.guild:
            raise ApplicationException(
                "You can only use this command in a guild channel."
            )

        cmds = list(interaction.guild.get_application_commands())
        await InvokeHelp(self._bot, interaction, cmds).run()
