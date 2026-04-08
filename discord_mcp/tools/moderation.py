"""Moderation tools — audit log, automod, purge, ban list."""

from __future__ import annotations

import datetime

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot

ACTION_TYPE_MAP = {name: member for name, member in discord.AuditLogAction.__members__.items()}

TRIGGER_TYPE_MAP = {
    "keyword": discord.AutoModRuleTriggerType.keyword,
    "spam": discord.AutoModRuleTriggerType.spam,
    "keyword_preset": discord.AutoModRuleTriggerType.keyword_preset,
    "mention_spam": discord.AutoModRuleTriggerType.mention_spam,
}


def _audit_entry_to_dict(entry: discord.AuditLogEntry) -> dict:
    """Convert an audit log entry to a serialisable dict."""
    return {
        "id": str(entry.id),
        "action": str(entry.action),
        "user_id": str(entry.user_id),
        "target": str(entry.target) if entry.target else None,
        "reason": entry.reason,
        "created_at": str(entry.created_at),
    }


def _automod_rule_to_dict(rule: discord.AutoModRule) -> dict:
    """Convert an automod rule to a serialisable dict."""
    return {
        "id": str(rule.id),
        "name": rule.name,
        "enabled": rule.enabled,
        "creator_id": str(rule.creator_id),
        "trigger_type": str(rule.trigger.type),
        "event_type": str(rule.event_type),
        "exempt_role_ids": [str(rid) for rid in rule.exempt_role_ids],
        "exempt_channel_ids": [str(cid) for cid in rule.exempt_channel_ids],
    }


def _build_action(action_dict: dict) -> discord.AutoModRuleAction:
    """Convert an action dict to an AutoModRuleAction."""
    action_type = action_dict["type"]
    if action_type == "block_message":
        return discord.AutoModRuleAction(
            custom_message=action_dict.get("custom_message"),
        )
    elif action_type == "send_alert_message":
        return discord.AutoModRuleAction(
            channel_id=action_dict["channel_id"],
        )
    elif action_type == "timeout":
        return discord.AutoModRuleAction(
            duration=datetime.timedelta(seconds=action_dict["duration_seconds"]),
        )
    else:
        return discord.AutoModRuleAction()


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_audit_log(
        guild_id: str,
        *,
        limit: int = 50,
        user_id: str | None = None,
        action_type: str | None = None,
    ) -> list[dict]:
        """Fetch audit log entries for a guild.

        Args:
            guild_id: Target guild.
            limit: Max entries to return (1-100).
            user_id: Filter by user who performed the action.
            action_type: Filter by action type (e.g. "ban", "kick", "channel_create").
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        kwargs: dict = {"limit": limit}
        if user_id is not None:
            kwargs["user"] = discord.Object(id=int(user_id))
        if action_type is not None:
            kwargs["action"] = ACTION_TYPE_MAP[action_type]

        entries: list[dict] = []
        async for entry in guild.audit_logs(**kwargs):
            entries.append(_audit_entry_to_dict(entry))
        return entries

    @mcp.tool()
    async def list_bans(
        guild_id: str,
        limit: int = 100,
    ) -> list[dict]:
        """List all bans in a guild.

        Args:
            guild_id: Target guild.
            limit: Max bans to return.

        Returns:
            List of bans with user info and reason.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        bans: list[dict] = []
        async for ban_entry in guild.bans(limit=limit):
            bans.append({
                "user_id": str(ban_entry.user.id),
                "user_name": ban_entry.user.name,
                "reason": ban_entry.reason,
            })
        return bans

    @mcp.tool()
    async def purge_messages(
        channel_id: str,
        limit: int,
        *,
        user_id: str | None = None,
        contains: str | None = None,
        before_message_id: str | None = None,
        after_message_id: str | None = None,
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
        bot = get_bot()
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")

        kwargs: dict = {"limit": limit, "reason": reason}

        if user_id is not None or contains is not None:
            _user_id_int = int(user_id) if user_id is not None else None
            def check(message: discord.Message) -> bool:
                if _user_id_int is not None and message.author.id != _user_id_int:
                    return False
                if contains is not None and contains not in message.content:
                    return False
                return True
            kwargs["check"] = check

        if before_message_id is not None:
            kwargs["before"] = discord.Object(id=int(before_message_id))
        if after_message_id is not None:
            kwargs["after"] = discord.Object(id=int(after_message_id))

        deleted = await channel.purge(**kwargs)
        return f"Purged {len(deleted)} message(s) from channel {channel_id}."

    @mcp.tool()
    async def list_automod_rules(guild_id: str) -> list[dict]:
        """List all auto-moderation rules in a guild.

        Args:
            guild_id: Target guild.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        rules = await guild.fetch_automod_rules()
        return [_automod_rule_to_dict(r) for r in rules]

    @mcp.tool()
    async def create_automod_rule(
        guild_id: str,
        name: str,
        trigger_type: str,
        actions: list[dict],
        *,
        enabled: bool = True,
        keyword_filter: list[str] | None = None,
        regex_patterns: list[str] | None = None,
        exempt_role_ids: list[str] | None = None,
        exempt_channel_ids: list[str] | None = None,
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
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        trigger = discord.AutoModTrigger(
            type=TRIGGER_TYPE_MAP[trigger_type],
            keyword_filter=keyword_filter,
            regex_patterns=regex_patterns,
        )

        actions_list = [_build_action(a) for a in actions]
        exempt_roles = [discord.Object(id=int(rid)) for rid in (exempt_role_ids or [])]
        exempt_channels = [discord.Object(id=int(cid)) for cid in (exempt_channel_ids or [])]

        rule = await guild.create_automod_rule(
            name=name,
            event_type=discord.AutoModRuleEventType.message_send,
            trigger=trigger,
            actions=actions_list,
            enabled=enabled,
            exempt_roles=exempt_roles,
            exempt_channels=exempt_channels,
            reason=reason,
        )
        return _automod_rule_to_dict(rule)

    @mcp.tool()
    async def delete_automod_rule(
        guild_id: str,
        rule_id: str,
        *,
        reason: str | None = None,
    ) -> str:
        """Delete an auto-moderation rule.

        Args:
            guild_id: Guild containing the rule.
            rule_id: Rule to delete.
            reason: Audit log reason.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        rule = await guild.fetch_automod_rule(int(rule_id))
        await rule.delete(reason=reason)
        return f"Deleted automod rule {rule.name} ({rule_id})."
