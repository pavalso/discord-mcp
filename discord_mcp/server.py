"""Discord MCP Server — main entry point.

Exposes Discord bot operations as MCP tools, organized by domain:
  - Connection management
  - Messaging (send, edit, delete, reply, reactions, history)
  - Channel management (create, edit, delete, list)
  - Thread management (create, edit, archive, members)
  - Member management (fetch, kick, ban, timeout, roles)
  - Role management (create, edit, delete, list)
  - Guild info and settings
  - Webhook operations
  - Invite management
  - Emoji/sticker management
  - Scheduled events
  - Moderation (audit log, automod, purge)
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot, start_bot, stop_bot
from discord_mcp.tools.channels import register as register_channels
from discord_mcp.tools.emojis import register as register_emojis
from discord_mcp.tools.guilds import register as register_guilds
from discord_mcp.tools.invites import register as register_invites
from discord_mcp.tools.members import register as register_members
from discord_mcp.tools.messages import register as register_messages
from discord_mcp.tools.moderation import register as register_moderation
from discord_mcp.tools.roles import register as register_roles
from discord_mcp.tools.scheduled_events import register as register_scheduled_events
from discord_mcp.tools.threads import register as register_threads
from discord_mcp.tools.webhooks import register as register_webhooks

mcp = FastMCP("Discord MCP Server")

# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------


@mcp.tool()
async def connect(token: str | None = None) -> str:
    """Connect the Discord bot.

    Args:
        token: Bot token. Falls back to DISCORD_BOT_TOKEN env var.

    Returns:
        Connection status with the bot's username.
    """
    resolved_token = token or os.environ.get("DISCORD_BOT_TOKEN")
    if not resolved_token:
        return "Error: No token provided and DISCORD_BOT_TOKEN env var is not set."

    bot = await start_bot(resolved_token)
    return f"Connected as {bot.user} (ID: {bot.user.id})"


@mcp.tool()
async def disconnect() -> str:
    """Disconnect the Discord bot gracefully."""
    await stop_bot()
    return "Disconnected."


@mcp.tool()
async def bot_status() -> dict:
    """Get the current bot connection status and basic info."""
    try:
        bot = get_bot()
    except RuntimeError:
        return {"connected": False}

    return {
        "connected": True,
        "user": str(bot.user),
        "user_id": bot.user.id,
        "guild_count": len(bot.guilds),
        "latency_ms": round(bot.latency * 1000, 2),
    }


# ---------------------------------------------------------------------------
# Register all tool modules
# ---------------------------------------------------------------------------

register_messages(mcp)
register_channels(mcp)
register_threads(mcp)
register_members(mcp)
register_roles(mcp)
register_guilds(mcp)
register_webhooks(mcp)
register_invites(mcp)
register_emojis(mcp)
register_scheduled_events(mcp)
register_moderation(mcp)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
