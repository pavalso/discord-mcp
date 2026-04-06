"""Tests for moderation tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.moderation import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


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


class TestModerationToolsNotImplemented:
    async def test_get_audit_log(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["get_audit_log"].fn(guild_id=1)

    async def test_list_bans(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_bans"].fn(guild_id=1)

    async def test_purge_messages(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["purge_messages"].fn(
                channel_id=1, limit=10
            )

    async def test_list_automod_rules(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_automod_rules"].fn(guild_id=1)

    async def test_create_automod_rule(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_automod_rule"].fn(
                guild_id=1, name="rule", trigger_type="keyword",
                actions=[{"type": "block_message"}]
            )

    async def test_delete_automod_rule(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_automod_rule"].fn(
                guild_id=1, rule_id=2
            )
