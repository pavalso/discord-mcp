"""Webhook tools — create, list, send, edit, delete."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_webhooks(
        channel_id: int | None = None,
        guild_id: int | None = None,
    ) -> list[dict]:
        """List webhooks for a channel or entire guild.

        Args:
            channel_id: List webhooks for this channel.
            guild_id: List all webhooks in this guild.
            At least one must be provided; channel_id takes priority.
        """
        raise NotImplementedError

    @mcp.tool()
    async def create_webhook(
        channel_id: int,
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
        raise NotImplementedError

    @mcp.tool()
    async def send_webhook_message(
        webhook_id: int,
        content: str,
        *,
        username: str | None = None,
        avatar_url: str | None = None,
        thread_id: int | None = None,
    ) -> dict:
        """Send a message via a webhook.

        Args:
            webhook_id: Webhook to send through.
            content: Message content.
            username: Override the webhook's display name.
            avatar_url: Override the webhook's avatar.
            thread_id: Send to a specific thread.
        """
        raise NotImplementedError

    @mcp.tool()
    async def edit_webhook(
        webhook_id: int,
        *,
        name: str | None = None,
        channel_id: int | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a webhook.

        Args:
            webhook_id: Webhook to edit.
            name: New name.
            channel_id: Move webhook to a different channel.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def delete_webhook(
        webhook_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a webhook.

        Args:
            webhook_id: Webhook to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError
