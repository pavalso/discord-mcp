# Discord MCP Server -- discord.py API Reference

Reference documentation for the 93 MCP tools in this project. Each file covers one tool module and maps tool functions to the discord.py API calls they require.

## Index

| Document | Module | Tools |
|----------|--------|-------|
| [connection.md](connection.md) | `server.py` | 4 -- connect, disconnect, status, presence |
| [messages.md](messages.md) | `tools/messages.py` | 13 -- send, files, embed, edit, delete, get, history, pins, reactions |
| [channels.md](channels.md) | `tools/channels.py` | 10 -- list, get, create (text/voice/stage/category/forum), edit, delete, permissions |
| [threads.md](threads.md) | `tools/threads.py` | 9 -- create, edit, delete, list active/archived, join/leave, member management |
| [members.md](members.md) | `tools/members.py` | 12 -- get user/member, list, search, kick, ban, timeout, edit, roles, DM |
| [roles.md](roles.md) | `tools/roles.py` | 5 -- list, get, create, edit, delete |
| [guilds.md](guilds.md) | `tools/guilds.py` | 4 -- list, get, edit, leave |
| [webhooks.md](webhooks.md) | `tools/webhooks.py` | 5 -- list, create, send, edit, delete |
| [invites.md](invites.md) | `tools/invites.py` | 4 -- list, create, delete, get |
| [emojis.md](emojis.md) | `tools/emojis.py` | 8 -- list/create/edit/delete emojis and stickers |
| [scheduled_events.md](scheduled_events.md) | `tools/scheduled_events.py` | 4 -- list, create, edit, delete |
| [moderation.md](moderation.md) | `tools/moderation.py` | 6 -- audit log, bans, purge, automod |
| [voice.md](voice.md) | `tools/voice.py` | 9 -- join/leave/move, mute/deafen, status, audio playback |
| [core_concepts.md](core_concepts.md) | -- | Intents, cache vs fetch, permissions, async patterns |
| [permissions_reference.md](permissions_reference.md) | -- | Full permissions flag list and PermissionOverwrite usage |
| [enums_reference.md](enums_reference.md) | -- | Common enums: ChannelType, VerificationLevel, EntityType, etc. |

## Key Patterns

All tools follow the same pattern:

```python
from discord_mcp.bot import get_bot

def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def tool_name(required_id: str, *, optional_param: str | None = None) -> dict:
        """Tool description for LLM consumption.

        Args:
            required_id: Description.
            optional_param: Description.
        """
        bot = get_bot()
        # Use bot.get_*() for cache lookups, bot.fetch_*() for API calls
        # Perform discord.py operations
        # Return a dict, or a plain string for simple confirmations
```

Two conventions worth noting, since the per-module docs below were written
before implementation and still show `int` parameters:

- **Snowflakes are passed as `str`, not `int`.** IDs exceed 2^53 and would lose
  precision in a JSON number. Tools take `channel_id: str` and call
  `int(channel_id)` internally; returned IDs are stringified too.
- **Tools live inside a `register(mcp)` function** in their module, called from
  `server.py`. Only the four connection tools are defined at module level.

## Cache vs Fetch

| Pattern | API Call? | Returns | When to use |
|---------|-----------|---------|-------------|
| `bot.get_guild(id)` | No | `Optional[Guild]` | Guild is cached (bot is a member) |
| `bot.fetch_guild(id)` | Yes | `Guild` | Need fresh data or guild not cached |
| `bot.get_channel(id)` | No | `Optional[Channel]` | Channel is in a cached guild |
| `bot.fetch_channel(id)` | Yes | `Channel` | Need fresh data |
| `guild.get_member(id)` | No | `Optional[Member]` | Member is cached (needs members intent) |
| `guild.fetch_member(id)` | Yes | `Member` | Always works, makes API call |
| `guild.get_role(id)` | No | `Optional[Role]` | Role is cached (always available) |
