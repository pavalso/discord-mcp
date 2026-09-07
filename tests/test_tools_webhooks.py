"""Tests for webhook tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.webhooks import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_webhook(*, id=1, name="TestHook"):
    w = MagicMock()
    w.id = id
    w.name = name
    w.type = MagicMock(__str__=lambda s: "incoming")
    w.guild_id = 100
    w.channel_id = 200
    w.url = "https://discord.com/api/webhooks/1/token"
    w.created_at = MagicMock(__str__=lambda s: "2025-01-01")
    w.send = AsyncMock()
    w.edit = AsyncMock(return_value=w)
    w.delete = AsyncMock()
    return w


class TestWebhookToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "list_webhooks",
        "create_webhook",
        "send_webhook_message",
        "edit_webhook",
        "delete_webhook",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestWebhookToolSchemas:
    def test_send_webhook_message_requires_id_and_content(self):
        schema = _get_tool_schema("send_webhook_message")
        required = schema.get("required", [])
        assert "webhook_id" in required
        assert "content" in required

    def test_send_webhook_message_has_overrides(self):
        schema = _get_tool_schema("send_webhook_message")
        props = schema.get("properties", {})
        assert "username" in props
        assert "avatar_url" in props

    def test_create_webhook_requires_channel_and_name(self):
        schema = _get_tool_schema("create_webhook")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "name" in required


class TestWebhookToolsBehavior:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.test_mcp = FastMCP("test")
        register(self.test_mcp)
        self.tools = self.test_mcp._tool_manager._tools

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_list_webhooks_by_channel(self, mock_get_bot):
        hook = _make_webhook()
        channel = MagicMock()
        channel.webhooks = AsyncMock(return_value=[hook])
        bot = MagicMock()
        bot.get_channel.return_value = channel
        mock_get_bot.return_value = bot

        result = await self.tools["list_webhooks"].fn(channel_id="200")
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "TestHook"
        bot.get_channel.assert_called_once_with(200)

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_list_webhooks_by_guild(self, mock_get_bot):
        hook = _make_webhook()
        guild = MagicMock()
        guild.webhooks = AsyncMock(return_value=[hook])
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        result = await self.tools["list_webhooks"].fn(guild_id="100")
        assert len(result) == 1
        assert result[0]["guild_id"] == "100"
        bot.get_guild.assert_called_once_with(100)

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_list_webhooks_no_args(self, mock_get_bot):
        mock_get_bot.return_value = MagicMock()
        with pytest.raises(ValueError, match="At least one"):
            await self.tools["list_webhooks"].fn()

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_list_webhooks_channel_not_found(self, mock_get_bot):
        bot = MagicMock()
        bot.get_channel.return_value = None
        mock_get_bot.return_value = bot
        with pytest.raises(ValueError, match="Channel 999 not found"):
            await self.tools["list_webhooks"].fn(channel_id="999")

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_list_webhooks_guild_not_found(self, mock_get_bot):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await self.tools["list_webhooks"].fn(guild_id="999")

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_create_webhook(self, mock_get_bot):
        hook = _make_webhook(id=42, name="NewHook")
        channel = MagicMock()
        channel.create_webhook = AsyncMock(return_value=hook)
        bot = MagicMock()
        bot.get_channel.return_value = channel
        mock_get_bot.return_value = bot

        result = await self.tools["create_webhook"].fn(channel_id="200", name="NewHook")
        assert result["id"] == "42"
        assert result["name"] == "NewHook"
        channel.create_webhook.assert_called_once_with(name="NewHook", reason=None)

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_send_webhook_message(self, mock_get_bot):
        hook = _make_webhook()
        msg = MagicMock()
        msg.id = 555
        msg.content = "hello"
        msg.channel.id = 200
        hook.send = AsyncMock(return_value=msg)

        bot = MagicMock()
        bot.fetch_webhook = AsyncMock(return_value=hook)
        mock_get_bot.return_value = bot

        result = await self.tools["send_webhook_message"].fn(webhook_id="1", content="hello")
        assert result["id"] == "555"
        assert result["content"] == "hello"
        assert result["channel_id"] == "200"
        hook.send.assert_called_once_with("hello", wait=True)

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_send_webhook_message_with_thread(self, mock_get_bot):
        hook = _make_webhook()
        msg = MagicMock()
        msg.id = 556
        msg.content = "threaded"
        msg.channel.id = 200
        hook.send = AsyncMock(return_value=msg)

        bot = MagicMock()
        bot.fetch_webhook = AsyncMock(return_value=hook)
        mock_get_bot.return_value = bot

        result = await self.tools["send_webhook_message"].fn(
            webhook_id="1", content="threaded", thread_id="999"
        )
        assert result["id"] == "556"
        call_kwargs = hook.send.call_args
        assert call_kwargs[1]["thread"].id == 999

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_edit_webhook(self, mock_get_bot):
        hook = _make_webhook(id=10, name="Edited")
        hook.edit = AsyncMock(return_value=hook)

        bot = MagicMock()
        bot.fetch_webhook = AsyncMock(return_value=hook)
        mock_get_bot.return_value = bot

        result = await self.tools["edit_webhook"].fn(webhook_id="10", name="Edited")
        assert result["id"] == "10"
        assert result["name"] == "Edited"
        hook.edit.assert_called_once_with(name="Edited")

    @patch("discord_mcp.tools.webhooks.get_bot")
    async def test_delete_webhook(self, mock_get_bot):
        hook = _make_webhook(id=10, name="Doomed")

        bot = MagicMock()
        bot.fetch_webhook = AsyncMock(return_value=hook)
        mock_get_bot.return_value = bot

        result = await self.tools["delete_webhook"].fn(webhook_id="10")
        assert "Doomed" in result
        assert "10" in result
        hook.delete.assert_called_once_with(reason=None)
