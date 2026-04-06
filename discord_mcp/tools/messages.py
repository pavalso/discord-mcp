"""Message tools — send, edit, delete, reply, reactions, history, pins."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def _message_to_dict(message: discord.Message) -> dict:
    """Convert a Message to a serialisable dict."""
    return {
        "id": message.id,
        "content": message.content,
        "author_id": message.author.id,
        "author_name": message.author.name,
        "channel_id": message.channel.id,
        "created_at": str(message.created_at),
        "edited_at": str(message.edited_at) if message.edited_at else None,
        "pinned": message.pinned,
        "tts": message.tts,
        "type": str(message.type),
        "jump_url": message.jump_url,
        "attachments": [{"id": a.id, "filename": a.filename, "url": a.url} for a in message.attachments],
        "embeds": [e.to_dict() for e in message.embeds],
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def send_message(
        channel_id: int,
        content: str,
        *,
        tts: bool = False,
        reply_to_message_id: int | None = None,
    ) -> dict:
        """Send a message to a Discord channel.

        Args:
            channel_id: Target channel ID.
            content: Message text content.
            tts: Whether this is a text-to-speech message.
            reply_to_message_id: Message ID to reply to, if any.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        kwargs: dict = {"content": content, "tts": tts}
        if reply_to_message_id is not None:
            kwargs["reference"] = discord.MessageReference(
                message_id=reply_to_message_id, channel_id=channel_id
            )

        message = await channel.send(**kwargs)
        return _message_to_dict(message)

    @mcp.tool()
    async def edit_message(
        channel_id: int,
        message_id: int,
        content: str,
    ) -> dict:
        """Edit an existing message sent by the bot.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to edit.
            content: New message content.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        edited = await message.edit(content=content)
        return _message_to_dict(edited or message)

    @mcp.tool()
    async def delete_message(
        channel_id: int,
        message_id: int,
    ) -> str:
        """Delete a message.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to delete.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        await message.delete()
        return f"Deleted message {message_id} in channel {channel_id}."

    @mcp.tool()
    async def get_message(
        channel_id: int,
        message_id: int,
    ) -> dict:
        """Fetch a single message by ID.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to fetch.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        return _message_to_dict(message)

    @mcp.tool()
    async def get_message_history(
        channel_id: int,
        limit: int = 50,
        before_message_id: int | None = None,
        after_message_id: int | None = None,
    ) -> list[dict]:
        """Retrieve recent message history from a channel.

        Args:
            channel_id: Target channel ID.
            limit: Max number of messages (1-100).
            before_message_id: Get messages before this message ID.
            after_message_id: Get messages after this message ID.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        kwargs: dict = {"limit": limit}
        if before_message_id is not None:
            kwargs["before"] = discord.Object(id=before_message_id)
        if after_message_id is not None:
            kwargs["after"] = discord.Object(id=after_message_id)

        messages: list[dict] = []
        async for msg in channel.history(**kwargs):
            messages.append(_message_to_dict(msg))
        return messages

    @mcp.tool()
    async def pin_message(
        channel_id: int,
        message_id: int,
    ) -> str:
        """Pin a message in a channel.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to pin.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        await message.pin()
        return f"Pinned message {message_id} in channel {channel_id}."

    @mcp.tool()
    async def unpin_message(
        channel_id: int,
        message_id: int,
    ) -> str:
        """Unpin a message in a channel.

        Args:
            channel_id: Channel containing the message.
            message_id: The message to unpin.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        await message.unpin()
        return f"Unpinned message {message_id} in channel {channel_id}."

    @mcp.tool()
    async def get_pinned_messages(channel_id: int) -> list[dict]:
        """Get all pinned messages in a channel.

        Args:
            channel_id: Target channel ID.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        pinned: list[dict] = []
        async for msg in channel.pins():
            pinned.append(_message_to_dict(msg))
        return pinned

    @mcp.tool()
    async def add_reaction(
        channel_id: int,
        message_id: int,
        emoji: str,
    ) -> str:
        """Add a reaction to a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Target message.
            emoji: Unicode emoji or custom emoji string (e.g. "thumbsup" or "emoji_name:emoji_id").
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        await message.add_reaction(emoji)
        return f"Added reaction {emoji} to message {message_id}."

    @mcp.tool()
    async def remove_reaction(
        channel_id: int,
        message_id: int,
        emoji: str,
        user_id: int | None = None,
    ) -> str:
        """Remove a reaction from a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Target message.
            emoji: The emoji to remove.
            user_id: User whose reaction to remove. Omit for the bot's own reaction.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        if user_id is not None:
            user = discord.Object(id=user_id)
            await message.remove_reaction(emoji, user)
        else:
            await message.remove_reaction(emoji, bot.user)
        return f"Removed reaction {emoji} from message {message_id}."

    @mcp.tool()
    async def clear_reactions(
        channel_id: int,
        message_id: int,
        emoji: str | None = None,
    ) -> str:
        """Clear reactions from a message.

        Args:
            channel_id: Channel containing the message.
            message_id: Target message.
            emoji: Specific emoji to clear. Omit to clear all reactions.
        """
        bot = get_bot()
        channel = bot.get_channel(channel_id)
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        message = await channel.fetch_message(message_id)
        if emoji is not None:
            await message.clear_reaction(emoji)
            return f"Cleared reaction {emoji} from message {message_id}."
        else:
            await message.clear_reactions()
            return f"Cleared all reactions from message {message_id}."
