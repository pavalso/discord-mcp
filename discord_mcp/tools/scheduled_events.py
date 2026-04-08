"""Scheduled event tools — create, list, edit, delete guild events."""

from __future__ import annotations

from datetime import datetime, timezone

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot

ENTITY_TYPE_MAP = {
    "stage_instance": discord.EntityType.stage_instance,
    "voice": discord.EntityType.voice,
    "external": discord.EntityType.external,
}

EVENT_STATUS_MAP = {
    "scheduled": discord.EventStatus.scheduled,
    "active": discord.EventStatus.active,
    "completed": discord.EventStatus.completed,
    "cancelled": discord.EventStatus.cancelled,
}


def _parse_iso(iso_string: str) -> datetime:
    dt = datetime.fromisoformat(iso_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _event_to_dict(event: discord.ScheduledEvent) -> dict:
    return {
        "id": str(event.id),
        "name": event.name,
        "description": event.description,
        "entity_type": str(event.entity_type),
        "start_time": str(event.start_time),
        "end_time": str(event.end_time) if event.end_time else None,
        "status": str(event.status),
        "location": event.location,
        "channel_id": str(event.channel.id) if getattr(event, "channel", None) else None,
        "creator_id": str(event.creator_id),
        "user_count": event.user_count,
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_scheduled_events(guild_id: str) -> list[dict]:
        """List all scheduled events in a guild.

        Args:
            guild_id: Target guild.

        Returns:
            List of events with id, name, description, start/end times, status, etc.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        events = await guild.fetch_scheduled_events(with_counts=True)
        return [_event_to_dict(e) for e in events]

    @mcp.tool()
    async def create_scheduled_event(
        guild_id: str,
        name: str,
        start_time: str,
        entity_type: str,
        *,
        description: str | None = None,
        end_time: str | None = None,
        channel_id: str | None = None,
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
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        kwargs: dict = {
            "name": name,
            "start_time": _parse_iso(start_time),
            "entity_type": ENTITY_TYPE_MAP[entity_type],
            "reason": reason,
        }
        if description is not None:
            kwargs["description"] = description
        if end_time is not None:
            kwargs["end_time"] = _parse_iso(end_time)
        if channel_id is not None:
            kwargs["channel"] = discord.Object(id=int(channel_id))
        if location is not None:
            kwargs["location"] = location
        event = await guild.create_scheduled_event(**kwargs)
        return _event_to_dict(event)

    @mcp.tool()
    async def edit_scheduled_event(
        guild_id: str,
        event_id: str,
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
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        event = guild.get_scheduled_event(int(event_id))
        if event is None:
            event = await guild.fetch_scheduled_event(int(event_id))
        kwargs: dict = {}
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if start_time is not None:
            kwargs["start_time"] = _parse_iso(start_time)
        if end_time is not None:
            kwargs["end_time"] = _parse_iso(end_time)
        if status is not None:
            kwargs["status"] = EVENT_STATUS_MAP[status]
        if reason is not None:
            kwargs["reason"] = reason
        updated = await event.edit(**kwargs)
        return _event_to_dict(updated or event)

    @mcp.tool()
    async def delete_scheduled_event(
        guild_id: str,
        event_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a scheduled event.

        Args:
            guild_id: Guild containing the event.
            event_id: Event to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")
        event = guild.get_scheduled_event(int(event_id))
        if event is None:
            event = await guild.fetch_scheduled_event(int(event_id))
        await event.delete(reason=reason)
        return f"Deleted scheduled event {event.name} ({event_id})."
