"""Shared test fixtures for the Discord MCP server test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import discord_mcp.bot as bot_module


# ---------------------------------------------------------------------------
# Mock Discord objects
# ---------------------------------------------------------------------------


def make_mock_user(*, id: int = 123456789, name: str = "TestBot", discriminator: str = "0001"):
    user = MagicMock()
    user.id = id
    user.name = name
    user.discriminator = discriminator
    user.__str__ = lambda self: f"{name}#{discriminator}"
    return user


def make_mock_guild(*, id: int = 111111111, name: str = "Test Guild", member_count: int = 42, owner_id: int = 999):
    guild = MagicMock()
    guild.id = id
    guild.name = name
    guild.member_count = member_count
    guild.owner_id = owner_id
    return guild


def make_mock_bot(*, ready: bool = True, guilds: list | None = None, latency: float = 0.05):
    bot = MagicMock()
    bot.user = make_mock_user()
    bot.is_ready.return_value = ready
    bot.guilds = guilds or [make_mock_guild()]
    bot.latency = latency
    bot.close = AsyncMock()
    bot.start = AsyncMock()
    return bot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_bot_state():
    """Reset the bot module global state before each test."""
    bot_module._bot = None
    bot_module._bot_task = None
    yield
    bot_module._bot = None
    bot_module._bot_task = None


@pytest.fixture()
def mock_bot():
    """A ready mock bot instance."""
    return make_mock_bot()


@pytest.fixture()
def inject_bot(mock_bot):
    """Inject a mock bot into the bot module so get_bot() works."""
    bot_module._bot = mock_bot
    return mock_bot


@pytest.fixture()
def mcp_server():
    """The FastMCP server instance with all tools registered."""
    from discord_mcp.server import mcp
    return mcp
