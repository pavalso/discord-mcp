"""Member tools — fetch, kick, ban, timeout, role assignment, DM."""

from __future__ import annotations

import datetime

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot
from discord_mcp.tools._common import require_guild, require_role


def _member_to_dict(member: discord.Member) -> dict:
    """Convert a guild member to a serialisable dict."""
    return {
        "id": str(member.id),
        "name": member.name,
        "display_name": member.display_name,
        "nick": member.nick,
        "bot": member.bot,
        "joined_at": str(member.joined_at) if member.joined_at else None,
        "roles": [{"id": str(r.id), "name": r.name} for r in member.roles],
        "top_role": {"id": str(member.top_role.id), "name": member.top_role.name},
        "premium_since": str(member.premium_since) if member.premium_since else None,
        "timed_out_until": str(member.timed_out_until) if member.timed_out_until else None,
        "pending": member.pending,
    }


def _user_to_dict(user: discord.User) -> dict:
    """Convert a global user (not a guild member) to a serialisable dict."""
    return {
        "id": str(user.id),
        "name": user.name,
        "global_name": user.global_name,
        "display_name": user.display_name,
        "bot": user.bot,
        "system": user.system,
        "avatar_url": str(user.display_avatar.url),
        "banner_url": str(user.banner.url) if user.banner else None,
        "accent_color": user.accent_color.value if user.accent_color else None,
        "created_at": str(user.created_at),
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_user(user_id: str) -> dict:
        """Fetch a Discord user by ID, whether or not they share a guild with the bot.

        get_member returns richer, guild-scoped data (nickname, roles, join date)
        but only works for members of a guild the bot is in. This works for any
        user, and returns only their global profile.

        Args:
            user_id: Target user ID.
        """
        bot = get_bot()
        user = await bot.fetch_user(int(user_id))
        return _user_to_dict(user)

    @mcp.tool()
    async def get_member(
        guild_id: str,
        user_id: str,
    ) -> dict:
        """Fetch detailed information about a guild member.

        Args:
            guild_id: Guild the member belongs to.
            user_id: The member's user ID.

        Returns:
            Member details including name, nickname, roles, join date, etc.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        member = await guild.fetch_member(int(user_id))
        return _member_to_dict(member)

    @mcp.tool()
    async def list_members(
        guild_id: str,
        limit: int = 100,
    ) -> list[dict]:
        """List members of a guild.

        Args:
            guild_id: Target guild.
            limit: Max members to return (1-1000).
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        members = []
        async for m in guild.fetch_members(limit=limit):
            members.append(_member_to_dict(m))
        return members

    @mcp.tool()
    async def search_members(
        guild_id: str,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search guild members by name/nickname prefix.

        Args:
            guild_id: Target guild.
            query: Search query (name prefix).
            limit: Max results (1-1000).
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        members = await guild.query_members(query=query, limit=limit)
        return [_member_to_dict(m) for m in members]

    @mcp.tool()
    async def kick_member(
        guild_id: str,
        user_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Kick a member from a guild.

        Args:
            guild_id: Target guild.
            user_id: Member to kick.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        member = await guild.fetch_member(int(user_id))
        await member.kick(reason=reason)
        return f"Kicked user {user_id} from guild {guild_id}."

    @mcp.tool()
    async def ban_member(
        guild_id: str,
        user_id: str,
        *,
        delete_message_seconds: int = 0,
        reason: str | None = None,
    ) -> str:
        """Ban a user from a guild.

        Args:
            guild_id: Target guild.
            user_id: User to ban.
            delete_message_seconds: Seconds of message history to delete (0-604800).
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        await guild.ban(
            discord.Object(id=int(user_id)),
            delete_message_seconds=delete_message_seconds,
            reason=reason,
        )
        return f"Banned user {user_id} from guild {guild_id}."

    @mcp.tool()
    async def unban_member(
        guild_id: str,
        user_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Unban a user from a guild.

        Args:
            guild_id: Target guild.
            user_id: User to unban.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        await guild.unban(discord.Object(id=int(user_id)), reason=reason)
        return f"Unbanned user {user_id} from guild {guild_id}."

    @mcp.tool()
    async def timeout_member(
        guild_id: str,
        user_id: str,
        duration_seconds: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Timeout (mute) a member for a duration.

        Args:
            guild_id: Target guild.
            user_id: Member to timeout.
            duration_seconds: Timeout duration in seconds (max 2419200 = 28 days).
                Use 0 to remove an existing timeout.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        member = await guild.fetch_member(int(user_id))
        if duration_seconds == 0:
            await member.timeout(None, reason=reason)
            return f"Removed timeout for user {user_id} in guild {guild_id}."
        duration = datetime.timedelta(seconds=duration_seconds)
        await member.timeout(duration, reason=reason)
        return f"Timed out user {user_id} for {duration_seconds}s in guild {guild_id}."

    @mcp.tool()
    async def edit_member(
        guild_id: str,
        user_id: str,
        *,
        nickname: str | None = None,
        mute: bool | None = None,
        deafen: bool | None = None,
        voice_channel_id: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a guild member's attributes.

        Args:
            guild_id: Target guild.
            user_id: Member to edit.
            nickname: New nickname (None to reset).
            mute: Server mute in voice.
            deafen: Server deafen in voice.
            voice_channel_id: Move member to this voice channel.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        member = await guild.fetch_member(int(user_id))
        kwargs: dict = {}
        if nickname is not None:
            kwargs["nick"] = nickname
        if mute is not None:
            kwargs["mute"] = mute
        if deafen is not None:
            kwargs["deafen"] = deafen
        if voice_channel_id is not None:
            kwargs["voice_channel"] = guild.get_channel(int(voice_channel_id))
        if reason is not None:
            kwargs["reason"] = reason
        updated = await member.edit(**kwargs)
        return _member_to_dict(updated or member)

    @mcp.tool()
    async def add_member_roles(
        guild_id: str,
        user_id: str,
        role_ids: list[str],
        *,
        reason: str | None = None,
    ) -> str:
        """Add roles to a guild member.

        Args:
            guild_id: Target guild.
            user_id: Target member.
            role_ids: List of role IDs to add.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        member = await guild.fetch_member(int(user_id))
        roles = [require_role(guild, rid) for rid in role_ids]
        await member.add_roles(*roles, reason=reason)
        return f"Added {len(roles)} role(s) to user {user_id} in guild {guild_id}."

    @mcp.tool()
    async def remove_member_roles(
        guild_id: str,
        user_id: str,
        role_ids: list[str],
        *,
        reason: str | None = None,
    ) -> str:
        """Remove roles from a guild member.

        Args:
            guild_id: Target guild.
            user_id: Target member.
            role_ids: List of role IDs to remove.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        member = await guild.fetch_member(int(user_id))
        roles = [require_role(guild, rid) for rid in role_ids]
        await member.remove_roles(*roles, reason=reason)
        return f"Removed {len(roles)} role(s) from user {user_id} in guild {guild_id}."

    @mcp.tool()
    async def send_dm(
        user_id: str,
        content: str,
    ) -> dict:
        """Send a direct message to a user.

        Args:
            user_id: Target user.
            content: Message content.
        """
        bot = get_bot()
        user = bot.get_user(int(user_id))
        if user is None:
            user = await bot.fetch_user(int(user_id))
        message = await user.send(content)
        return {
            "id": str(message.id),
            "content": message.content,
            "channel_id": str(message.channel.id),
        }
