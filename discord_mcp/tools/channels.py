"""Channel tools — create, edit, delete, list, permissions."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot
from discord_mcp.tools._common import (
    require_category,
    require_editable_channel,
    require_guild,
    require_guild_channel,
    require_role,
)


def _channel_to_dict(channel: discord.abc.GuildChannel) -> dict:
    """Convert a guild channel to a serialisable dict."""
    data: dict = {
        "id": str(channel.id),
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "category_id": str(channel.category_id) if getattr(channel, "category_id", None) else None,
    }
    if hasattr(channel, "topic"):
        data["topic"] = channel.topic
    if hasattr(channel, "nsfw"):
        data["nsfw"] = channel.nsfw
    if hasattr(channel, "slowmode_delay"):
        data["slowmode_delay"] = channel.slowmode_delay
    if hasattr(channel, "bitrate"):
        data["bitrate"] = channel.bitrate
    if hasattr(channel, "user_limit"):
        data["user_limit"] = channel.user_limit
    return data


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_channels(guild_id: str) -> list[dict]:
        """List all channels in a guild.

        Args:
            guild_id: Target guild ID.

        Returns:
            List of channels with id, name, type, category, and position.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        return [_channel_to_dict(ch) for ch in guild.channels]

    @mcp.tool()
    async def get_channel(channel_id: str) -> dict:
        """Get detailed information about a channel.

        Args:
            channel_id: Target channel ID.
        """
        bot = get_bot()
        channel = require_guild_channel(bot, channel_id)
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_text_channel(
        guild_id: str,
        name: str,
        *,
        topic: str | None = None,
        category_id: str | None = None,
        slowmode_delay: int = 0,
        nsfw: bool = False,
        reason: str | None = None,
    ) -> dict:
        """Create a new text channel in a guild.

        Args:
            guild_id: Target guild.
            name: Channel name.
            topic: Channel topic/description.
            category_id: Parent category ID.
            slowmode_delay: Slowmode in seconds (0-21600).
            nsfw: Whether the channel is NSFW.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)

        category = require_category(guild, category_id)

        channel = await guild.create_text_channel(
            name,
            topic=topic,  # type: ignore[arg-type]
            category=category,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            reason=reason,
        )
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_voice_channel(
        guild_id: str,
        name: str,
        *,
        category_id: str | None = None,
        bitrate: int | None = None,
        user_limit: int = 0,
        reason: str | None = None,
    ) -> dict:
        """Create a new voice channel in a guild.

        Args:
            guild_id: Target guild.
            name: Channel name.
            category_id: Parent category ID.
            bitrate: Bitrate in bits per second (8000-384000).
            user_limit: Max users (0 = unlimited).
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)

        category = require_category(guild, category_id)

        kwargs: dict = {
            "name": name,
            "category": category,
            "user_limit": user_limit,
            "reason": reason,
        }
        if bitrate is not None:
            kwargs["bitrate"] = bitrate

        channel = await guild.create_voice_channel(**kwargs)
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_stage_channel(
        guild_id: str,
        name: str,
        *,
        category_id: str | None = None,
        topic: str | None = None,
        bitrate: int | None = None,
        user_limit: int = 0,
        reason: str | None = None,
    ) -> dict:
        """Create a new stage channel in a guild.

        Stage channels are voice channels where only designated speakers may
        talk and everyone else listens. The guild needs the COMMUNITY feature.

        Args:
            guild_id: Target guild.
            name: Channel name.
            category_id: Parent category ID.
            topic: Stage topic.
            bitrate: Bitrate in bits per second (8000-384000).
            user_limit: Max users (0 = unlimited).
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)

        category = require_category(guild, category_id)

        kwargs: dict = {
            "name": name,
            "category": category,
            "user_limit": user_limit,
            "reason": reason,
        }
        if topic is not None:
            kwargs["topic"] = topic
        if bitrate is not None:
            kwargs["bitrate"] = bitrate

        channel = await guild.create_stage_channel(**kwargs)
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_category(
        guild_id: str,
        name: str,
        *,
        reason: str | None = None,
    ) -> dict:
        """Create a new category in a guild.

        Args:
            guild_id: Target guild.
            name: Category name.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)

        channel = await guild.create_category(name, reason=reason)
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_forum_channel(
        guild_id: str,
        name: str,
        *,
        topic: str | None = None,
        category_id: str | None = None,
        slowmode_delay: int = 0,
        nsfw: bool = False,
        reason: str | None = None,
    ) -> dict:
        """Create a new forum channel in a guild.

        Args:
            guild_id: Target guild.
            name: Channel name.
            topic: Channel guidelines/topic.
            category_id: Parent category ID.
            slowmode_delay: Slowmode in seconds.
            nsfw: Whether the channel is NSFW.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)

        category = require_category(guild, category_id)

        channel = await guild.create_forum(
            name,
            topic=topic,  # type: ignore[arg-type]
            category=category,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            reason=reason,
        )
        return _channel_to_dict(channel)

    @mcp.tool()
    async def edit_channel(
        channel_id: str,
        *,
        name: str | None = None,
        topic: str | None = None,
        position: int | None = None,
        nsfw: bool | None = None,
        slowmode_delay: int | None = None,
        bitrate: int | None = None,
        user_limit: int | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a channel's settings.

        Args:
            channel_id: Channel to edit.
            name: New name.
            topic: New topic.
            position: New position.
            nsfw: New NSFW flag.
            slowmode_delay: New slowmode in seconds.
            bitrate: Bitrate in bits per second (voice channels only, 8000-384000).
            user_limit: Max users (voice channels only, 0 = unlimited).
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = require_editable_channel(bot, channel_id)

        kwargs: dict = {}
        if name is not None:
            kwargs["name"] = name
        if topic is not None:
            kwargs["topic"] = topic
        if position is not None:
            kwargs["position"] = position
        if nsfw is not None:
            kwargs["nsfw"] = nsfw
        if slowmode_delay is not None:
            kwargs["slowmode_delay"] = slowmode_delay
        if bitrate is not None:
            kwargs["bitrate"] = bitrate
        if user_limit is not None:
            kwargs["user_limit"] = user_limit
        if reason is not None:
            kwargs["reason"] = reason

        updated = await channel.edit(**kwargs)
        return _channel_to_dict(updated or channel)

    @mcp.tool()
    async def delete_channel(
        channel_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a channel.

        Args:
            channel_id: Channel to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = require_guild_channel(bot, channel_id)

        await channel.delete(reason=reason)
        return f"Deleted channel {channel.name} ({channel_id})."

    @mcp.tool()
    async def set_channel_permissions(
        channel_id: str,
        target_id: str,
        target_type: str,
        *,
        allow: list[str] | None = None,
        deny: list[str] | None = None,
        reason: str | None = None,
    ) -> str:
        """Set permission overwrites for a role or member on a channel.

        Args:
            channel_id: Target channel.
            target_id: Role or member ID.
            target_type: Either "role" or "member".
            allow: Permission names to allow (e.g. ["send_messages", "read_messages"]).
            deny: Permission names to deny.
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = require_guild_channel(bot, channel_id)

        target: discord.Role | discord.Member
        if target_type == "role":
            target = require_role(channel.guild, target_id)
        elif target_type == "member":
            cached = channel.guild.get_member(int(target_id))
            target = cached or await channel.guild.fetch_member(int(target_id))
        else:
            raise ValueError(f"target_type must be 'role' or 'member', got '{target_type}'.")

        overwrite = discord.PermissionOverwrite()
        for perm in allow or []:
            setattr(overwrite, perm, True)
        for perm in deny or []:
            setattr(overwrite, perm, False)

        await channel.set_permissions(target, overwrite=overwrite, reason=reason)
        return f"Updated permissions for {target_type} {target_id} on channel {channel_id}."
