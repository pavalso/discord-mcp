"""Role tools — create, edit, delete, list roles."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_roles(guild_id: int) -> list[dict]:
        """List all roles in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of roles with id, name, color, position, permissions, etc.
        """
        raise NotImplementedError

    @mcp.tool()
    async def get_role(
        guild_id: int,
        role_id: int,
    ) -> dict:
        """Get detailed information about a role.

        Args:
            guild_id: Guild containing the role.
            role_id: Target role ID.
        """
        raise NotImplementedError

    @mcp.tool()
    async def create_role(
        guild_id: int,
        name: str,
        *,
        color: int | None = None,
        hoist: bool = False,
        mentionable: bool = False,
        permissions: list[str] | None = None,
        reason: str | None = None,
    ) -> dict:
        """Create a new role in a guild.

        Args:
            guild_id: Target guild.
            name: Role name.
            color: Role color as integer (e.g. 0xFF0000 for red).
            hoist: Whether to display the role separately in the member sidebar.
            mentionable: Whether the role can be mentioned.
            permissions: List of permission names to grant (e.g. ["send_messages", "manage_channels"]).
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def edit_role(
        guild_id: int,
        role_id: int,
        *,
        name: str | None = None,
        color: int | None = None,
        hoist: bool | None = None,
        mentionable: bool | None = None,
        permissions: list[str] | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit an existing role.

        Args:
            guild_id: Guild containing the role.
            role_id: Role to edit.
            name: New name.
            color: New color as integer.
            hoist: Whether to hoist.
            mentionable: Whether mentionable.
            permissions: New permission list (replaces current permissions).
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def delete_role(
        guild_id: int,
        role_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a role from a guild.

        Args:
            guild_id: Guild containing the role.
            role_id: Role to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError
