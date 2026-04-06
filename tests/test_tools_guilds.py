"""Tests for guild tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.guilds import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestGuildToolsRegistration:
    EXPECTED = {"list_guilds", "get_guild", "edit_guild"}

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


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
            "name", "description", "verification_level",
            "default_notifications", "explicit_content_filter",
            "afk_channel_id", "afk_timeout", "system_channel_id",
        ):
            assert field in props, f"Missing field: {field}"


class TestGuildToolsNotImplemented:
    async def test_list_guilds(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_guilds"].fn()

    async def test_get_guild(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["get_guild"].fn(guild_id=1)

    async def test_edit_guild(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["edit_guild"].fn(guild_id=1)
