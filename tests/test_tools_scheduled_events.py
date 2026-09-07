"""Tests for scheduled event tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.scheduled_events import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_event(*, id=1, name="Test Event"):
    e = MagicMock()
    e.id = id
    e.name = name
    e.description = "A test event"
    e.entity_type = MagicMock(__str__=lambda s: "voice")
    e.start_time = MagicMock(__str__=lambda s: "2025-06-01 18:00:00+00:00")
    e.end_time = None
    e.status = MagicMock(__str__=lambda s: "scheduled")
    e.location = None
    e.channel = MagicMock()
    e.channel.id = 300
    e.creator_id = 400
    e.user_count = 10
    e.edit = AsyncMock(return_value=e)
    e.delete = AsyncMock()
    return e


class TestScheduledEventToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "list_scheduled_events",
        "create_scheduled_event",
        "edit_scheduled_event",
        "delete_scheduled_event",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


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


class TestScheduledEventToolsBehavior:
    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_list_scheduled_events(self, mock_get_bot):
        event = _make_event()
        guild = MagicMock()
        guild.fetch_scheduled_events = AsyncMock(return_value=[event])
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["list_scheduled_events"].fn(guild_id="1")

        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "Test Event"
        guild.fetch_scheduled_events.assert_awaited_once_with(with_counts=True)

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_list_scheduled_events_guild_not_found(self, mock_get_bot):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["list_scheduled_events"].fn(guild_id="999")

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_create_scheduled_event(self, mock_get_bot):
        event = _make_event()
        guild = MagicMock()
        guild.create_scheduled_event = AsyncMock(return_value=event)
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["create_scheduled_event"].fn(
            guild_id="1",
            name="Test Event",
            start_time="2025-06-01T18:00:00Z",
            entity_type="voice",
            channel_id="300",
        )

        assert result["name"] == "Test Event"
        guild.create_scheduled_event.assert_awaited_once()
        call_kwargs = guild.create_scheduled_event.call_args.kwargs
        assert call_kwargs["name"] == "Test Event"
        assert "channel" in call_kwargs

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_create_scheduled_event_guild_not_found(self, mock_get_bot):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["create_scheduled_event"].fn(
                guild_id="999",
                name="E",
                start_time="2025-06-01T18:00:00Z",
                entity_type="voice",
            )

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_edit_scheduled_event(self, mock_get_bot):
        event = _make_event()
        guild = MagicMock()
        guild.get_scheduled_event.return_value = event
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["edit_scheduled_event"].fn(
            guild_id="1",
            event_id="1",
            name="Updated",
        )

        assert result["name"] == "Test Event"
        event.edit.assert_awaited_once()
        assert event.edit.call_args.kwargs["name"] == "Updated"

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_edit_scheduled_event_fetches_if_not_cached(self, mock_get_bot):
        event = _make_event()
        guild = MagicMock()
        guild.get_scheduled_event.return_value = None
        guild.fetch_scheduled_event = AsyncMock(return_value=event)
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["edit_scheduled_event"].fn(
            guild_id="1",
            event_id="1",
            name="Updated",
        )

        guild.fetch_scheduled_event.assert_awaited_once_with(1)
        event.edit.assert_awaited_once()
        assert result["id"] == "1"

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_delete_scheduled_event(self, mock_get_bot):
        event = _make_event()
        guild = MagicMock()
        guild.get_scheduled_event.return_value = event
        bot = MagicMock()
        bot.get_guild.return_value = guild
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        result = await test_mcp._tool_manager._tools["delete_scheduled_event"].fn(
            guild_id="1",
            event_id="1",
        )

        assert "Deleted" in result
        assert "Test Event" in result
        event.delete.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("discord_mcp.tools.scheduled_events.get_bot")
    async def test_delete_scheduled_event_guild_not_found(self, mock_get_bot):
        bot = MagicMock()
        bot.get_guild.return_value = None
        mock_get_bot.return_value = bot

        test_mcp = FastMCP("test")
        register(test_mcp)
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["delete_scheduled_event"].fn(
                guild_id="999",
                event_id="1",
            )
