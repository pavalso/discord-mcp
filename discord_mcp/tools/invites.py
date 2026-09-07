"""Invite tools — create, list, delete invites."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot
from discord_mcp.tools._common import require_guild, require_guild_channel


def _invite_to_dict(invite: discord.Invite) -> dict:
    return {
        "code": invite.code,
        "url": invite.url,
        "channel_id": str(invite.channel.id) if invite.channel is not None else None,
        "inviter_id": str(invite.inviter.id) if invite.inviter is not None else None,
        "max_age": invite.max_age,
        "max_uses": invite.max_uses,
        "uses": invite.uses,
        "temporary": invite.temporary,
        "created_at": str(invite.created_at) if invite.created_at else None,
        "expires_at": str(invite.expires_at) if invite.expires_at else None,
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_invites(guild_id: str) -> list[dict]:
        """List all active invites in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of invites with code, channel, inviter, uses, max_uses, etc.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        invites = await guild.invites()
        return [_invite_to_dict(i) for i in invites]

    @mcp.tool()
    async def create_invite(
        channel_id: str,
        *,
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = True,
        reason: str | None = None,
    ) -> dict:
        """Create an invite for a channel.

        Args:
            channel_id: Channel to create invite for.
            max_age: Invite lifetime in seconds (0 = forever, default 86400 = 24h).
            max_uses: Max number of uses (0 = unlimited).
            temporary: Whether membership is temporary.
            unique: Whether to create a new unique invite or reuse existing.
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = require_guild_channel(bot, channel_id)
        invite = await channel.create_invite(
            max_age=max_age,
            max_uses=max_uses,
            temporary=temporary,
            unique=unique,
            reason=reason,
        )
        return _invite_to_dict(invite)

    @mcp.tool()
    async def delete_invite(
        invite_code: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete/revoke an invite.

        Args:
            invite_code: Invite code or full URL.
            reason: Audit log reason.
        """
        bot = get_bot()
        invite = await bot.fetch_invite(invite_code)
        await invite.delete(reason=reason)
        return f"Deleted invite {invite_code}."

    @mcp.tool()
    async def get_invite(invite_code: str) -> dict:
        """Get information about an invite.

        Args:
            invite_code: Invite code or full URL.
        """
        bot = get_bot()
        invite = await bot.fetch_invite(invite_code, with_counts=True, with_expiration=True)
        return _invite_to_dict(invite)
