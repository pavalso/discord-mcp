"""Tests for invite tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.invites import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_mock_invite(**overrides):
    invite = MagicMock()
    invite.code = overrides.get("code", "abc123")
    invite.url = overrides.get("url", "https://discord.gg/abc123")
    channel = MagicMock()
    channel.id = overrides.get("channel_id", 100)
    invite.channel = channel
    inviter = MagicMock()
    inviter.id = overrides.get("inviter_id", 200)
    invite.inviter = inviter
    invite.max_age = overrides.get("max_age", 86400)
    invite.max_uses = overrides.get("max_uses", 0)
    invite.uses = overrides.get("uses", 5)
    invite.temporary = overrides.get("temporary", False)
    invite.created_at = overrides.get("created_at", "2026-01-01 00:00:00")
    invite.expires_at = overrides.get("expires_at", "2026-01-02 00:00:00")
    invite.delete = AsyncMock()
    return invite


class TestInviteToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {"list_invites", "create_invite", "delete_invite", "get_invite"}

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestInviteToolSchemas:
    def test_create_invite_requires_channel_id(self):
        schema = _get_tool_schema("create_invite")
        assert "channel_id" in schema.get("required", [])

    def test_create_invite_has_all_options(self):
        schema = _get_tool_schema("create_invite")
        props = schema.get("properties", {})
        for field in ("max_age", "max_uses", "temporary", "unique"):
            assert field in props, f"Missing field: {field}"

    def test_delete_invite_requires_code(self):
        schema = _get_tool_schema("delete_invite")
        assert "invite_code" in schema.get("required", [])

    def test_get_invite_requires_code(self):
        schema = _get_tool_schema("get_invite")
        assert "invite_code" in schema.get("required", [])


class TestInviteToolsBehavior:
    @patch("discord_mcp.tools.invites.get_bot")
    async def test_list_invites(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_invite = _make_mock_invite()
        mock_guild.invites = AsyncMock(return_value=[mock_invite])

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["list_invites"].fn(guild_id="1")

        assert len(result) == 1
        assert result[0]["code"] == "abc123"
        assert result[0]["url"] == "https://discord.gg/abc123"
        assert result[0]["channel_id"] == "100"
        assert result[0]["inviter_id"] == "200"
        assert result[0]["uses"] == 5
        mock_bot.get_guild.assert_called_once_with(1)  # int after conversion

    @patch("discord_mcp.tools.invites.get_bot")
    async def test_list_invites_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["list_invites"].fn(guild_id="999")

    @patch("discord_mcp.tools.invites.get_bot")
    async def test_create_invite(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_channel = MagicMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_invite = _make_mock_invite()
        mock_channel.create_invite = AsyncMock(return_value=mock_invite)

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["create_invite"].fn(channel_id="100")

        assert result["code"] == "abc123"
        mock_channel.create_invite.assert_called_once_with(
            max_age=86400,
            max_uses=0,
            temporary=False,
            unique=True,
            reason=None,
        )

    @patch("discord_mcp.tools.invites.get_bot")
    async def test_create_invite_channel_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Channel 999 not found"):
            await test_mcp._tool_manager._tools["create_invite"].fn(channel_id="999")

    @patch("discord_mcp.tools.invites.get_bot")
    async def test_delete_invite(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_invite = _make_mock_invite()
        mock_bot.fetch_invite = AsyncMock(return_value=mock_invite)

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["delete_invite"].fn(invite_code="abc123")

        assert result == "Deleted invite abc123."
        mock_invite.delete.assert_called_once_with(reason=None)

    @patch("discord_mcp.tools.invites.get_bot")
    async def test_get_invite(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_invite = _make_mock_invite()
        mock_bot.fetch_invite = AsyncMock(return_value=mock_invite)

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["get_invite"].fn(invite_code="abc123")

        assert result["code"] == "abc123"
        mock_bot.fetch_invite.assert_called_once_with(
            "abc123", with_counts=True, with_expiration=True
        )
