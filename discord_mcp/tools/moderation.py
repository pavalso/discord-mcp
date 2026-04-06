"""Moderation tools — audit log, automod, purge, ban list."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_audit_log(
        guild_id: int,
        *,
        limit: int = 50,
        user_id: int | None = None,
        action_type: str | None = None,
    ) -> list[dict]:
        """Fetch audit log entries for a guild.

        Args:
            guild_id: Target guild.
            limit: Max entries to return (1-100).
            user_id: Filter by user who performed the action.
            action_type: Filter by action type (e.g. "ban", "kick", "channel_create").
        """
        raise NotImplementedError

    @mcp.tool()
    async def list_bans(
        guild_id: int,
        limit: int = 100,
    ) -> list[dict]:
        """List all bans in a guild.

        Args:
            guild_id: Target guild.
            limit: Max bans to return.

        Returns:
            List of bans with user info and reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def purge_messages(
        channel_id: int,
        limit: int,
        *,
        user_id: int | None = None,
        contains: str | None = None,
        before_message_id: int | None = None,
        after_message_id: int | None = None,
        reason: str | None = None,
    ) -> str:
        """Bulk delete messages from a channel.

        Args:
            channel_id: Target channel.
            limit: Max messages to delete (1-100).
            user_id: Only delete messages by this user.
            contains: Only delete messages containing this substring.
            before_message_id: Only messages before this ID.
            after_message_id: Only messages after this ID.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def list_automod_rules(guild_id: int) -> list[dict]:
        """List all auto-moderation rules in a guild.

        Args:
            guild_id: Target guild.
        """
        raise NotImplementedError

    @mcp.tool()
    async def create_automod_rule(
        guild_id: int,
        name: str,
        trigger_type: str,
        actions: list[dict],
        *,
        enabled: bool = True,
        keyword_filter: list[str] | None = None,
        regex_patterns: list[str] | None = None,
        exempt_role_ids: list[int] | None = None,
        exempt_channel_ids: list[int] | None = None,
        reason: str | None = None,
    ) -> dict:
        """Create an auto-moderation rule.

        Args:
            guild_id: Target guild.
            name: Rule name.
            trigger_type: "keyword", "spam", "keyword_preset", or "mention_spam".
            actions: List of action dicts, e.g. [{"type": "block_message"}],
                     [{"type": "send_alert_message", "channel_id": 123}],
                     [{"type": "timeout", "duration_seconds": 60}].
            enabled: Whether the rule is active.
            keyword_filter: Keywords to match (for "keyword" trigger).
            regex_patterns: Regex patterns to match (for "keyword" trigger).
            exempt_role_ids: Roles exempt from this rule.
            exempt_channel_ids: Channels exempt from this rule.
            reason: Audit log reason.
        """
        raise NotImplementedError

    @mcp.tool()
    async def delete_automod_rule(
        guild_id: int,
        rule_id: int,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete an auto-moderation rule.

        Args:
            guild_id: Guild containing the rule.
            rule_id: Rule to delete.
            reason: Audit log reason.
        """
        raise NotImplementedError
