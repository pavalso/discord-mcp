"""Tests for discord_mcp.server — MCP server setup and connection tools."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

from tests.conftest import make_mock_bot

# ---------------------------------------------------------------------------
# Server initialization & tool registration
# ---------------------------------------------------------------------------


class TestServerSetup:
    def test_server_name(self, mcp_server):
        assert mcp_server.name == "Discord MCP Server"

    def test_total_tool_count(self, mcp_server):
        tools = mcp_server._tool_manager.list_tools()
        assert len(tools) == 92

    def test_all_tools_have_descriptions(self, mcp_server):
        tools = mcp_server._tool_manager.list_tools()
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' has no description"

    def test_no_duplicate_tool_names(self, mcp_server):
        tools = mcp_server._tool_manager.list_tools()
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), (
            f"Duplicate tools: {[n for n in names if names.count(n) > 1]}"
        )


EXPECTED_TOOL_NAMES = {
    # Connection
    "connect",
    "disconnect",
    "bot_status",
    "change_presence",
    # Messages
    "send_message",
    "send_embed",
    "edit_message",
    "delete_message",
    "get_message",
    "get_message_history",
    "pin_message",
    "unpin_message",
    "get_pinned_messages",
    "add_reaction",
    "remove_reaction",
    "clear_reactions",
    # Channels
    "list_channels",
    "get_channel",
    "create_text_channel",
    "create_voice_channel",
    "create_stage_channel",
    "create_category",
    "create_forum_channel",
    "edit_channel",
    "delete_channel",
    "set_channel_permissions",
    # Threads
    "create_thread",
    "edit_thread",
    "delete_thread",
    "list_active_threads",
    "list_archived_threads",
    "join_thread",
    "leave_thread",
    "add_thread_member",
    "remove_thread_member",
    # Members
    "get_user",
    "get_member",
    "list_members",
    "search_members",
    "kick_member",
    "ban_member",
    "unban_member",
    "timeout_member",
    "edit_member",
    "add_member_roles",
    "remove_member_roles",
    "send_dm",
    # Roles
    "list_roles",
    "get_role",
    "create_role",
    "edit_role",
    "delete_role",
    # Guilds
    "list_guilds",
    "get_guild",
    "edit_guild",
    "leave_guild",
    # Webhooks
    "list_webhooks",
    "create_webhook",
    "send_webhook_message",
    "edit_webhook",
    "delete_webhook",
    # Invites
    "list_invites",
    "create_invite",
    "delete_invite",
    "get_invite",
    # Emojis
    "list_emojis",
    "create_emoji",
    "edit_emoji",
    "delete_emoji",
    "list_stickers",
    "create_sticker",
    "edit_sticker",
    "delete_sticker",
    # Scheduled events
    "list_scheduled_events",
    "create_scheduled_event",
    "edit_scheduled_event",
    "delete_scheduled_event",
    # Moderation
    "get_audit_log",
    "list_bans",
    "purge_messages",
    "list_automod_rules",
    "create_automod_rule",
    "delete_automod_rule",
    # Voice
    "join_voice",
    "leave_voice",
    "voice_status",
    "set_voice_state",
    "play_audio",
    "stop_audio",
    "pause_audio",
    "resume_audio",
    "set_volume",
}


class TestToolRegistration:
    def test_expected_tools_are_registered(self, mcp_server):
        tools = mcp_server._tool_manager.list_tools()
        registered = {t.name for t in tools}
        missing = EXPECTED_TOOL_NAMES - registered
        extra = registered - EXPECTED_TOOL_NAMES
        assert not missing, f"Missing tools: {missing}"
        assert not extra, f"Unexpected extra tools: {extra}"

    def test_each_module_registers_tools(self, mcp_server):
        tools = mcp_server._tool_manager.list_tools()
        names = {t.name for t in tools}

        module_markers = {
            "messages": "send_message",
            "channels": "create_text_channel",
            "threads": "create_thread",
            "members": "kick_member",
            "roles": "create_role",
            "guilds": "list_guilds",
            "webhooks": "create_webhook",
            "invites": "create_invite",
            "emojis": "create_emoji",
            "scheduled_events": "create_scheduled_event",
            "moderation": "get_audit_log",
        }

        for module, marker in module_markers.items():
            assert marker in names, f"Module '{module}' did not register tool '{marker}'"


# ---------------------------------------------------------------------------
# Connection tools (connect, disconnect, bot_status)
# ---------------------------------------------------------------------------


class TestConnectTool:
    async def test_connect_no_token_no_env(self, mcp_server):
        with patch.dict(os.environ, {}, clear=True):
            from discord_mcp.server import connect

            result = await connect(token=None)
            assert "Error" in result
            assert "No token" in result

    async def test_connect_with_token(self, mcp_server):
        mock_bot = make_mock_bot()
        with patch("discord_mcp.server.start_bot", new_callable=AsyncMock, return_value=mock_bot):
            from discord_mcp.server import connect

            result = await connect(token="test-token-123")
            assert "Connected as" in result
            assert str(mock_bot.user.id) in result

    async def test_connect_uses_env_var(self, mcp_server):
        mock_bot = make_mock_bot()
        with (
            patch.dict(os.environ, {"DISCORD_BOT_TOKEN": "env-token"}),
            patch(
                "discord_mcp.server.start_bot", new_callable=AsyncMock, return_value=mock_bot
            ) as mock_start,
        ):
            from discord_mcp.server import connect

            result = await connect(token=None)
            mock_start.assert_awaited_once_with("env-token")
            assert "Connected as" in result

    async def test_connect_token_overrides_env(self, mcp_server):
        mock_bot = make_mock_bot()
        with (
            patch.dict(os.environ, {"DISCORD_BOT_TOKEN": "env-token"}),
            patch(
                "discord_mcp.server.start_bot", new_callable=AsyncMock, return_value=mock_bot
            ) as mock_start,
        ):
            from discord_mcp.server import connect

            await connect(token="explicit-token")
            mock_start.assert_awaited_once_with("explicit-token")


class TestDisconnectTool:
    async def test_disconnect(self, mcp_server):
        with patch("discord_mcp.server.stop_bot", new_callable=AsyncMock) as mock_stop:
            from discord_mcp.server import disconnect

            result = await disconnect()
            assert result == "Disconnected."
            mock_stop.assert_awaited_once()


class TestBotStatusTool:
    async def test_status_when_not_connected(self, mcp_server):
        from discord_mcp.server import bot_status

        result = await bot_status()
        assert result == {"connected": False}

    async def test_status_when_connected(self, inject_bot, mcp_server):
        from discord_mcp.server import bot_status

        result = await bot_status()
        assert result["connected"] is True
        assert result["user"] == str(inject_bot.user)
        assert result["user_id"] == str(inject_bot.user.id)
        assert result["guild_count"] == len(inject_bot.guilds)
        assert isinstance(result["latency_ms"], float)


class TestChangePresenceTool:
    async def test_change_status(self, inject_bot, mcp_server):
        from discord_mcp.server import change_presence

        inject_bot.change_presence = AsyncMock()
        result = await change_presence(status="dnd")
        assert "status=dnd" in result
        inject_bot.change_presence.assert_awaited_once()

    async def test_change_activity(self, inject_bot, mcp_server):
        from discord_mcp.server import change_presence

        inject_bot.change_presence = AsyncMock()
        result = await change_presence(activity_type="playing", activity_name="a game")
        assert "playing" in result
        assert "a game" in result

    async def test_invalid_status(self, inject_bot, mcp_server):
        from discord_mcp.server import change_presence

        result = await change_presence(status="bad")
        assert "Error" in result

    async def test_invalid_activity_type(self, inject_bot, mcp_server):
        from discord_mcp.server import change_presence

        result = await change_presence(activity_type="bad", activity_name="x")
        assert "Error" in result

    async def test_activity_type_without_name(self, inject_bot, mcp_server):
        from discord_mcp.server import change_presence

        result = await change_presence(activity_type="playing")
        assert "Error" in result
        assert "activity_name" in result

    async def test_no_args_resets(self, inject_bot, mcp_server):
        from discord_mcp.server import change_presence

        inject_bot.change_presence = AsyncMock()
        result = await change_presence()
        assert "default" in result.lower()
