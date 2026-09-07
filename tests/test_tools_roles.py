"""Tests for role tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.roles import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_role(
    *,
    id: int = 10,
    name: str = "Admin",
    color_value: int = 0xFF0000,
    hoist: bool = True,
    position: int = 1,
    managed: bool = False,
    mentionable: bool = True,
) -> MagicMock:
    role = MagicMock()
    role.id = id
    role.name = name
    role.color = MagicMock()
    role.color.value = color_value
    role.hoist = hoist
    role.position = position
    role.managed = managed
    role.mentionable = mentionable
    role.permissions = MagicMock()
    role.permissions.__iter__ = MagicMock(
        return_value=iter([("send_messages", True), ("manage_channels", False)])
    )
    role.edit = AsyncMock(return_value=role)
    role.delete = AsyncMock()
    return role


class TestRoleToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "list_roles",
        "get_role",
        "create_role",
        "edit_role",
        "delete_role",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestRoleToolSchemas:
    def test_create_role_requires_guild_and_name(self):
        schema = _get_tool_schema("create_role")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "name" in required

    def test_create_role_has_permissions_list(self):
        schema = _get_tool_schema("create_role")
        props = schema.get("properties", {})
        assert "permissions" in props

    def test_edit_role_requires_guild_and_role(self):
        schema = _get_tool_schema("edit_role")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "role_id" in required

    def test_delete_role_requires_guild_and_role(self):
        schema = _get_tool_schema("delete_role")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "role_id" in required


class TestRoleToolsBehavior:
    @pytest.fixture()
    def tools(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        return test_mcp._tool_manager._tools

    @pytest.fixture()
    def mock_role(self):
        return _make_role()

    @pytest.fixture()
    def mock_guild(self, mock_role):
        guild = MagicMock()
        guild.roles = [mock_role]
        guild.get_role = MagicMock(return_value=mock_role)
        guild.create_role = AsyncMock(return_value=mock_role)
        return guild

    @pytest.fixture()
    def mock_bot(self, mock_guild):
        bot = MagicMock()
        bot.get_guild = MagicMock(return_value=mock_guild)
        return bot

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_list_roles(self, mock_get_bot, tools, mock_bot, mock_role):
        mock_get_bot.return_value = mock_bot
        result = await tools["list_roles"].fn(guild_id="1")
        assert len(result) == 1
        assert result[0]["id"] == str(mock_role.id)
        assert result[0]["name"] == "Admin"
        assert result[0]["color"] == 0xFF0000
        assert result[0]["permissions"] == ["send_messages"]

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_list_roles_guild_not_found(self, mock_get_bot, tools):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await tools["list_roles"].fn(guild_id="999")

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_get_role(self, mock_get_bot, tools, mock_bot, mock_role):
        mock_get_bot.return_value = mock_bot
        result = await tools["get_role"].fn(guild_id="1", role_id="10")
        assert result["id"] == "10"
        assert result["name"] == "Admin"
        assert result["hoist"] is True
        assert result["mentionable"] is True

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_get_role_not_found(self, mock_get_bot, tools, mock_bot):
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value.get_role.return_value = None
        with pytest.raises(ValueError, match="Role 999 not found"):
            await tools["get_role"].fn(guild_id="1", role_id="999")

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_get_role_guild_not_found(self, mock_get_bot, tools):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await tools["get_role"].fn(guild_id="999", role_id="10")

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_create_role(self, mock_get_bot, tools, mock_bot, mock_guild):
        mock_get_bot.return_value = mock_bot
        result = await tools["create_role"].fn(guild_id="1", name="Mod")
        mock_guild.create_role.assert_called_once()
        call_kwargs = mock_guild.create_role.call_args.kwargs
        assert call_kwargs["name"] == "Mod"
        assert call_kwargs["hoist"] is False
        assert call_kwargs["mentionable"] is False
        assert result["id"] == "10"

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_create_role_with_color_and_permissions(
        self, mock_get_bot, tools, mock_bot, mock_guild
    ):
        mock_get_bot.return_value = mock_bot
        await tools["create_role"].fn(
            guild_id="1",
            name="Special",
            color=0x00FF00,
            permissions=["send_messages"],
        )
        call_kwargs = mock_guild.create_role.call_args.kwargs
        assert call_kwargs["color"].value == 0x00FF00
        assert call_kwargs["permissions"].send_messages is True

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_create_role_guild_not_found(self, mock_get_bot, tools):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await tools["create_role"].fn(guild_id="999", name="Test")

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_edit_role(self, mock_get_bot, tools, mock_bot, mock_role):
        mock_get_bot.return_value = mock_bot
        result = await tools["edit_role"].fn(guild_id="1", role_id="10", name="NewName")
        mock_role.edit.assert_called_once_with(name="NewName")
        assert result["id"] == "10"

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_edit_role_not_found(self, mock_get_bot, tools, mock_bot):
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value.get_role.return_value = None
        with pytest.raises(ValueError, match="Role 999 not found"):
            await tools["edit_role"].fn(guild_id="1", role_id="999", name="X")

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_delete_role(self, mock_get_bot, tools, mock_bot, mock_role):
        mock_get_bot.return_value = mock_bot
        result = await tools["delete_role"].fn(guild_id="1", role_id="10", reason="cleanup")
        mock_role.delete.assert_called_once_with(reason="cleanup")
        assert "Deleted role Admin" in result

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_delete_role_not_found(self, mock_get_bot, tools, mock_bot):
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value.get_role.return_value = None
        with pytest.raises(ValueError, match="Role 999 not found"):
            await tools["delete_role"].fn(guild_id="1", role_id="999")

    @patch("discord_mcp.tools.roles.get_bot")
    async def test_delete_role_guild_not_found(self, mock_get_bot, tools):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await tools["delete_role"].fn(guild_id="999", role_id="10")
