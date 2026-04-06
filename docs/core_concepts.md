# Core Concepts

## Intents

discord.py v2.0+ requires explicit intents. The bot must declare which events and data it needs access to.

```python
intents = discord.Intents.default()
intents.members = True          # Required for: fetch_members, member events, member cache
intents.message_content = True  # Required for: message.content on non-mention messages
bot = commands.Bot(command_prefix="!", intents=intents)
```

### Intent Requirements by Tool

| Intent | Required for |
|--------|-------------|
| `members` | `list_members`, `search_members`, `get_member` (cache), thread member fetching |
| `message_content` | Reading `message.content` on messages not directed at the bot |
| `guilds` (default) | Guild/channel/role cache |
| `guild_messages` (default) | Message events in guild channels |

## Cache vs API Calls

### `get_*` Methods (Cache Lookup)

- **No API call** -- instant, returns `None` if not cached
- Used for: `bot.get_guild()`, `bot.get_channel()`, `bot.get_user()`, `guild.get_member()`, `guild.get_role()`, `guild.get_channel()`
- Cache depends on intents and whether the bot has seen the entity

### `fetch_*` Methods (API Call)

- **Makes HTTP request** -- slower, subject to rate limits, always returns fresh data
- Used for: `bot.fetch_guild()`, `bot.fetch_channel()`, `bot.fetch_user()`, `guild.fetch_member()`, `bot.fetch_webhook()`, `bot.fetch_invite()`
- Raises `NotFound` if the entity doesn't exist, `Forbidden` if no access

### Recommended Pattern

```python
# Try cache first, fall back to API
guild = bot.get_guild(guild_id)
if guild is None:
    guild = await bot.fetch_guild(guild_id)
```

For tools where freshness matters (e.g., member info), prefer `fetch_*` directly.

## Async Iterators

Several discord.py methods return async iterators rather than lists:

```python
# guild.fetch_members(), guild.audit_logs(), guild.bans(),
# channel.history(), channel.archived_threads()

# Collect all results into a list:
members = [m async for m in guild.fetch_members(limit=100)]

# Or iterate:
async for entry in guild.audit_logs(limit=50):
    process(entry)

# With flattening (deprecated in favor of list comprehension):
members = await guild.fetch_members(limit=100).flatten()
```

## Error Handling

### Common Exceptions

| Exception | When |
|-----------|------|
| `discord.NotFound` | Entity doesn't exist (404) |
| `discord.Forbidden` | Bot lacks permissions (403) |
| `discord.HTTPException` | Any Discord API error |
| `discord.InvalidData` | Unexpected data from Discord |

### Error Response Pattern

```python
try:
    channel = bot.get_channel(channel_id)
    if channel is None:
        return f"Channel {channel_id} not found"
    await channel.send(content)
    return "Message sent successfully"
except discord.Forbidden:
    return f"Bot lacks permission to send messages in channel {channel_id}"
except discord.HTTPException as e:
    return f"Discord API error: {e}"
```

## Rate Limiting

discord.py handles rate limits automatically by default. The library will:
1. Queue requests that hit rate limits
2. Wait the required time before retrying
3. Respect per-route and global rate limits

To change this behavior:
```python
bot = commands.Bot(..., max_ratelimit_timeout=30.0)
# Raises discord.RateLimited instead of waiting if limit > 30s
```

## Snowflake IDs

All Discord entities use 64-bit integer IDs (snowflakes). They encode:
- Timestamp (milliseconds since Discord epoch: 2015-01-01)
- Worker ID, process ID, increment

```python
# Get creation time from any snowflake
from discord.utils import snowflake_time
created_at = snowflake_time(message_id)  # Returns datetime

# Create a snowflake from a datetime (for before/after parameters)
from discord.utils import time_snowflake
snowflake = time_snowflake(datetime_obj)
```

## Object References

Many methods accept `discord.Object(id=...)` as a lightweight reference when you only have an ID:

```python
# Instead of fetching the full user just to pass it:
await guild.ban(discord.Object(id=user_id), reason="spam")

# Works for: ban, unban, kick, and any method accepting abc.Snowflake
```

## Datetime Handling

All datetimes from Discord are UTC-aware. When passing datetimes to the API:

```python
import datetime

# Use discord's helper for current UTC time
now = discord.utils.utcnow()

# Create timezone-aware datetime
start = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)

# Parse ISO 8601 string (for tool parameters)
from datetime import datetime, timezone
dt = datetime.fromisoformat(iso_string).replace(tzinfo=timezone.utc)
```

## Converting Permission Strings

Tools accept permission names as strings. Convert to discord.py `Permissions`:

```python
# From a list of permission name strings
perms = discord.Permissions()
for perm_name in permission_strings:
    setattr(perms, perm_name, True)

# Or using kwargs
perms = discord.Permissions(**{name: True for name in permission_strings})

# For PermissionOverwrite (channel-specific)
overwrite = discord.PermissionOverwrite()
for name in allow_list:
    setattr(overwrite, name, True)
for name in deny_list:
    setattr(overwrite, name, False)
```
