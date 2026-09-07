"""Tests for thread tools."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.threads import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_mock_thread(**overrides):
    """Create a mock thread with sensible defaults."""
    defaults = {
        "id": 1,
        "name": "test-thread",
        "parent_id": 100,
        "owner_id": 200,
        "archived": False,
        "locked": False,
        "auto_archive_duration": 1440,
        "slowmode_delay": 0,
        "message_count": 0,
        "member_count": 1,
        "type": MagicMock(__str__=lambda s: "public_thread"),
        "created_at": None,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _build_mcp():
    """Create a fresh FastMCP and register thread tools."""
    test_mcp = FastMCP("test")
    register(test_mcp)
    return test_mcp


class TestThreadToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "create_thread",
        "edit_thread",
        "delete_thread",
        "list_active_threads",
        "join_thread",
        "leave_thread",
        "add_thread_member",
        "remove_thread_member",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


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


class TestThreadToolsBehavior:
    @patch("discord_mcp.tools.threads.get_bot")
    async def test_create_thread(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_channel = MagicMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_thread = _make_mock_thread()
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["create_thread"].fn(
            channel_id="100", name="test-thread"
        )
        assert isinstance(result, dict)
        assert result["name"] == "test-thread"
        assert result["id"] == "1"
        assert result["parent_id"] == "100"
        mock_channel.create_thread.assert_called_once()

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_create_thread_channel_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["create_thread"].fn(channel_id="999", name="thread")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_create_thread_forum_tuple(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_channel = MagicMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_thread = _make_mock_thread(name="forum-post")
        mock_message = MagicMock()
        mock_channel.create_thread = AsyncMock(return_value=(mock_thread, mock_message))

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["create_thread"].fn(
            channel_id="100", name="forum-post"
        )
        assert isinstance(result, dict)
        assert result["name"] == "forum-post"

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_create_thread_with_message_id(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_channel = MagicMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_thread = _make_mock_thread()
        mock_channel.create_thread = AsyncMock(return_value=mock_thread)

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["create_thread"].fn(
            channel_id="100", name="test-thread", message_id="555"
        )
        assert isinstance(result, dict)
        call_kwargs = mock_channel.create_thread.call_args[1]
        assert call_kwargs["message"].id == 555

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_edit_thread(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread()
        mock_bot.get_channel.return_value = mock_thread
        updated = _make_mock_thread(name="renamed")
        mock_thread.edit = AsyncMock(return_value=updated)

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["edit_thread"].fn(
            thread_id="1", name="renamed"
        )
        assert isinstance(result, dict)
        assert result["name"] == "renamed"
        mock_thread.edit.assert_called_once_with(name="renamed")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_edit_thread_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["edit_thread"].fn(thread_id="999")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_edit_thread_returns_original_when_edit_returns_none(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread(name="original")
        mock_bot.get_channel.return_value = mock_thread
        mock_thread.edit = AsyncMock(return_value=None)

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["edit_thread"].fn(thread_id="1", archived=True)
        assert isinstance(result, dict)
        assert result["name"] == "original"

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_delete_thread(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread(name="doomed")
        mock_bot.get_channel.return_value = mock_thread
        mock_thread.delete = AsyncMock()

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["delete_thread"].fn(thread_id="1")
        assert isinstance(result, str)
        assert "doomed" in result
        mock_thread.delete.assert_called_once_with(reason=None)

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_delete_thread_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["delete_thread"].fn(thread_id="999")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_list_active_threads(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_guild = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        t1 = _make_mock_thread(id=1, name="thread-1")
        t2 = _make_mock_thread(id=2, name="thread-2")
        mock_guild.active_threads = AsyncMock(return_value=[t1, t2])

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["list_active_threads"].fn(guild_id="10")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "thread-1"
        assert result[1]["name"] == "thread-2"
        mock_guild.active_threads.assert_called_once()

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_list_active_threads_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_guild.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["list_active_threads"].fn(guild_id="999")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_join_thread(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread(name="joinable")
        mock_bot.get_channel.return_value = mock_thread
        mock_thread.join = AsyncMock()

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["join_thread"].fn(thread_id="1")
        assert isinstance(result, str)
        assert "joinable" in result
        mock_thread.join.assert_called_once()

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_join_thread_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["join_thread"].fn(thread_id="999")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_leave_thread(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread(name="leaving")
        mock_bot.get_channel.return_value = mock_thread
        mock_thread.leave = AsyncMock()

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["leave_thread"].fn(thread_id="1")
        assert isinstance(result, str)
        assert "leaving" in result
        mock_thread.leave.assert_called_once()

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_leave_thread_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["leave_thread"].fn(thread_id="999")

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_add_thread_member(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread(name="members")
        mock_bot.get_channel.return_value = mock_thread
        mock_thread.add_user = AsyncMock()

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["add_thread_member"].fn(
            thread_id="1", user_id="42"
        )
        assert isinstance(result, str)
        assert "42" in result
        mock_thread.add_user.assert_called_once()
        added_obj = mock_thread.add_user.call_args[0][0]
        assert added_obj.id == 42

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_add_thread_member_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["add_thread_member"].fn(
                thread_id="999", user_id="42"
            )

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_remove_thread_member(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_thread = _make_mock_thread(name="members")
        mock_bot.get_channel.return_value = mock_thread
        mock_thread.remove_user = AsyncMock()

        test_mcp = _build_mcp()
        result = await test_mcp._tool_manager._tools["remove_thread_member"].fn(
            thread_id="1", user_id="42"
        )
        assert isinstance(result, str)
        assert "42" in result
        mock_thread.remove_user.assert_called_once()
        removed_obj = mock_thread.remove_user.call_args[0][0]
        assert removed_obj.id == 42

    @patch("discord_mcp.tools.threads.get_bot")
    async def test_remove_thread_member_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_get_bot.return_value = mock_bot
        mock_bot.get_channel.return_value = None

        test_mcp = _build_mcp()
        with pytest.raises(ValueError, match="not found"):
            await test_mcp._tool_manager._tools["remove_thread_member"].fn(
                thread_id="999", user_id="42"
            )
