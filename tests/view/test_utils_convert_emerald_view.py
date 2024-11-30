from unittest import IsolatedAsyncioTestCase
from unittest.mock import call
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from nextcord import Interaction

from faz.bot.app.discord.view.wynn_utils.convert_emerald_view import ConvertEmeraldView


class TestUtilsConvertEmeraldView(IsolatedAsyncioTestCase):
    @patch("faz.bot.app.discord.view.wynn_utils.convert_emerald_view.CustomEmbedFactory")
    async def test_run(self, mock_embed: MagicMock) -> None:
        # Prepare
        embed_ins = mock_embed.return_value.get_base.return_value
        mock_bot = MagicMock()
        mock_interaction = create_autospec(Interaction, spec_set=True)
        view = ConvertEmeraldView(
            mock_bot,
            mock_interaction,
            "100le",
        )
        # Act
        await view.run()
        # Assert
        mock_embed.assert_called_once_with(
            mock_interaction,
            title="Emerald Convertor",
            color=8894804,
            thumbnail_url="https://static.wikia.nocookie.net/wynncraft_gamepedia_en/images/8/8c/Experience_bottle.png/revision/latest?cb=20190118234414",
        )
        self.assertEqual(
            embed_ins.description,
            "Converted: **1stx 36le 0eb 0e**\nEmeralds Total: **409600e**",
        )
        embed_ins.add_field.assert_has_calls(
            [
                call(name="TM Set Price", value="390094", inline=True),
                call(name="Silverbull Set Price", value="397668", inline=True),
            ],
        )
        embed_ins.finalize.assert_called_once()
        mock_interaction.send.assert_awaited_once_with(embed=embed_ins)
