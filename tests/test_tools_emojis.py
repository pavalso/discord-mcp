"""Tests for emoji/sticker tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.emojis import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_mock_emoji(**overrides):
    emoji = MagicMock()
    emoji.id = overrides.get("id", 1001)
    emoji.name = overrides.get("name", "test_emoji")
    emoji.animated = overrides.get("animated", False)
    emoji.available = overrides.get("available", True)
    emoji.managed = overrides.get("managed", False)
    emoji.url = overrides.get("url", "https://cdn.discordapp.com/emojis/1001.png")
    emoji.guild_id = overrides.get("guild_id", 1)
    return emoji


def _make_mock_sticker(**overrides):
    sticker = MagicMock()
    sticker.id = overrides.get("id", 2001)
    sticker.name = overrides.get("name", "test_sticker")
    sticker.description = overrides.get("description", "A test sticker")
    sticker.format = overrides.get("format", "png")
    sticker.available = overrides.get("available", True)
    sticker.guild_id = overrides.get("guild_id", 1)
    sticker.url = overrides.get("url", "https://cdn.discordapp.com/stickers/2001.png")
    return sticker


class TestEmojiToolsRegistration:
    EXPECTED = {
        "list_emojis", "create_emoji", "delete_emoji",
        "list_stickers", "delete_sticker",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


class TestEmojiToolSchemas:
    def test_create_emoji_requires_guild_name_image(self):
        schema = _get_tool_schema("create_emoji")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "name" in required
        assert "image_url" in required

    def test_delete_emoji_requires_guild_and_emoji(self):
        schema = _get_tool_schema("delete_emoji")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "emoji_id" in required

    def test_delete_sticker_requires_guild_and_sticker(self):
        schema = _get_tool_schema("delete_sticker")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "sticker_id" in required


class TestEmojiToolsBehavior:
    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_list_emojis(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_emoji = _make_mock_emoji()
        mock_guild.emojis = [mock_emoji]

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["list_emojis"].fn(guild_id="1")

        assert len(result) == 1
        assert result[0]["id"] == "1001"
        assert result[0]["name"] == "test_emoji"
        assert result[0]["animated"] is False
        mock_bot.get_guild.assert_called_once_with(1)

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_list_emojis_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["list_emojis"].fn(guild_id="999")

    @patch("discord_mcp.tools.emojis.aiohttp.ClientSession")
    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_create_emoji(self, mock_get_bot, mock_session_cls):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_emoji = _make_mock_emoji()
        mock_guild.create_custom_emoji = AsyncMock(return_value=mock_emoji)

        # Set up aiohttp mock
        mock_resp = MagicMock()
        mock_resp.read = AsyncMock(return_value=b"fake-image-data")
        mock_session = MagicMock()
        mock_session.get = MagicMock(
            return_value=MagicMock(
                __aenter__=AsyncMock(return_value=mock_resp),
                __aexit__=AsyncMock(return_value=False),
            )
        )
        mock_session_cls.return_value = MagicMock(
            __aenter__=AsyncMock(return_value=mock_session),
            __aexit__=AsyncMock(return_value=False),
        )

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["create_emoji"].fn(
            guild_id="1", name="test_emoji", image_url="https://example.com/img.png"
        )

        assert result["id"] == "1001"
        assert result["name"] == "test_emoji"
        mock_guild.create_custom_emoji.assert_called_once_with(
            name="test_emoji", image=b"fake-image-data", reason=None,
        )

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_create_emoji_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["create_emoji"].fn(
                guild_id="999", name="x", image_url="https://example.com/img.png"
            )

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_delete_emoji(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_guild.delete_emoji = AsyncMock()

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["delete_emoji"].fn(guild_id="1", emoji_id="1001")

        assert result == "Deleted emoji 1001 from guild 1."
        mock_guild.delete_emoji.assert_called_once()

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_delete_emoji_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["delete_emoji"].fn(guild_id="999", emoji_id="1001")

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_list_stickers(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_sticker = _make_mock_sticker()
        mock_guild.stickers = [mock_sticker]

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["list_stickers"].fn(guild_id="1")

        assert len(result) == 1
        assert result[0]["id"] == "2001"
        assert result[0]["name"] == "test_sticker"

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_list_stickers_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["list_stickers"].fn(guild_id="999")

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_delete_sticker(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_guild.delete_sticker = AsyncMock()

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["delete_sticker"].fn(guild_id="1", sticker_id="2001")

        assert result == "Deleted sticker 2001 from guild 1."
        mock_guild.delete_sticker.assert_called_once()

    @patch("discord_mcp.tools.emojis.get_bot")
    async def test_delete_sticker_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="Guild 999 not found"):
            await test_mcp._tool_manager._tools["delete_sticker"].fn(guild_id="999", sticker_id="2001")
