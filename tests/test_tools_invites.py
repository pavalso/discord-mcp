"""Tests for invite tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.invites import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestInviteToolsRegistration:
    EXPECTED = {"list_invites", "create_invite", "delete_invite", "get_invite"}

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


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


class TestInviteToolsNotImplemented:
    async def test_list_invites(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_invites"].fn(guild_id=1)

    async def test_create_invite(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_invite"].fn(channel_id=1)

    async def test_delete_invite(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_invite"].fn(invite_code="abc")

    async def test_get_invite(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["get_invite"].fn(invite_code="abc")
