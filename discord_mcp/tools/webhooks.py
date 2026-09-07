"""Webhook tools — create, list, send, edit, delete."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def _webhook_to_dict(webhook: discord.Webhook) -> dict:
    return {
        "id": str(webhook.id),
        "name": webhook.name,
        "type": str(webhook.type),
        "guild_id": str(webhook.guild_id),
        "channel_id": str(webhook.channel_id),
        "url": webhook.url,
        "created_at": str(webhook.created_at),
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_webhooks(
        channel_id: str | None = None,
        guild_id: str | None = None,
    ) -> list[dict]:
        """List webhooks for a channel or entire guild.

        Args:
            channel_id: List webhooks for this channel.
            guild_id: List all webhooks in this guild.
            At least one must be provided; channel_id takes priority.
        """
        bot = get_bot()
        if channel_id is not None:
            channel = bot.get_channel(int(channel_id))
            if channel is None:
                raise ValueError(f"Channel {channel_id} not found (not in cache).")
            webhooks = await channel.webhooks()
        elif guild_id is not None:
            guild = bot.get_guild(int(guild_id))
            if guild is None:
                raise ValueError(f"Guild {guild_id} not found (not in cache).")
            webhooks = await guild.webhooks()
        else:
            raise ValueError("At least one of channel_id or guild_id must be provided.")
        return [_webhook_to_dict(w) for w in webhooks]

    @mcp.tool()
    async def create_webhook(
        channel_id: str,
        name: str,
        *,
        reason: str | None = None,
    ) -> dict:
        """Create a webhook for a channel.

        Args:
            channel_id: Target channel.
            name: Webhook name.
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")
        webhook = await channel.create_webhook(name=name, reason=reason)
        return _webhook_to_dict(webhook)

    @mcp.tool()
    async def send_webhook_message(
        webhook_id: str,
        content: str,
        *,
        username: str | None = None,
        avatar_url: str | None = None,
        thread_id: str | None = None,
    ) -> dict:
        """Send a message via a webhook.

        Args:
            webhook_id: Webhook to send through.
            content: Message content.
            username: Override the webhook's display name.
            avatar_url: Override the webhook's avatar.
            thread_id: Send to a specific thread.
        """
        bot = get_bot()
        webhook = await bot.fetch_webhook(int(webhook_id))
        kwargs: dict = {"wait": True}
        if username is not None:
            kwargs["username"] = username
        if avatar_url is not None:
            kwargs["avatar_url"] = avatar_url
        if thread_id is not None:
            kwargs["thread"] = discord.Object(id=int(thread_id))
        message = await webhook.send(content, **kwargs)
        return {
            "id": str(message.id),
            "content": message.content,
            "channel_id": str(message.channel.id),
        }

    @mcp.tool()
    async def edit_webhook(
        webhook_id: str,
        *,
        name: str | None = None,
        channel_id: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a webhook.

        Args:
            webhook_id: Webhook to edit.
            name: New name.
            channel_id: Move webhook to a different channel.
            reason: Audit log reason.
        """
        bot = get_bot()
        webhook = await bot.fetch_webhook(int(webhook_id))
        kwargs: dict = {}
        if name is not None:
            kwargs["name"] = name
        if channel_id is not None:
            kwargs["channel"] = discord.Object(id=int(channel_id))
        if reason is not None:
            kwargs["reason"] = reason
        updated = await webhook.edit(**kwargs)
        return _webhook_to_dict(updated)

    @mcp.tool()
    async def delete_webhook(
        webhook_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a webhook.

        Args:
            webhook_id: Webhook to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        webhook = await bot.fetch_webhook(int(webhook_id))
        await webhook.delete(reason=reason)
        return f"Deleted webhook {webhook.name} ({webhook_id})."
