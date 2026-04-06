"""Tests for scheduled event tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.scheduled_events import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestScheduledEventToolsRegistration:
    EXPECTED = {
        "list_scheduled_events", "create_scheduled_event",
        "edit_scheduled_event", "delete_scheduled_event",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


class TestScheduledEventToolSchemas:
    def test_create_requires_core_fields(self):
        schema = _get_tool_schema("create_scheduled_event")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "name" in required
        assert "start_time" in required
        assert "entity_type" in required

    def test_create_has_optional_fields(self):
        schema = _get_tool_schema("create_scheduled_event")
        props = schema.get("properties", {})
        for field in ("description", "end_time", "channel_id", "location"):
            assert field in props, f"Missing: {field}"

    def test_edit_requires_guild_and_event(self):
        schema = _get_tool_schema("edit_scheduled_event")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "event_id" in required

    def test_edit_has_status_field(self):
        schema = _get_tool_schema("edit_scheduled_event")
        props = schema.get("properties", {})
        assert "status" in props


class TestScheduledEventToolsNotImplemented:
    async def test_list_scheduled_events(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_scheduled_events"].fn(guild_id=1)

    async def test_create_scheduled_event(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_scheduled_event"].fn(
                guild_id=1, name="event", start_time="2025-06-01T18:00:00Z",
                entity_type="external"
            )

    async def test_edit_scheduled_event(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["edit_scheduled_event"].fn(
                guild_id=1, event_id=2
            )

    async def test_delete_scheduled_event(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_scheduled_event"].fn(
                guild_id=1, event_id=2
            )
