"""Tests for the shared snowflake resolvers in tools/_common.py."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from discord_mcp.tools._common import (
    require_category,
    require_editable_channel,
    require_guild,
    require_guild_channel,
    require_messageable,
    require_role,
    require_text_channel,
    require_thread,
)

CHANNEL_RESOLVERS = [
    require_messageable,
    require_guild_channel,
    require_text_channel,
    require_editable_channel,
]


class TestRequireGuild:
    def test_returns_cached_guild(self):
        guild = MagicMock()
        bot = MagicMock()
        bot.get_guild.return_value = guild

        assert require_guild(bot, "123") is guild
        bot.get_guild.assert_called_once_with(123)

    def test_raises_when_not_cached(self):
        bot = MagicMock()
        bot.get_guild.return_value = None

        with pytest.raises(ValueError, match="Guild 123 not found"):
            require_guild(bot, "123")


class TestChannelResolvers:
    @pytest.mark.parametrize("resolver", CHANNEL_RESOLVERS)
    def test_returns_cached_channel(self, resolver):
        channel = MagicMock()
        bot = MagicMock()
        bot.get_channel.return_value = channel

        assert resolver(bot, "456") is channel
        bot.get_channel.assert_called_once_with(456)

    @pytest.mark.parametrize("resolver", CHANNEL_RESOLVERS)
    def test_raises_when_not_cached(self, resolver):
        bot = MagicMock()
        bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="Channel 456 not found"):
            resolver(bot, "456")


class TestRequireThread:
    def test_returns_cached_thread(self):
        thread = MagicMock()
        bot = MagicMock()
        bot.get_channel.return_value = thread

        assert require_thread(bot, "789") is thread
        bot.get_channel.assert_called_once_with(789)

    def test_raises_with_thread_wording(self):
        bot = MagicMock()
        bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="Thread 789 not found"):
            require_thread(bot, "789")


class TestRequireRole:
    def test_returns_role(self):
        role = MagicMock()
        guild = MagicMock()
        guild.get_role.return_value = role

        assert require_role(guild, "42") is role
        guild.get_role.assert_called_once_with(42)

    def test_raises_naming_the_guild(self):
        guild = MagicMock()
        guild.id = 7
        guild.get_role.return_value = None

        with pytest.raises(ValueError, match="Role 42 not found in guild 7"):
            require_role(guild, "42")


class TestRequireCategory:
    def test_returns_none_without_an_id(self):
        guild = MagicMock()

        assert require_category(guild, None) is None
        guild.get_channel.assert_not_called()

    def test_returns_none_for_empty_string(self):
        guild = MagicMock()

        assert require_category(guild, "") is None
        guild.get_channel.assert_not_called()

    def test_resolves_a_given_id(self):
        category = MagicMock()
        guild = MagicMock()
        guild.get_channel.return_value = category

        assert require_category(guild, "5") is category
        guild.get_channel.assert_called_once_with(5)
