"""Tests for role tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.roles import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestRoleToolsRegistration:
    EXPECTED = {"list_roles", "get_role", "create_role", "edit_role", "delete_role"}

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


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


class TestRoleToolsNotImplemented:
    async def test_list_roles(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_roles"].fn(guild_id=1)

    async def test_get_role(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["get_role"].fn(guild_id=1, role_id=2)

    async def test_create_role(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_role"].fn(
                guild_id=1, name="admin"
            )

    async def test_edit_role(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["edit_role"].fn(guild_id=1, role_id=2)

    async def test_delete_role(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_role"].fn(guild_id=1, role_id=2)
