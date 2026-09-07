"""Role tools — create, edit, delete, list roles."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot
from discord_mcp.tools._common import require_guild


def _role_to_dict(role: discord.Role) -> dict:
    """Convert a role to a serialisable dict."""
    return {
        "id": str(role.id),
        "name": role.name,
        "color": role.color.value,
        "hoist": role.hoist,
        "position": role.position,
        "managed": role.managed,
        "mentionable": role.mentionable,
        "permissions": [perm for perm, value in role.permissions if value],
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_roles(guild_id: str) -> list[dict]:
        """List all roles in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of roles with id, name, color, position, permissions, etc.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        return [_role_to_dict(r) for r in guild.roles]

    @mcp.tool()
    async def get_role(
        guild_id: str,
        role_id: str,
    ) -> dict:
        """Get detailed information about a role.

        Args:
            guild_id: Guild containing the role.
            role_id: Target role ID.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        role = guild.get_role(int(role_id))
        if role is None:
            raise ValueError(f"Role {role_id} not found in guild {guild_id}.")
        return _role_to_dict(role)

    @mcp.tool()
    async def create_role(
        guild_id: str,
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
            permissions: List of permission names to grant
                (e.g. ["send_messages", "manage_channels"]).
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        kwargs: dict = {
            "name": name,
            "hoist": hoist,
            "mentionable": mentionable,
            "reason": reason,
        }
        if color is not None:
            kwargs["color"] = discord.Colour(color)
        if permissions is not None:
            kwargs["permissions"] = discord.Permissions(**{p: True for p in permissions})
        role = await guild.create_role(**kwargs)
        return _role_to_dict(role)

    @mcp.tool()
    async def edit_role(
        guild_id: str,
        role_id: str,
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
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        role = guild.get_role(int(role_id))
        if role is None:
            raise ValueError(f"Role {role_id} not found in guild {guild_id}.")
        kwargs: dict = {}
        if name is not None:
            kwargs["name"] = name
        if color is not None:
            kwargs["color"] = discord.Colour(color)
        if hoist is not None:
            kwargs["hoist"] = hoist
        if mentionable is not None:
            kwargs["mentionable"] = mentionable
        if permissions is not None:
            kwargs["permissions"] = discord.Permissions(**{p: True for p in permissions})
        if reason is not None:
            kwargs["reason"] = reason
        updated = await role.edit(**kwargs)
        return _role_to_dict(updated or role)

    @mcp.tool()
    async def delete_role(
        guild_id: str,
        role_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a role from a guild.

        Args:
            guild_id: Guild containing the role.
            role_id: Role to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        role = guild.get_role(int(role_id))
        if role is None:
            raise ValueError(f"Role {role_id} not found in guild {guild_id}.")
        await role.delete(reason=reason)
        return f"Deleted role {role.name} ({role_id})."
