"""Tests for discord_mcp.bot — bot lifecycle management."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import discord_mcp.bot as bot_module
from discord_mcp.bot import get_bot, start_bot, stop_bot

# ---------------------------------------------------------------------------
# get_bot
# ---------------------------------------------------------------------------


class TestGetBot:
    def test_raises_when_bot_is_none(self):
        assert bot_module._bot is None
        with pytest.raises(RuntimeError, match="not connected"):
            get_bot()

    def test_raises_when_bot_not_ready(self):
        bot = MagicMock()
        bot.is_ready.return_value = False
        bot_module._bot = bot

        with pytest.raises(RuntimeError, match="not connected"):
            get_bot()

    def test_returns_bot_when_ready(self, inject_bot):
        bot = get_bot()
        assert bot is inject_bot
        assert bot.is_ready()


# ---------------------------------------------------------------------------
# start_bot
# ---------------------------------------------------------------------------


class TestStartBot:
    async def test_returns_existing_bot_if_already_ready(self, inject_bot):
        result = await start_bot("fake-token")
        assert result is inject_bot
        inject_bot.start.assert_not_called()

    async def test_raises_on_timeout(self):
        mock_bot = MagicMock()
        mock_bot.is_ready.return_value = False
        mock_bot.start = AsyncMock(side_effect=lambda token: asyncio.sleep(999))
        mock_bot.event = MagicMock(side_effect=lambda fn: fn)

        # wait_for is patched to fire immediately so this test does not wait 30s.
        with (
            patch.object(bot_module, "_create_bot", return_value=mock_bot),
            patch("discord_mcp.bot.asyncio.wait_for", side_effect=asyncio.TimeoutError),
            pytest.raises(RuntimeError, match="failed to connect within"),
        ):
            await start_bot("fake-token")

    async def test_successful_start(self):
        mock_bot = MagicMock()
        mock_bot.is_ready.return_value = False
        mock_bot.user = MagicMock()
        mock_bot.user.name = "TestBot"

        on_ready_callback = None

        def capture_event(fn):
            nonlocal on_ready_callback
            on_ready_callback = fn
            return fn

        mock_bot.event = capture_event

        async def fake_start(token):
            assert token == "test-token"
            if on_ready_callback:
                await on_ready_callback()

        mock_bot.start = AsyncMock(side_effect=fake_start)

        with patch.object(bot_module, "_create_bot", return_value=mock_bot):
            result = await start_bot("test-token")

        assert result is mock_bot
        assert bot_module._bot is mock_bot


# ---------------------------------------------------------------------------
# stop_bot
# ---------------------------------------------------------------------------


class TestStopBot:
    async def test_stop_when_no_bot(self):
        await stop_bot()
        assert bot_module._bot is None
        assert bot_module._bot_task is None

    async def test_stop_closes_bot_and_cancels_task(self, inject_bot):
        mock_task = MagicMock()
        mock_task.cancel = MagicMock()
        bot_module._bot_task = mock_task

        await stop_bot()

        inject_bot.close.assert_awaited_once()
        mock_task.cancel.assert_called_once()
        assert bot_module._bot is None
        assert bot_module._bot_task is None

    async def test_stop_is_idempotent(self):
        await stop_bot()
        await stop_bot()
        assert bot_module._bot is None


# ---------------------------------------------------------------------------
# _create_bot
# ---------------------------------------------------------------------------


class TestCreateBot:
    def test_creates_bot_with_correct_intents(self):
        bot = bot_module._create_bot()
        assert bot.intents.message_content is True
        assert bot.intents.members is True
        assert bot.command_prefix == "!"
