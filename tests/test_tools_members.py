"""Tests for member tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.members import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_mock_member(*, id=1, name="TestUser", display_name="TestUser", nick=None, bot=False):
    m = MagicMock()
    m.id = id
    m.name = name
    m.display_name = display_name
    m.nick = nick
    m.bot = bot
    m.joined_at = None
    m.premium_since = None
    m.timed_out_until = None
    m.pending = False
    mock_role = MagicMock()
    mock_role.id = 1
    mock_role.name = "everyone"
    m.roles = [mock_role]
    m.top_role = mock_role
    m.kick = AsyncMock()
    m.timeout = AsyncMock()
    m.edit = AsyncMock(return_value=None)
    m.add_roles = AsyncMock()
    m.remove_roles = AsyncMock()
    m.send = AsyncMock()
    return m


def _make_mock_guild(*, guild_id=100, member=None):
    guild = MagicMock()
    guild.id = guild_id
    guild.fetch_member = AsyncMock(return_value=member)
    guild.query_members = AsyncMock(return_value=[member] if member else [])
    guild.ban = AsyncMock()
    guild.unban = AsyncMock()
    guild.get_role = MagicMock(side_effect=lambda rid: MagicMock(id=rid, name=f"Role-{rid}"))
    guild.get_channel = MagicMock(return_value=MagicMock())
    return guild


class TestMemberToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "get_member",
        "list_members",
        "search_members",
        "kick_member",
        "ban_member",
        "unban_member",
        "timeout_member",
        "edit_member",
        "add_member_roles",
        "remove_member_roles",
        "send_dm",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestMemberToolSchemas:
    def test_get_member_requires_guild_and_user(self):
        schema = _get_tool_schema("get_member")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "user_id" in required

    def test_ban_member_has_delete_message_seconds(self):
        schema = _get_tool_schema("ban_member")
        props = schema.get("properties", {})
        assert "delete_message_seconds" in props

    def test_timeout_member_requires_duration(self):
        schema = _get_tool_schema("timeout_member")
        required = schema.get("required", [])
        assert "duration_seconds" in required

    def test_add_member_roles_requires_role_ids_list(self):
        schema = _get_tool_schema("add_member_roles")
        required = schema.get("required", [])
        assert "role_ids" in required
        props = schema.get("properties", {})
        assert props["role_ids"]["type"] == "array"

    def test_search_members_requires_query(self):
        schema = _get_tool_schema("search_members")
        required = schema.get("required", [])
        assert "query" in required

    def test_send_dm_requires_user_and_content(self):
        schema = _get_tool_schema("send_dm")
        required = schema.get("required", [])
        assert "user_id" in required
        assert "content" in required

    def test_edit_member_only_requires_ids(self):
        schema = _get_tool_schema("edit_member")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "user_id" in required
        assert len(required) == 2


class TestMemberToolsBehavior:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.test_mcp = FastMCP("test")
        register(self.test_mcp)
        self.tools = self.test_mcp._tool_manager._tools

    @patch("discord_mcp.tools.members.get_bot")
    async def test_get_member(self, mock_get_bot):
        mock_member = _make_mock_member(id=42, name="Alice")
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["get_member"].fn(guild_id="100", user_id="42")
        assert result["id"] == "42"
        assert result["name"] == "Alice"
        mock_guild.fetch_member.assert_awaited_once_with(42)

    @patch("discord_mcp.tools.members.get_bot")
    async def test_get_member_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="Guild 999 not found"):
            await self.tools["get_member"].fn(guild_id="999", user_id="1")

    @patch("discord_mcp.tools.members.get_bot")
    async def test_list_members(self, mock_get_bot):
        mock_member = _make_mock_member(id=1, name="Bob")
        mock_guild = _make_mock_guild(member=mock_member)

        async def mock_fetch_members(limit=100):
            for m in [mock_member]:
                yield m

        mock_guild.fetch_members = mock_fetch_members
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["list_members"].fn(guild_id="100", limit=50)
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "Bob"

    @patch("discord_mcp.tools.members.get_bot")
    async def test_search_members(self, mock_get_bot):
        mock_member = _make_mock_member(id=5, name="Charlie")
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["search_members"].fn(guild_id="100", query="Char", limit=10)
        assert len(result) == 1
        assert result[0]["name"] == "Charlie"
        mock_guild.query_members.assert_awaited_once_with(query="Char", limit=10)

    @patch("discord_mcp.tools.members.get_bot")
    async def test_kick_member(self, mock_get_bot):
        mock_member = _make_mock_member(id=7)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["kick_member"].fn(guild_id="100", user_id="7", reason="spam")
        assert "Kicked user 7" in result
        mock_member.kick.assert_awaited_once_with(reason="spam")

    @patch("discord_mcp.tools.members.get_bot")
    async def test_kick_member_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="Guild 999 not found"):
            await self.tools["kick_member"].fn(guild_id="999", user_id="1")

    @patch("discord_mcp.tools.members.get_bot")
    async def test_ban_member(self, mock_get_bot):
        mock_guild = _make_mock_guild()
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["ban_member"].fn(
            guild_id="100", user_id="9", delete_message_seconds=3600, reason="abuse"
        )
        assert "Banned user 9" in result
        mock_guild.ban.assert_awaited_once()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_unban_member(self, mock_get_bot):
        mock_guild = _make_mock_guild()
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["unban_member"].fn(
            guild_id="100", user_id="9", reason="appeal accepted"
        )
        assert "Unbanned user 9" in result
        mock_guild.unban.assert_awaited_once()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_timeout_member(self, mock_get_bot):
        mock_member = _make_mock_member(id=10)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["timeout_member"].fn(
            guild_id="100", user_id="10", duration_seconds=60, reason="chill"
        )
        assert "Timed out user 10 for 60s" in result
        mock_member.timeout.assert_awaited_once()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_timeout_member_remove(self, mock_get_bot):
        mock_member = _make_mock_member(id=10)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["timeout_member"].fn(
            guild_id="100", user_id="10", duration_seconds=0
        )
        assert "Removed timeout" in result
        mock_member.timeout.assert_awaited_once_with(None, reason=None)

    @patch("discord_mcp.tools.members.get_bot")
    async def test_edit_member(self, mock_get_bot):
        mock_member = _make_mock_member(id=11, name="Dave")
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["edit_member"].fn(
            guild_id="100", user_id="11", nickname="NewNick"
        )
        assert result["id"] == "11"
        mock_member.edit.assert_awaited_once_with(nick="NewNick")

    @patch("discord_mcp.tools.members.get_bot")
    async def test_add_member_roles(self, mock_get_bot):
        mock_member = _make_mock_member(id=12)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["add_member_roles"].fn(
            guild_id="100", user_id="12", role_ids=["3", "4"], reason="promotion"
        )
        assert "Added 2 role(s)" in result
        mock_member.add_roles.assert_awaited_once()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_add_member_roles_rejects_unknown_role(self, mock_get_bot):
        # An unresolvable role ID used to become None and be handed to
        # add_roles(); it must fail with a clear message instead.
        mock_member = _make_mock_member(id=12)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_guild.id = 100
        mock_guild.get_role = MagicMock(return_value=None)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="Role 999 not found in guild 100"):
            await self.tools["add_member_roles"].fn(guild_id="100", user_id="12", role_ids=["999"])
        mock_member.add_roles.assert_not_awaited()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_remove_member_roles_rejects_unknown_role(self, mock_get_bot):
        mock_member = _make_mock_member(id=13)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_guild.id = 100
        mock_guild.get_role = MagicMock(return_value=None)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="Role 999 not found in guild 100"):
            await self.tools["remove_member_roles"].fn(
                guild_id="100", user_id="13", role_ids=["999"]
            )
        mock_member.remove_roles.assert_not_awaited()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_remove_member_roles(self, mock_get_bot):
        mock_member = _make_mock_member(id=13)
        mock_guild = _make_mock_guild(member=mock_member)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["remove_member_roles"].fn(
            guild_id="100", user_id="13", role_ids=["5"], reason="demotion"
        )
        assert "Removed 1 role(s)" in result
        mock_member.remove_roles.assert_awaited_once()

    @patch("discord_mcp.tools.members.get_bot")
    async def test_send_dm(self, mock_get_bot):
        mock_user = MagicMock()
        mock_message = MagicMock()
        mock_message.id = 999
        mock_message.content = "hello"
        mock_message.channel.id = 888
        mock_user.send = AsyncMock(return_value=mock_message)

        mock_bot = MagicMock()
        mock_bot.get_user.return_value = mock_user
        mock_get_bot.return_value = mock_bot

        result = await self.tools["send_dm"].fn(user_id="50", content="hello")
        assert result["id"] == "999"
        assert result["content"] == "hello"
        assert result["channel_id"] == "888"
        mock_user.send.assert_awaited_once_with("hello")

    @patch("discord_mcp.tools.members.get_bot")
    async def test_send_dm_fetch_user_fallback(self, mock_get_bot):
        mock_user = MagicMock()
        mock_message = MagicMock()
        mock_message.id = 777
        mock_message.content = "hi"
        mock_message.channel.id = 666
        mock_user.send = AsyncMock(return_value=mock_message)

        mock_bot = MagicMock()
        mock_bot.get_user.return_value = None
        mock_bot.fetch_user = AsyncMock(return_value=mock_user)
        mock_get_bot.return_value = mock_bot

        result = await self.tools["send_dm"].fn(user_id="50", content="hi")
        assert result["id"] == "777"
        mock_bot.fetch_user.assert_awaited_once_with(50)
