"""Member tools — fetch, kick, ban, timeout, role assignment, DM."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_member(
        guild_id: int,
        user_id: int,
    ) -> dict:
        """Fetch detailed information about a guild member.

        Args:
            guild_id: Guild the member belongs to.
            user_id: The member's user ID.

        Returns:
            Member details including name, nickname, roles, join date, etc.
        """
        raise NotImplementedError

    @mcp.tool()
    async def list_members(
        guild_id: int,
        limit: int = 100,
    ) -> list[dict]:
        """List members of a guild.

        Args:
            guild_id: Target guild.
            limit: Max members to return (1-1000).
        """
        raise NotImplementedError

    @mcp.tool()
    async def search_members(
        guild_id: int,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search guild members by name/nickname prefix.

        Args:
            guild_id: Target guild.
            query: Search query (name prefix).
            limit: Max results (1-1000).
        """
        raise NotImplementedError

    @mcp.tool()
    async def kick_member(
        guild_id: int,
        user_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Kick a member from a guild.

        Args:
            guild_id: Target guild.
            user_id: Member to kick.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def ban_member(
        guild_id: int,
        user_id: int,
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
        raise NotImplementedError

    @mcp.tool()
    async def unban_member(
        guild_id: int,
        user_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Unban a user from a guild.

        Args:
            guild_id: Target guild.
            user_id: User to unban.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def timeout_member(
        guild_id: int,
        user_id: int,
        duration_seconds: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Timeout (mute) a member for a duration.

        Args:
            guild_id: Target guild.
            user_id: Member to timeout.
            duration_seconds: Timeout duration in seconds (max 2419200 = 28 days). Use 0 to remove timeout.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def edit_member(
        guild_id: int,
        user_id: int,
        *,
        nickname: str | None = None,
        mute: bool | None = None,
        deafen: bool | None = None,
        voice_channel_id: int | None = None,
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
        raise NotImplementedError

    @mcp.tool()
    async def add_member_roles(
        guild_id: int,
        user_id: int,
        role_ids: list[int],
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
        raise NotImplementedError

    @mcp.tool()
    async def remove_member_roles(
        guild_id: int,
        user_id: int,
        role_ids: list[int],
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
        raise NotImplementedError

    @mcp.tool()
    async def send_dm(
        user_id: int,
        content: str,
    ) -> dict:
        """Send a direct message to a user.

        Args:
            user_id: Target user.
            content: Message content.
        """
        raise NotImplementedError
