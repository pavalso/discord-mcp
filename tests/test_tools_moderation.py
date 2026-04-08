"""Tests for moderation tools."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.moderation import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_audit_entry(*, id=1, action="ban", user_id=100, target=None, reason=None):
    entry = MagicMock()
    entry.id = id
    entry.action = MagicMock(__str__=lambda s: action)
    entry.user_id = user_id
    entry.target = target
    entry.reason = reason
    entry.created_at = MagicMock(__str__=lambda s: "2025-01-01")
    return entry


def _make_ban_entry(*, user_id=200, user_name="Banned", reason="spam"):
    entry = MagicMock()
    entry.user = MagicMock()
    entry.user.id = user_id
    entry.user.name = user_name
    entry.reason = reason
    return entry


def _make_automod_rule(*, id=1, name="TestRule"):
    rule = MagicMock()
    rule.id = id
    rule.name = name
    rule.enabled = True
    rule.creator_id = 500
    rule.trigger = MagicMock()
    rule.trigger.type = MagicMock(__str__=lambda s: "keyword")
    rule.event_type = MagicMock(__str__=lambda s: "message_send")
    rule.exempt_role_ids = {10, 20}
    rule.exempt_channel_ids = {30}
    rule.delete = AsyncMock()
    return rule


class TestModerationToolsRegistration:
    EXPECTED = {
        "get_audit_log", "list_bans", "purge_messages",
        "list_automod_rules", "create_automod_rule", "delete_automod_rule",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


class TestModerationToolSchemas:
    def test_get_audit_log_requires_guild(self):
        schema = _get_tool_schema("get_audit_log")
        assert "guild_id" in schema.get("required", [])

    def test_get_audit_log_has_filters(self):
        schema = _get_tool_schema("get_audit_log")
        props = schema.get("properties", {})
        assert "user_id" in props
        assert "action_type" in props
        assert "limit" in props

    def test_purge_messages_requires_channel_and_limit(self):
        schema = _get_tool_schema("purge_messages")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "limit" in required

    def test_purge_messages_has_filters(self):
        schema = _get_tool_schema("purge_messages")
        props = schema.get("properties", {})
        for field in ("user_id", "contains", "before_message_id", "after_message_id"):
            assert field in props, f"Missing: {field}"

    def test_create_automod_rule_requires_core_fields(self):
        schema = _get_tool_schema("create_automod_rule")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "name" in required
        assert "trigger_type" in required
        assert "actions" in required

    def test_create_automod_rule_actions_is_array(self):
        schema = _get_tool_schema("create_automod_rule")
        props = schema.get("properties", {})
        assert props["actions"]["type"] == "array"

    def test_create_automod_rule_has_exemptions(self):
        schema = _get_tool_schema("create_automod_rule")
        props = schema.get("properties", {})
        assert "exempt_role_ids" in props
        assert "exempt_channel_ids" in props


class TestModerationToolsBehavior:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.test_mcp = FastMCP("test")
        register(self.test_mcp)
        self.tools = self.test_mcp._tool_manager._tools

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_get_audit_log(self, mock_get_bot):
        mock_guild = MagicMock()
        entry = _make_audit_entry(id=1, action="ban", user_id=100, reason="abuse")

        async def mock_audit_logs(**kwargs):
            for e in [entry]:
                yield e

        mock_guild.audit_logs = mock_audit_logs
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["get_audit_log"].fn(guild_id="1")
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["reason"] == "abuse"

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_get_audit_log_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="not found"):
            await self.tools["get_audit_log"].fn(guild_id="999")

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_list_bans(self, mock_get_bot):
        mock_guild = MagicMock()
        ban = _make_ban_entry(user_id=200, user_name="BadUser", reason="spam")

        async def mock_bans(**kwargs):
            for b in [ban]:
                yield b

        mock_guild.bans = mock_bans
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["list_bans"].fn(guild_id="1")
        assert len(result) == 1
        assert result[0]["user_id"] == "200"
        assert result[0]["user_name"] == "BadUser"
        assert result[0]["reason"] == "spam"

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_list_bans_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="not found"):
            await self.tools["list_bans"].fn(guild_id="999")

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_purge_messages(self, mock_get_bot):
        mock_channel = MagicMock()
        mock_channel.purge = AsyncMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_bot = MagicMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_get_bot.return_value = mock_bot

        result = await self.tools["purge_messages"].fn(channel_id="1", limit=10)
        assert "3 message(s)" in result
        mock_channel.purge.assert_awaited_once()

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_purge_messages_with_filters(self, mock_get_bot):
        mock_channel = MagicMock()
        mock_channel.purge = AsyncMock(return_value=[MagicMock()])
        mock_bot = MagicMock()
        mock_bot.get_channel.return_value = mock_channel
        mock_get_bot.return_value = mock_bot

        result = await self.tools["purge_messages"].fn(
            channel_id="1", limit=5, user_id="42", contains="bad"
        )
        assert "1 message(s)" in result
        call_kwargs = mock_channel.purge.call_args.kwargs
        assert "check" in call_kwargs
        assert call_kwargs["limit"] == 5

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_purge_messages_channel_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_channel.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="not found"):
            await self.tools["purge_messages"].fn(channel_id="999", limit=10)

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_list_automod_rules(self, mock_get_bot):
        mock_guild = MagicMock()
        rule = _make_automod_rule(id=1, name="NoSpam")
        mock_guild.fetch_automod_rules = AsyncMock(return_value=[rule])
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["list_automod_rules"].fn(guild_id="1")
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "NoSpam"
        assert result[0]["enabled"] is True

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_create_automod_rule(self, mock_get_bot):
        mock_guild = MagicMock()
        rule = _make_automod_rule(id=5, name="BlockBadWords")
        mock_guild.create_automod_rule = AsyncMock(return_value=rule)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["create_automod_rule"].fn(
            guild_id="1", name="BlockBadWords", trigger_type="keyword",
            actions=[{"type": "block_message"}],
            keyword_filter=["badword"],
        )
        assert result["id"] == "5"
        assert result["name"] == "BlockBadWords"
        mock_guild.create_automod_rule.assert_awaited_once()

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_create_automod_rule_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="not found"):
            await self.tools["create_automod_rule"].fn(
                guild_id="999", name="x", trigger_type="keyword",
                actions=[{"type": "block_message"}],
            )

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_delete_automod_rule(self, mock_get_bot):
        mock_guild = MagicMock()
        rule = _make_automod_rule(id=3, name="OldRule")
        mock_guild.fetch_automod_rule = AsyncMock(return_value=rule)
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = mock_guild
        mock_get_bot.return_value = mock_bot

        result = await self.tools["delete_automod_rule"].fn(guild_id="1", rule_id="3", reason="cleanup")
        assert "OldRule" in result
        rule.delete.assert_awaited_once_with(reason="cleanup")

    @patch("discord_mcp.tools.moderation.get_bot")
    async def test_delete_automod_rule_guild_not_found(self, mock_get_bot):
        mock_bot = MagicMock()
        mock_bot.get_guild.return_value = None
        mock_get_bot.return_value = mock_bot

        with pytest.raises(ValueError, match="not found"):
            await self.tools["delete_automod_rule"].fn(guild_id="999", rule_id="1")
