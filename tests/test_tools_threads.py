"""Tests for thread tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.threads import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestThreadToolsRegistration:
    EXPECTED = {
        "create_thread", "edit_thread", "delete_thread", "list_active_threads",
        "join_thread", "leave_thread", "add_thread_member", "remove_thread_member",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


class TestThreadToolSchemas:
    def test_create_thread_requires_channel_and_name(self):
        schema = _get_tool_schema("create_thread")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "name" in required

    def test_create_thread_message_id_optional(self):
        schema = _get_tool_schema("create_thread")
        assert "message_id" not in schema.get("required", [])

    def test_edit_thread_only_requires_id(self):
        schema = _get_tool_schema("edit_thread")
        assert schema.get("required", []) == ["thread_id"]

    def test_add_thread_member_requires_both_ids(self):
        schema = _get_tool_schema("add_thread_member")
        required = schema.get("required", [])
        assert "thread_id" in required
        assert "user_id" in required


class TestThreadToolsNotImplemented:
    async def test_create_thread(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_thread"].fn(
                channel_id=1, name="thread"
            )

    async def test_edit_thread(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["edit_thread"].fn(thread_id=1)

    async def test_delete_thread(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_thread"].fn(thread_id=1)

    async def test_list_active_threads(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_active_threads"].fn(guild_id=1)

    async def test_join_thread(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["join_thread"].fn(thread_id=1)

    async def test_leave_thread(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["leave_thread"].fn(thread_id=1)

    async def test_add_thread_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["add_thread_member"].fn(
                thread_id=1, user_id=2
            )

    async def test_remove_thread_member(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["remove_thread_member"].fn(
                thread_id=1, user_id=2
            )
