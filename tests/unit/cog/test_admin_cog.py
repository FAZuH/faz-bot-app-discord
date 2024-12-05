from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, TYPE_CHECKING
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from faz.bot.database.fazcord.fazcord_database import FazcordDatabase
from faz.bot.database.fazwynn.fazwynn_database import FazwynnDatabase

from faz.bot.app.discord.app._properties import Properties
from faz.bot.app.discord.bot._utils import Utils
from faz.bot.app.discord.bot.bot import Bot
from faz.bot.app.discord.bot.errors import ApplicationException
from faz.bot.app.discord.cog.admin_cog import AdminCog

FazwynnDatabase  # type: ignore : Let sqlalchemy load the models

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@patch("nextcord.interactions.Interaction", autospec=True)
class TestAdminCog(IsolatedAsyncioTestCase):
    @asynccontextmanager
    async def _mock_enter_db_session(
        self,
    ) -> AsyncGenerator[tuple[FazcordDatabase, AsyncSession], None]:
        async with self.db.enter_async_session() as session:
            yield self.db, session

    async def asyncSetUp(self) -> None:
        self.mock_bot = create_autospec(Bot, spec_set=True)
        p = Properties()
        p.setup()
        self.db = FazcordDatabase(
            p.MYSQL_USER,
            p.MYSQL_PASSWORD,
            p.MYSQL_HOST,
            p.MYSQL_PORT,
            f"{p.MYSQL_FAZCORD_DATABASE}_test",
        )
        self.db.create_all()
        await self.db.whitelist_group.truncate()

        self.mock_utils = create_autospec(Utils, spec_set=True)
        self.mock_utils.must_get_user.return_value = self._get_mock_user()
        self.mock_utils.must_get_guild.return_value = self._get_mock_guild()
        self.mock_utils.must_get_channel.return_value = self._get_mock_channel()
        self.mock_bot.utils = self.mock_utils
        self.admin = AdminCog(self.mock_bot)
        self.admin._enter_botdb_session = self._mock_enter_db_session
        self.admin._respond_successful = AsyncMock()

    async def test_ban_user_not_banned(self, mock_intr: MagicMock) -> None:
        """Test if ban method successfully bans user that's not already banned."""
        await self.admin.ban(mock_intr, user_id="1")
        self.assertTrue(await self.db.whitelist_group.is_banned_user(1))

    async def test_ban_user_already_banned(self, mock_intr: MagicMock) -> None:
        """Test if ban method fails banning user that's already banned."""
        mock_intr.send = AsyncMock()
        await self.db.whitelist_group.ban_user(user_id=1)
        with self.assertRaises(ApplicationException):
            await self.admin.ban(mock_intr, user_id="1")

    async def test_unban_already_banned(self, mock_intr: MagicMock) -> None:
        """Test if unban successfully unbans a banned user."""
        await self.db.whitelist_group.ban_user(user_id=1)

        await self.admin.unban(mock_intr, user_id="1")
        self.assertFalse(await self.db.whitelist_group.is_banned_user(1))

    async def test_unban_not_banned(self, mock_intr: MagicMock) -> None:
        """Test if ban method fails banning user that's already banned."""
        mock_intr.send = AsyncMock()

        with self.assertRaises(ApplicationException):
            await self.admin.unban(mock_intr, user_id="1")

    async def test_echo(self, mock_intr: MagicMock) -> None:
        mock_intr.send = AsyncMock()
        await self.admin.echo(mock_intr, "test")
        mock_intr.send.assert_awaited_once_with("test")

    async def test_send(self, mock_intr: MagicMock) -> None:
        mock_channel = self._get_mock_channel()
        self.mock_utils.must_get_channel.return_value = mock_channel
        await self.admin.send(mock_intr, 1, "test")
        mock_channel.send.assert_awaited_once_with("test")
        mock_channel = self._get_mock_channel()
        del mock_channel.send
        self.mock_utils.must_get_channel.return_value = mock_channel
        with self.assertRaises(ApplicationException):
            await self.admin.send(mock_intr, 1, "test")

    async def test_sync_guild(self, mock_intr: MagicMock) -> None:
        mock_intr.response.defer = AsyncMock()
        self.mock_bot.client.sync_application_commands = AsyncMock()
        await self.admin.sync_guild(mock_intr, "1")
        self.mock_bot.client.sync_application_commands.assert_awaited_once_with(guild_id=1)

    async def test_sync(self, mock_intr: MagicMock) -> None:
        self.mock_bot.client.sync_all_application_commands = AsyncMock()
        mock_intr.response.defer = AsyncMock()
        await self.admin.sync(mock_intr)
        self.mock_bot.client.sync_all_application_commands.assert_awaited_once()

    async def test_shutdown(self, mock_intr: MagicMock) -> None:
        self.mock_bot.app.stop = MagicMock()
        await self.admin.shutdown(mock_intr)
        self.mock_bot.app.stop.assert_called_once()

    async def test_whisper(self, mock_intr: MagicMock) -> None:
        mock_user = self._get_mock_user()
        self.mock_utils.must_get_user.return_value = mock_user
        mock_user.send = AsyncMock()
        await self.admin.whisper(mock_intr, "1", "test")
        mock_user.send.assert_awaited_once_with("test")

    async def test_whitelist_guild_not_whitelisted(self, mock_intr: MagicMock) -> None:
        """Test if whitelist method successfully whitelists guild that's not already whitelisted."""
        await self.admin.whitelist(mock_intr, guild_id="1")
        self.assertTrue(await self.db.whitelist_group.is_whitelisted_guild(1))

    async def test_whitelist_guild_already_whitelisted(self, mock_intr: MagicMock) -> None:
        """Test if whitelist method fails whitelisting guild that's already whitelisted."""
        await self.db.whitelist_group.whitelist_guild(guild_id=1)
        with self.assertRaises(ApplicationException):
            await self.admin.whitelist(mock_intr, guild_id="1")

    async def asyncTearDown(self) -> None:
        await self.db.async_engine.dispose()
        return await super().asyncTearDown()

    @staticmethod
    def _get_mock_user() -> MagicMock:
        ret = MagicMock()
        ret.id = 1
        return ret

    @staticmethod
    def _get_mock_channel() -> MagicMock:
        ret = MagicMock()
        ret.send = AsyncMock()
        return ret

    @staticmethod
    def _get_mock_guild() -> MagicMock:
        ret = MagicMock()
        ret.id = 1
        ret.name = "test"
        return ret
