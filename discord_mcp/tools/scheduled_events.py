"""Scheduled event tools — create, list, edit, delete guild events."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_scheduled_events(guild_id: int) -> list[dict]:
        """List all scheduled events in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of events with id, name, description, start/end times, status, etc.
        """
        raise NotImplementedError

    @mcp.tool()
    async def create_scheduled_event(
        guild_id: int,
        name: str,
        start_time: str,
        entity_type: str,
        *,
        description: str | None = None,
        end_time: str | None = None,
        channel_id: int | None = None,
        location: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """Create a scheduled event in a guild.

        Args:
            guild_id: Target guild.
            name: Event name.
            start_time: ISO 8601 datetime string (e.g. "2025-06-01T18:00:00Z").
            entity_type: "stage_instance", "voice", or "external".
            description: Event description.
            end_time: ISO 8601 end datetime (required for external events).
            channel_id: Voice/stage channel ID (required for voice/stage events).
            location: Location string (required for external events).
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def edit_scheduled_event(
        guild_id: int,
        event_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        status: str | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a scheduled event.

        Args:
            guild_id: Guild containing the event.
            event_id: Event to edit.
            name: New name.
            description: New description.
            start_time: New start time (ISO 8601).
            end_time: New end time (ISO 8601).
            status: "scheduled", "active", "completed", or "cancelled".
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def delete_scheduled_event(
        guild_id: int,
        event_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a scheduled event.

        Args:
            guild_id: Guild containing the event.
            event_id: Event to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError
