"""Tests for member tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.members import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestMemberToolsRegistration:
    EXPECTED = {
        "get_member", "list_members", "search_members", "kick_member",
        "ban_member", "unban_member", "timeout_member", "edit_member",
        "add_member_roles", "remove_member_roles", "send_dm",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


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


class TestMemberToolsNotImplemented:
    async def test_get_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["get_member"].fn(guild_id=1, user_id=2)

    async def test_list_members(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_members"].fn(guild_id=1)

    async def test_search_members(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["search_members"].fn(
                guild_id=1, query="test"
            )

    async def test_kick_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["kick_member"].fn(guild_id=1, user_id=2)

    async def test_ban_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["ban_member"].fn(guild_id=1, user_id=2)

    async def test_unban_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["unban_member"].fn(guild_id=1, user_id=2)

    async def test_timeout_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["timeout_member"].fn(
                guild_id=1, user_id=2, duration_seconds=60
            )

    async def test_edit_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["edit_member"].fn(guild_id=1, user_id=2)

    async def test_add_member_roles(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["add_member_roles"].fn(
                guild_id=1, user_id=2, role_ids=[3, 4]
            )

    async def test_remove_member_roles(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["remove_member_roles"].fn(
                guild_id=1, user_id=2, role_ids=[3]
            )

    async def test_send_dm(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["send_dm"].fn(user_id=1, content="hi")
