"""Invite tools — create, list, delete invites."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_invites(guild_id: int) -> list[dict]:
        """List all active invites in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of invites with code, channel, inviter, uses, max_uses, etc.
        """
        raise NotImplementedError

    @mcp.tool()
    async def create_invite(
        channel_id: int,
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
        raise NotImplementedError

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
        raise NotImplementedError

    @mcp.tool()
    async def get_invite(invite_code: str) -> dict:
        """Get information about an invite.

        Args:
            invite_code: Invite code or full URL.
        """
        raise NotImplementedError
