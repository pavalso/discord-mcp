"""Emoji and sticker tools — list, create, delete."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_emojis(guild_id: int) -> list[dict]:
        """List all custom emojis in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of emojis with id, name, animated flag, and available roles.
        """
        raise NotImplementedError

    @mcp.tool()
    async def create_emoji(
        guild_id: int,
        name: str,
        image_url: str,
        *,
        reason: str | None = None,
    ) -> dict:
        """Create a custom emoji in a guild.

        Args:
            guild_id: Target guild.
            name: Emoji name.
            image_url: URL of the image to use (PNG/GIF, max 256KB).
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def delete_emoji(
        guild_id: int,
        emoji_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a custom emoji from a guild.

        Args:
            guild_id: Guild containing the emoji.
            emoji_id: Emoji to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def list_stickers(guild_id: int) -> list[dict]:
        """List all custom stickers in a guild.

        Args:
            guild_id: Target guild.
        """
        raise NotImplementedError

    @mcp.tool()
    async def delete_sticker(
        guild_id: int,
        sticker_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a custom sticker from a guild.

        Args:
            guild_id: Guild containing the sticker.
            sticker_id: Sticker to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError
