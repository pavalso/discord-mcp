"""Tests for guild tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.guilds import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_mock_guild(
    guild_id: int = 1,
    name: str = "Test Guild",
    description: str | None = "A test guild",
    owner_id: int = 100,
    member_count: int = 42,
) -> MagicMock:
    guild = MagicMock()
    guild.id = guild_id
    guild.name = name
    guild.description = description
    guild.owner_id = owner_id
    guild.member_count = member_count
    guild.icon = None
    guild.premium_tier = 0
    guild.premium_subscription_count = 0
    guild.features = []
    guild.verification_level = MagicMock(__str__=lambda self: "none")
    guild.default_notifications = MagicMock(__str__=lambda self: "all_messages")
    guild.explicit_content_filter = MagicMock(__str__=lambda self: "disabled")
    guild.afk_timeout = 300
    guild.afk_channel = None
    guild.system_channel = None
    guild.edit = AsyncMock(return_value=None)
    guild.get_channel = MagicMock(return_value=None)
    return guild


class TestGuildToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {"list_guilds", "get_guild", "edit_guild", "leave_guild"}

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestGuildToolSchemas:
    def test_list_guilds_no_required_params(self):
        schema = _get_tool_schema("list_guilds")
        required = schema.get("required", [])
        assert required == []

    def test_get_guild_requires_guild_id(self):
        schema = _get_tool_schema("get_guild")
        assert "guild_id" in schema.get("required", [])

    def test_edit_guild_requires_guild_id_only(self):
        schema = _get_tool_schema("edit_guild")
        assert schema.get("required", []) == ["guild_id"]

    def test_edit_guild_has_all_settings(self):
        schema = _get_tool_schema("edit_guild")
        props = schema.get("properties", {})
        for field in (
            "name",
            "description",
            "verification_level",
            "default_notifications",
            "explicit_content_filter",
            "afk_channel_id",
            "afk_timeout",
            "system_channel_id",
        ):
            assert field in props, f"Missing field: {field}"


class TestGuildToolsBehavior:
    @pytest.fixture()
    def tool_mcp(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        return test_mcp

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_list_guilds(self, mock_get_bot, tool_mcp):
        guild1 = _make_mock_guild(guild_id=1, name="Guild A")
        guild2 = _make_mock_guild(guild_id=2, name="Guild B")
        bot = MagicMock()
        bot.guilds = [guild1, guild2]
        mock_get_bot.return_value = bot

        result = await tool_mcp._tool_manager._tools["list_guilds"].fn()

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "Guild A"
        assert result[1]["id"] == "2"
        assert result[1]["name"] == "Guild B"

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_list_guilds_empty(self, mock_get_bot, tool_mcp):
        bot = MagicMock()
        bot.guilds = []
        mock_get_bot.return_value = bot

        result = await tool_mcp._tool_manager._tools["list_guilds"].fn()
        assert result == []

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_get_guild(self, mock_get_bot, tool_mcp):
        guild = _make_mock_guild(guild_id=42, name="My Guild")
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        result = await tool_mcp._tool_manager._tools["get_guild"].fn(guild_id="42")

        assert result["id"] == "42"
        assert result["name"] == "My Guild"
        assert result["description"] == "A test guild"
        assert result["owner_id"] == "100"
        assert result["member_count"] == 42
        assert result["icon"] is None
        assert result["premium_tier"] == 0
        assert result["verification_level"] == "none"
        assert result["afk_timeout"] == 300
        assert result["afk_channel_id"] is None
        assert result["system_channel_id"] is None

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_get_guild_not_found(self, mock_get_bot, tool_mcp):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot

        with pytest.raises(ValueError, match="not found"):
            await tool_mcp._tool_manager._tools["get_guild"].fn(guild_id="999")

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_edit_guild_name(self, mock_get_bot, tool_mcp):
        guild = _make_mock_guild(guild_id=1, name="Old Name")
        guild.edit = AsyncMock(return_value=None)
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        result = await tool_mcp._tool_manager._tools["edit_guild"].fn(guild_id="1", name="New Name")

        guild.edit.assert_awaited_once_with(name="New Name")
        assert result["id"] == "1"

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_edit_guild_not_found(self, mock_get_bot, tool_mcp):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot

        with pytest.raises(ValueError, match="not found"):
            await tool_mcp._tool_manager._tools["edit_guild"].fn(guild_id="999")

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_edit_guild_with_reason(self, mock_get_bot, tool_mcp):
        guild = _make_mock_guild(guild_id=1)
        guild.edit = AsyncMock(return_value=None)
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        await tool_mcp._tool_manager._tools["edit_guild"].fn(
            guild_id="1", name="X", reason="testing"
        )

        guild.edit.assert_awaited_once_with(name="X", reason="testing")

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_leave_guild(self, mock_get_bot):
        mock_guild = _make_mock_guild(name="Doomed Server")
        mock_guild.leave = AsyncMock()
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["leave_guild"].fn(guild_id="1")

        assert result == "Left guild 'Doomed Server' (1)."
        mock_guild.leave.assert_awaited_once()

    @patch("discord_mcp.tools.guilds.get_bot")
    async def test_leave_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["leave_guild"].fn(guild_id="999")
