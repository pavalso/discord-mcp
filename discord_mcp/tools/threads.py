"""Thread tools — create, edit, archive, join, manage members."""

from __future__ import annotations

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def _thread_to_dict(thread: discord.Thread) -> dict:
    """Convert a thread to a serialisable dict."""
    return {
        "id": str(thread.id),
        "name": thread.name,
        "parent_id": str(thread.parent_id),
        "owner_id": str(thread.owner_id),
        "archived": thread.archived,
        "locked": thread.locked,
        "auto_archive_duration": thread.auto_archive_duration,
        "slowmode_delay": thread.slowmode_delay,
        "message_count": thread.message_count,
        "member_count": thread.member_count,
        "type": str(thread.type),
        "created_at": str(thread.created_at),
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_thread(
        channel_id: str,
        name: str,
        *,
        message_id: str | None = None,
        auto_archive_duration: int = 1440,
        slowmode_delay: int = 0,
        reason: str | None = None,
    ) -> dict:
        """Create a thread in a text or forum channel.

        Args:
            channel_id: Parent channel ID.
            name: Thread name.
            message_id: Message to create thread from (optional, not for forums).
            auto_archive_duration: Minutes until auto-archive (60, 1440, 4320, 10080).
            slowmode_delay: Slowmode in seconds.
            reason: Audit log reason.
        """
        bot = get_bot()
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        kwargs: dict = {
            "name": name,
            "auto_archive_duration": auto_archive_duration,
            "slowmode_delay": slowmode_delay,
            "reason": reason,
        }
        if message_id:
            kwargs["message"] = discord.Object(id=int(message_id))

        thread = await channel.create_thread(**kwargs)
        if isinstance(thread, tuple):
            thread = thread[0]
        return _thread_to_dict(thread)

    @mcp.tool()
    async def edit_thread(
        thread_id: str,
        *,
        name: str | None = None,
        archived: bool | None = None,
        locked: bool | None = None,
        slowmode_delay: int | None = None,
        auto_archive_duration: int | None = None,
        reason: str | None = None,
    ) -> dict:
        """Edit a thread's settings.

        Args:
            thread_id: Thread to edit.
            name: New name.
            archived: Set archived state.
            locked: Set locked state.
            slowmode_delay: Slowmode in seconds.
            auto_archive_duration: Auto-archive duration in minutes.
            reason: Audit log reason.
        """
        bot = get_bot()
        thread = bot.get_channel(int(thread_id))
        if thread is None:
            raise ValueError(f"Thread {thread_id} not found (not in cache).")

        kwargs: dict = {}
        if name is not None:
            kwargs["name"] = name
        if archived is not None:
            kwargs["archived"] = archived
        if locked is not None:
            kwargs["locked"] = locked
        if slowmode_delay is not None:
            kwargs["slowmode_delay"] = slowmode_delay
        if auto_archive_duration is not None:
            kwargs["auto_archive_duration"] = auto_archive_duration
        if reason is not None:
            kwargs["reason"] = reason

        updated = await thread.edit(**kwargs)
        return _thread_to_dict(updated or thread)

    @mcp.tool()
    async def delete_thread(
        thread_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a thread.

        Args:
            thread_id: Thread to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        thread = bot.get_channel(int(thread_id))
        if thread is None:
            raise ValueError(f"Thread {thread_id} not found (not in cache).")

        await thread.delete(reason=reason)
        return f"Deleted thread {thread.name} ({thread_id})."

    @mcp.tool()
    async def list_active_threads(guild_id: str) -> list[dict]:
        """List all active threads in a guild.

        Args:
            guild_id: Target guild ID.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        threads = await guild.active_threads()
        return [_thread_to_dict(t) for t in threads]

    @mcp.tool()
    async def join_thread(thread_id: str) -> str:
        """Make the bot join a thread.

        Args:
            thread_id: Thread to join.
        """
        bot = get_bot()
        thread = bot.get_channel(int(thread_id))
        if thread is None:
            raise ValueError(f"Thread {thread_id} not found (not in cache).")

        await thread.join()
        return f"Joined thread {thread.name} ({thread_id})."

    @mcp.tool()
    async def leave_thread(thread_id: str) -> str:
        """Make the bot leave a thread.

        Args:
            thread_id: Thread to leave.
        """
        bot = get_bot()
        thread = bot.get_channel(int(thread_id))
        if thread is None:
            raise ValueError(f"Thread {thread_id} not found (not in cache).")

        await thread.leave()
        return f"Left thread {thread.name} ({thread_id})."

    @mcp.tool()
    async def add_thread_member(
        thread_id: str,
        user_id: str,
    ) -> str:
        """Add a user to a thread.

        Args:
            thread_id: Target thread.
            user_id: User to add.
        """
        bot = get_bot()
        thread = bot.get_channel(int(thread_id))
        if thread is None:
            raise ValueError(f"Thread {thread_id} not found (not in cache).")

        await thread.add_user(discord.Object(id=int(user_id)))
        return f"Added user {user_id} to thread {thread.name} ({thread_id})."

    @mcp.tool()
    async def remove_thread_member(
        thread_id: str,
        user_id: str,
    ) -> str:
        """Remove a user from a thread.

        Args:
            thread_id: Target thread.
            user_id: User to remove.
        """
        bot = get_bot()
        thread = bot.get_channel(int(thread_id))
        if thread is None:
            raise ValueError(f"Thread {thread_id} not found (not in cache).")

        await thread.remove_user(discord.Object(id=int(user_id)))
        return f"Removed user {user_id} from thread {thread.name} ({thread_id})."
