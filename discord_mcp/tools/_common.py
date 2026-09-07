"""Shared resolvers turning snowflake strings into live discord.py objects.

Every tool starts the same way: take an ID string, look the object up in the
bot's cache, and fail with a consistent message when it is not there. These
helpers hold that logic once instead of in ~70 call sites.

They also solve a typing problem. ``Bot.get_channel()`` is declared as
returning a seven-way union (text, voice, stage, forum, category, thread,
private), so ``channel.fetch_message(...)`` is an error under mypy even though
the tool only ever receives the right kind of channel. The resolvers below
narrow that union with ``cast``.

``cast`` and not ``isinstance`` is deliberate. The real guarantee comes from
Discord: a channel ID the caller passes to ``send_message`` resolves to
something messageable, and if it does not, discord.py raises ``AttributeError``
at the call. Adding ``isinstance`` gates would change that behaviour rather than
just describe it, and would reject the ``MagicMock`` channels the test suite is
built on. The narrowing therefore documents the contract for the type checker
and leaves runtime behaviour exactly as it was.

The ``bot`` is passed in rather than fetched via ``get_bot()`` here, so the
per-module ``get_bot`` symbol each test patches stays the one that is called.
"""

from __future__ import annotations

from typing import Any, cast

import discord
from discord.ext import commands


def require_guild(bot: commands.Bot, guild_id: str) -> discord.Guild:
    """Resolve a guild the bot is in, or raise."""
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        raise ValueError(f"Guild {guild_id} not found (not in cache).")
    return guild


def _resolve_channel(
    bot: commands.Bot, channel_id: str
) -> discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel:
    """Resolve any channel by ID, or raise. Callers narrow the result."""
    channel = bot.get_channel(int(channel_id))
    if channel is None:
        raise ValueError(f"Channel {channel_id} not found (not in cache).")
    return channel


def require_messageable(bot: commands.Bot, channel_id: str) -> discord.abc.Messageable:
    """A channel that can send, fetch, and list messages."""
    return cast(discord.abc.Messageable, _resolve_channel(bot, channel_id))


def require_guild_channel(bot: commands.Bot, channel_id: str) -> discord.abc.GuildChannel:
    """A channel that lives in a guild, so it has name, guild, edit, and delete."""
    return cast(discord.abc.GuildChannel, _resolve_channel(bot, channel_id))


def require_text_channel(bot: commands.Bot, channel_id: str) -> discord.TextChannel:
    """A text channel, for the operations only it supports (webhooks, purge)."""
    return cast(discord.TextChannel, _resolve_channel(bot, channel_id))


def require_editable_channel(bot: commands.Bot, channel_id: str) -> Any:
    """Any guild channel, for the generic edit tool.

    Typed ``Any`` on purpose: ``edit()`` is defined on each concrete channel
    class rather than on the ``GuildChannel`` base, and each one accepts a
    different set of kwargs (``topic`` for text, ``bitrate`` for voice). There
    is no single type that describes "whatever channel this ID names".
    """
    return _resolve_channel(bot, channel_id)


def require_category(
    guild: discord.Guild, category_id: str | None
) -> discord.CategoryChannel | None:
    """Resolve an optional parent category. ``None`` in, ``None`` out."""
    if not category_id:
        return None
    return cast(discord.CategoryChannel, guild.get_channel(int(category_id)))


def require_thread(bot: commands.Bot, thread_id: str) -> discord.Thread:
    """Resolve a thread by ID, or raise."""
    thread = bot.get_channel(int(thread_id))
    if thread is None:
        raise ValueError(f"Thread {thread_id} not found (not in cache).")
    return cast(discord.Thread, thread)


def require_role(guild: discord.Guild, role_id: str) -> discord.Role:
    """Resolve a role within a guild, or raise."""
    role = guild.get_role(int(role_id))
    if role is None:
        raise ValueError(f"Role {role_id} not found in guild {guild.id}.")
    return role
