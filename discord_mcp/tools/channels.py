"""Channel tools — create, edit, delete, list, permissions."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def _channel_to_dict(channel: discord.abc.GuildChannel) -> dict:
    """Convert a guild channel to a serialisable dict."""
    data: dict = {
        "id": channel.id,
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "category_id": getattr(channel, "category_id", None),
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
    async def list_channels(guild_id: int) -> list[dict]:
        """List all channels in a guild.

        Args:
            guild_id: Target guild ID.

        Returns:
            List of channels with id, name, type, category, and position.
        """
        bot = get_bot()
        guild = bot.get_guild(guild_id)
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        return [_channel_to_dict(ch) for ch in guild.channels]

    @mcp.tool()
    async def get_channel(channel_id: int) -> dict:
        """Get detailed information about a channel.

        Args:
            channel_id: Target channel ID.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_text_channel(
        guild_id: int,
        name: str,
        *,
        topic: str | None = None,
        category_id: int | None = None,
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
        guild = bot.get_guild(guild_id)
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        category = guild.get_channel(category_id) if category_id else None

        channel = await guild.create_text_channel(
            name,
            topic=topic,
            category=category,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            reason=reason,
        )
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_voice_channel(
        guild_id: int,
        name: str,
        *,
        category_id: int | None = None,
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
        guild = bot.get_guild(guild_id)
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        category = guild.get_channel(category_id) if category_id else None

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
    async def create_category(
        guild_id: int,
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
        guild = bot.get_guild(guild_id)
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        channel = await guild.create_category(name, reason=reason)
        return _channel_to_dict(channel)

    @mcp.tool()
    async def create_forum_channel(
        guild_id: int,
        name: str,
        *,
        topic: str | None = None,
        category_id: int | None = None,
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
        guild = bot.get_guild(guild_id)
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        category = guild.get_channel(category_id) if category_id else None

        channel = await guild.create_forum(
            name,
            topic=topic,
            category=category,
            slowmode_delay=slowmode_delay,
            nsfw=nsfw,
            reason=reason,
        )
        return _channel_to_dict(channel)

    @mcp.tool()
    async def edit_channel(
        channel_id: int,
        *,
        name: str | None = None,
        topic: str | None = None,
        position: int | None = None,
        nsfw: bool | None = None,
        slowmode_delay: int | None = None,
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
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

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
        if reason is not None:
            kwargs["reason"] = reason

        updated = await channel.edit(**kwargs)
        return _channel_to_dict(updated or channel)

    @mcp.tool()
    async def delete_channel(
        channel_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a channel.

        Args:
            channel_id: Channel to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        await channel.delete(reason=reason)
        return f"Deleted channel {channel.name} ({channel_id})."

    @mcp.tool()
    async def set_channel_permissions(
        channel_id: int,
        target_id: int,
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
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        if target_type == "role":
            target = channel.guild.get_role(target_id)
            if target is None:
                raise ValueError(f"Role {target_id} not found.")
        elif target_type == "member":
            target = channel.guild.get_member(target_id)
            if target is None:
                target = await channel.guild.fetch_member(target_id)
        else:
            raise ValueError(f"target_type must be 'role' or 'member', got '{target_type}'.")

        overwrite = discord.PermissionOverwrite()
        for perm in (allow or []):
            setattr(overwrite, perm, True)
        for perm in (deny or []):
            setattr(overwrite, perm, False)

        await channel.set_permissions(target, overwrite=overwrite, reason=reason)
        return f"Updated permissions for {target_type} {target_id} on channel {channel_id}."
