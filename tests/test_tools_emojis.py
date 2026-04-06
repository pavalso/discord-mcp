"""Tests for emoji/sticker tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.emojis import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


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


class TestEmojiToolsNotImplemented:
    async def test_list_emojis(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_emojis"].fn(guild_id=1)

    async def test_create_emoji(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_emoji"].fn(
                guild_id=1, name="test", image_url="https://example.com/img.png"
            )

    async def test_delete_emoji(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_emoji"].fn(guild_id=1, emoji_id=2)

    async def test_list_stickers(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_stickers"].fn(guild_id=1)

    async def test_delete_sticker(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_sticker"].fn(
                guild_id=1, sticker_id=2
            )
