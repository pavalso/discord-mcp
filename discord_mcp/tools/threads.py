"""Thread tools — create, edit, archive, join, manage members."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_thread(
        channel_id: int,
        name: str,
        *,
        message_id: int | None = None,
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
        raise NotImplementedError

    @mcp.tool()
    async def edit_thread(
        thread_id: int,
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
        raise NotImplementedError

    @mcp.tool()
    async def delete_thread(
        thread_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete a thread.

        Args:
            thread_id: Thread to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def list_active_threads(guild_id: int) -> list[dict]:
        """List all active threads in a guild.

        Args:
            guild_id: Target guild ID.
        """
        raise NotImplementedError

    @mcp.tool()
    async def join_thread(thread_id: int) -> str:
        """Make the bot join a thread.

        Args:
            thread_id: Thread to join.
        """
        raise NotImplementedError

    @mcp.tool()
    async def leave_thread(thread_id: int) -> str:
        """Make the bot leave a thread.

        Args:
            thread_id: Thread to leave.
        """
        raise NotImplementedError

    @mcp.tool()
    async def add_thread_member(
        thread_id: int,
        user_id: int,
    ) -> str:
        """Add a user to a thread.

        Args:
            thread_id: Target thread.
            user_id: User to add.
        """
        raise NotImplementedError

    @mcp.tool()
    async def remove_thread_member(
        thread_id: int,
        user_id: int,
    ) -> str:
        """Remove a user from a thread.

        Args:
            thread_id: Target thread.
            user_id: User to remove.
        """
        raise NotImplementedError
