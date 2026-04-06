"""Tests for webhook tools."""

from __future__ import annotations

import pytest

from discord_mcp.server import mcp
from discord_mcp.tools.webhooks import register
from mcp.server.fastmcp import FastMCP


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestWebhookToolsRegistration:
    EXPECTED = {
        "list_webhooks", "create_webhook", "send_webhook_message",
        "edit_webhook", "delete_webhook",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert self.EXPECTED == names


class TestWebhookToolSchemas:
    def test_send_webhook_message_requires_id_and_content(self):
        schema = _get_tool_schema("send_webhook_message")
        required = schema.get("required", [])
        assert "webhook_id" in required
        assert "content" in required

    def test_send_webhook_message_has_overrides(self):
        schema = _get_tool_schema("send_webhook_message")
        props = schema.get("properties", {})
        assert "username" in props
        assert "avatar_url" in props

    def test_create_webhook_requires_channel_and_name(self):
        schema = _get_tool_schema("create_webhook")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "name" in required


class TestWebhookToolsNotImplemented:
    async def test_list_webhooks(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["list_webhooks"].fn()

    async def test_create_webhook(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["create_webhook"].fn(
                channel_id=1, name="hook"
            )

    async def test_send_webhook_message(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["send_webhook_message"].fn(
                webhook_id=1, content="hi"
            )

    async def test_edit_webhook(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["edit_webhook"].fn(webhook_id=1)

    async def test_delete_webhook(self):
        with pytest.raises(NotImplementedError):
            test_mcp = FastMCP("test")
            register(test_mcp)
            await test_mcp._tool_manager._tools["delete_webhook"].fn(webhook_id=1)
