"""Guild tools — list, info, settings."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_guilds() -> list[dict]:
        """List all guilds the bot is a member of.

        Returns:
            List of guilds with id, name, member_count, and owner_id.
        """
        raise NotImplementedError

    @mcp.tool()
    async def get_guild(guild_id: int) -> dict:
        """Get detailed information about a guild.

        Args:
            guild_id: Target guild ID.

        Returns:
            Guild details including name, description, owner, member count,
            channel count, role count, premium tier, features, etc.
        """
        raise NotImplementedError

    @mcp.tool()
    async def edit_guild(
        guild_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        verification_level: str | None = None,
        default_notifications: str | None = None,
        explicit_content_filter: str | None = None,
        afk_channel_id: int | None = None,
        afk_timeout: int | None = None,
        system_channel_id: int | None = None,
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
        raise NotImplementedError
