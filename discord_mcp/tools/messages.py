"""Message tools — send, edit, delete, reply, reactions, history, pins."""

from __future__ import annotations

from typing import cast

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot
from discord_mcp.tools._common import require_messageable


def _message_to_dict(message: discord.Message) -> dict:
    """Convert a Message to a serialisable dict."""
    return {
        "id": str(message.id),
        "content": message.content,
        "author_id": str(message.author.id),
        "author_name": message.author.name,
        "channel_id": str(message.channel.id),
        "created_at": str(message.created_at),
        "edited_at": str(message.edited_at) if message.edited_at else None,
        "pinned": message.pinned,
        "tts": message.tts,
        "type": str(message.type),
        "jump_url": message.jump_url,
        "attachments": [
            {"id": str(a.id), "filename": a.filename, "url": a.url} for a in message.attachments
        ],
        "embeds": [e.to_dict() for e in message.embeds],
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def send_message(
        channel_id: str,
        content: str,
        *,
        tts: bool = False,
        reply_to_message_id: str | None = None,
    ) -> dict:
        """Send a message to a Discord channel.

        Args:
            channel_id: Target channel ID.
            content: Message text content.
            tts: Whether this is a text-to-speech message.
            reply_to_message_id: Message ID to reply to, if any.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        kwargs: dict = {"content": content, "tts": tts}
        if reply_to_message_id is not None:
            kwargs["reference"] = discord.MessageReference(
                message_id=int(reply_to_message_id), channel_id=int(channel_id)
            )

        message = await channel.send(**kwargs)
        return _message_to_dict(message)

    @mcp.tool()
    async def send_embed(
        channel_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        color: int | None = None,
        url: str | None = None,
        footer_text: str | None = None,
        footer_icon_url: str | None = None,
        image_url: str | None = None,
        thumbnail_url: str | None = None,
        author_name: str | None = None,
        author_url: str | None = None,
        author_icon_url: str | None = None,
        fields: list[dict] | None = None,
        content: str | None = None,
    ) -> dict:
        """Send a rich embed message to a Discord channel.

        Args:
            channel_id: Target channel ID.
            title: Embed title.
            description: Embed description text.
            color: Embed color as an integer (e.g. 0xFF5733).
            url: URL the title links to.
            footer_text: Footer text.
            footer_icon_url: Footer icon URL.
            image_url: Large image URL.
            thumbnail_url: Thumbnail image URL.
            author_name: Author name shown at the top.
            author_url: URL the author name links to.
            author_icon_url: Author icon URL.
            fields: List of field dicts with keys "name", "value", and optional "inline" (bool).
            content: Optional text content sent alongside the embed.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        embed = discord.Embed()
        if title is not None:
            embed.title = title
        if description is not None:
            embed.description = description
        if color is not None:
            embed.color = discord.Color(color)
        if url is not None:
            embed.url = url

        if footer_text is not None:
            footer_kwargs: dict = {"text": footer_text}
            if footer_icon_url is not None:
                footer_kwargs["icon_url"] = footer_icon_url
            embed.set_footer(**footer_kwargs)
        if image_url is not None:
            embed.set_image(url=image_url)
        if thumbnail_url is not None:
            embed.set_thumbnail(url=thumbnail_url)
        if author_name is not None:
            kwargs: dict = {"name": author_name}
            if author_url is not None:
                kwargs["url"] = author_url
            if author_icon_url is not None:
                kwargs["icon_url"] = author_icon_url
            embed.set_author(**kwargs)

        if fields is not None:
            for field in fields:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", False),
                )

        message = await channel.send(content=content, embed=embed)
        return _message_to_dict(message)

    @mcp.tool()
    async def edit_message(
        channel_id: str,
        message_id: str,
        content: str,
    ) -> dict:
        """Edit an existing message sent by the bot.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to edit.
            content: New message content.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        edited = await message.edit(content=content)
        return _message_to_dict(edited or message)

    @mcp.tool()
    async def delete_message(
        channel_id: str,
        message_id: str,
    ) -> str:
        """Delete a message.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to delete.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        await message.delete()
        return f"Deleted message {message_id} in channel {channel_id}."

    @mcp.tool()
    async def get_message(
        channel_id: str,
        message_id: str,
    ) -> dict:
        """Fetch a single message by ID.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to fetch.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        return _message_to_dict(message)

    @mcp.tool()
    async def get_message_history(
        channel_id: str,
        limit: int = 50,
        before_message_id: str | None = None,
        after_message_id: str | None = None,
    ) -> list[dict]:
        """Retrieve recent message history from a channel.

        Args:
            channel_id: Target channel ID.
            limit: Max number of messages (1-100).
            before_message_id: Get messages before this message ID.
            after_message_id: Get messages after this message ID.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        kwargs: dict = {"limit": limit}
        if before_message_id is not None:
            kwargs["before"] = discord.Object(id=int(before_message_id))
        if after_message_id is not None:
            kwargs["after"] = discord.Object(id=int(after_message_id))

        messages: list[dict] = []
        async for msg in channel.history(**kwargs):
            messages.append(_message_to_dict(msg))
        return messages

    @mcp.tool()
    async def pin_message(
        channel_id: str,
        message_id: str,
    ) -> str:
        """Pin a message in a channel.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to pin.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        await message.pin()
        return f"Pinned message {message_id} in channel {channel_id}."

    @mcp.tool()
    async def unpin_message(
        channel_id: str,
        message_id: str,
    ) -> str:
        """Unpin a message in a channel.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to unpin.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        await message.unpin()
        return f"Unpinned message {message_id} in channel {channel_id}."

    @mcp.tool()
    async def get_pinned_messages(channel_id: str) -> list[dict]:
        """Get all pinned messages in a channel.

        Args:
            channel_id: Target channel ID.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        pinned: list[dict] = []
        async for msg in channel.pins():
            pinned.append(_message_to_dict(msg))
        return pinned

    @mcp.tool()
    async def add_reaction(
        channel_id: str,
        message_id: str,
        emoji: str,
    ) -> str:
        """Add a reaction to a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Target message.
            emoji: Unicode emoji or custom emoji string (e.g. "thumbsup" or "emoji_name:emoji_id").
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        await message.add_reaction(emoji)
        return f"Added reaction {emoji} to message {message_id}."

    @mcp.tool()
    async def remove_reaction(
        channel_id: str,
        message_id: str,
        emoji: str,
        user_id: str | None = None,
    ) -> str:
        """Remove a reaction from a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Target message.
            emoji: The emoji to remove.
            user_id: User whose reaction to remove. Omit for the bot's own reaction.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        if user_id is not None:
            user = discord.Object(id=int(user_id))
            await message.remove_reaction(emoji, user)
        else:
            await message.remove_reaction(emoji, cast(discord.ClientUser, bot.user))
        return f"Removed reaction {emoji} from message {message_id}."

    @mcp.tool()
    async def clear_reactions(
        channel_id: str,
        message_id: str,
        emoji: str | None = None,
    ) -> str:
        """Clear reactions from a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Target message.
            emoji: Specific emoji to clear. Omit to clear all reactions.
        """
        bot = get_bot()
        channel = require_messageable(bot, channel_id)

        message = await channel.fetch_message(int(message_id))
        if emoji is not None:
            await message.clear_reaction(emoji)
            return f"Cleared reaction {emoji} from message {message_id}."
        else:
            await message.clear_reactions()
            return f"Cleared all reactions from message {message_id}."
