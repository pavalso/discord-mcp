"""Guild tools — list, info, settings."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def _guild_to_dict(guild: discord.Guild) -> dict:
    """Convert a guild to a serialisable dict."""
    return {
        "id": str(guild.id),
        "name": guild.name,
        "description": guild.description,
        "owner_id": str(guild.owner_id),
        "member_count": guild.member_count,
        "icon": str(guild.icon) if guild.icon else None,
        "premium_tier": guild.premium_tier,
        "premium_subscription_count": guild.premium_subscription_count,
        "features": guild.features,
        "verification_level": str(guild.verification_level),
        "default_notifications": str(guild.default_notifications),
        "explicit_content_filter": str(guild.explicit_content_filter),
        "afk_timeout": guild.afk_timeout,
        "afk_channel_id": str(guild.afk_channel.id) if guild.afk_channel else None,
        "system_channel_id": str(guild.system_channel.id) if guild.system_channel else None,
    }


VERIFICATION_MAP = {
    "none": discord.VerificationLevel.none,
    "low": discord.VerificationLevel.low,
    "medium": discord.VerificationLevel.medium,
    "high": discord.VerificationLevel.high,
    "highest": discord.VerificationLevel.highest,
}

NOTIFICATION_MAP = {
    "all_messages": discord.NotificationLevel.all_messages,
    "only_mentions": discord.NotificationLevel.only_mentions,
}

CONTENT_FILTER_MAP = {
    "disabled": discord.ContentFilter.disabled,
    "members_without_roles": discord.ContentFilter.no_role,
    "all_members": discord.ContentFilter.all_members,
}


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_guilds() -> list[dict]:
        """List all guilds the bot is a member of.

        Returns:
            List of guilds with id, name, member_count, and owner_id.
        """
        bot = get_bot()
        return [_guild_to_dict(g) for g in bot.guilds]

    @mcp.tool()
    async def get_guild(guild_id: str) -> dict:
        """Get detailed information about a guild.

        Args:
            guild_id: Target guild ID.

        Returns:
            Guild details including name, description, owner, member count,
            channel count, role count, premium tier, features, etc.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        return _guild_to_dict(guild)

    @mcp.tool()
    async def edit_guild(
        guild_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        verification_level: str | None = None,
        default_notifications: str | None = None,
        explicit_content_filter: str | None = None,
        afk_channel_id: str | None = None,
        afk_timeout: int | None = None,
        system_channel_id: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit guild settings.

        Args:
            guild_id: Target guild.
            name: New guild name.
            description: New description.
            verification_level: "none", "low", "medium", "high", or "highest".
            default_notifications: "all_messages" or "only_mentions".
            explicit_content_filter: "disabled", "members_without_roles", or "all_members".
            afk_channel_id: AFK voice channel ID.
            afk_timeout: AFK timeout in seconds.
            system_channel_id: System messages channel ID.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        kwargs: dict = {}
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if verification_level is not None:
            kwargs["verification_level"] = VERIFICATION_MAP[verification_level]
        if default_notifications is not None:
            kwargs["default_notifications"] = NOTIFICATION_MAP[default_notifications]
        if explicit_content_filter is not None:
            kwargs["explicit_content_filter"] = CONTENT_FILTER_MAP[explicit_content_filter]
        if afk_channel_id is not None:
            kwargs["afk_channel"] = guild.get_channel(int(afk_channel_id))
        if afk_timeout is not None:
            kwargs["afk_timeout"] = afk_timeout
        if system_channel_id is not None:
            kwargs["system_channel"] = guild.get_channel(int(system_channel_id))
        if reason is not None:
            kwargs["reason"] = reason

        updated = await guild.edit(**kwargs)
        return _guild_to_dict(updated or guild)
