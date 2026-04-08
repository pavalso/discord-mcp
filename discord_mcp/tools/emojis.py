"""Emoji and sticker tools — list, create, delete."""

from __future__ import annotations

import aiohttp
import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def _emoji_to_dict(emoji: discord.Emoji) -> dict:
    return {
        "id": str(emoji.id),
        "name": emoji.name,
        "animated": emoji.animated,
        "available": emoji.available,
        "managed": emoji.managed,
        "url": str(emoji.url),
        "guild_id": str(emoji.guild_id),
    }


def _sticker_to_dict(sticker: discord.GuildSticker) -> dict:
    return {
        "id": str(sticker.id),
        "name": sticker.name,
        "description": sticker.description,
        "format": str(sticker.format),
        "available": sticker.available,
        "guild_id": str(sticker.guild_id),
        "url": str(sticker.url),
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_emojis(guild_id: str) -> list[dict]:
        """List all custom emojis in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of emojis with id, name, animated flag, and available roles.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        return [_emoji_to_dict(e) for e in guild.emojis]

    @mcp.tool()
    async def create_emoji(
        guild_id: str,
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
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                image_data = await resp.read()
        emoji = await guild.create_custom_emoji(name=name, image=image_data, reason=reason)
        return _emoji_to_dict(emoji)

    @mcp.tool()
    async def delete_emoji(
        guild_id: str,
        emoji_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a custom emoji from a guild.

        Args:
            guild_id: Guild containing the emoji.
            emoji_id: Emoji to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        await guild.delete_emoji(discord.Object(id=int(emoji_id)), reason=reason)
        return f"Deleted emoji {emoji_id} from guild {guild_id}."

    @mcp.tool()
    async def list_stickers(guild_id: str) -> list[dict]:
        """List all custom stickers in a guild.

        Args:
            guild_id: Target guild.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        return [_sticker_to_dict(s) for s in guild.stickers]

    @mcp.tool()
    async def delete_sticker(
        guild_id: str,
        sticker_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a custom sticker from a guild.

        Args:
            guild_id: Guild containing the sticker.
            sticker_id: Sticker to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        await guild.delete_sticker(discord.Object(id=int(sticker_id)), reason=reason)
        return f"Deleted sticker {sticker_id} from guild {guild_id}."
