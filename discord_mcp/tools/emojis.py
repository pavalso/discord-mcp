"""Emoji and sticker tools — list, create, edit, delete."""

from __future__ import annotations

import io

import aiohttp
import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot
from discord_mcp.tools._common import require_guild, require_role


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
        guild = require_guild(bot, guild_id)
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
        guild = require_guild(bot, guild_id)
        async with aiohttp.ClientSession() as session, session.get(image_url) as resp:
            image_data = await resp.read()
        emoji = await guild.create_custom_emoji(name=name, image=image_data, reason=reason)
        return _emoji_to_dict(emoji)

    @mcp.tool()
    async def edit_emoji(
        guild_id: str,
        emoji_id: str,
        *,
        name: str | None = None,
        role_ids: list[str] | None = None,
        reason: str | None = None,
    ) -> dict:
        """Rename a custom emoji, or restrict which roles may use it.

        Args:
            guild_id: Guild containing the emoji.
            emoji_id: Emoji to edit.
            name: New emoji name. Omit to leave unchanged.
            role_ids: Roles allowed to use the emoji. Pass an empty list to
                clear the restriction and let everyone use it. Omit to leave
                the current restriction unchanged.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        emoji = await guild.fetch_emoji(int(emoji_id))

        kwargs: dict = {"reason": reason}
        if name is not None:
            kwargs["name"] = name
        if role_ids is not None:
            kwargs["roles"] = [require_role(guild, rid) for rid in role_ids]

        updated = await emoji.edit(**kwargs)
        return _emoji_to_dict(updated or emoji)

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
        guild = require_guild(bot, guild_id)
        await guild.delete_emoji(discord.Object(id=int(emoji_id)), reason=reason)
        return f"Deleted emoji {emoji_id} from guild {guild_id}."

    @mcp.tool()
    async def list_stickers(guild_id: str) -> list[dict]:
        """List all custom stickers in a guild.

        Args:
            guild_id: Target guild.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        return [_sticker_to_dict(s) for s in guild.stickers]

    @mcp.tool()
    async def create_sticker(
        guild_id: str,
        name: str,
        description: str,
        emoji: str,
        image_url: str,
        *,
        reason: str | None = None,
    ) -> dict:
        """Create a custom sticker in a guild.

        Args:
            guild_id: Target guild.
            name: Sticker name.
            description: Sticker description shown in the picker.
            emoji: Unicode emoji that acts as the sticker's tag, e.g. "😀".
            image_url: URL of the image to use (PNG or APNG, max 512KB, 320x320).
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        async with aiohttp.ClientSession() as session, session.get(image_url) as resp:
            image_data = await resp.read()

        sticker = await guild.create_sticker(
            name=name,
            description=description,
            emoji=emoji,
            file=discord.File(io.BytesIO(image_data), filename=f"{name}.png"),
            reason=reason,
        )
        return _sticker_to_dict(sticker)

    @mcp.tool()
    async def edit_sticker(
        guild_id: str,
        sticker_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        emoji: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a custom sticker's name, description, or emoji tag.

        The sticker image itself cannot be changed; delete and recreate for that.

        Args:
            guild_id: Guild containing the sticker.
            sticker_id: Sticker to edit.
            name: New sticker name. Omit to leave unchanged.
            description: New description. Omit to leave unchanged.
            emoji: New unicode emoji tag. Omit to leave unchanged.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = require_guild(bot, guild_id)
        sticker = await guild.fetch_sticker(int(sticker_id))

        kwargs: dict = {"reason": reason}
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if emoji is not None:
            kwargs["emoji"] = emoji

        updated = await sticker.edit(**kwargs)
        return _sticker_to_dict(updated or sticker)

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
        guild = require_guild(bot, guild_id)
        await guild.delete_sticker(discord.Object(id=int(sticker_id)), reason=reason)
        return f"Deleted sticker {sticker_id} from guild {guild_id}."
