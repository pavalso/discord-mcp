# Members Tools -- discord.py API Reference

Tools in `discord_mcp/tools/members.py` (11 tools).

---

## get_member

**Tool params:** `guild_id: int`, `user_id: int`

### API Calls

#### `Guild.fetch_member()`

```python
guild = bot.get_guild(guild_id)
member = await guild.fetch_member(user_id)  # -> Member
```

Always makes an API call. Use `guild.get_member(user_id)` for cache lookup (requires `members` intent).

**Key Member attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | User ID |
| `name` | `str` | Username |
| `display_name` | `str` | Nick > global_name > username |
| `nick` | `Optional[str]` | Server nickname |
| `global_name` | `Optional[str]` | Global display name |
| `bot` | `bool` | Whether the user is a bot |
| `joined_at` | `Optional[datetime]` | When they joined the guild |
| `premium_since` | `Optional[datetime]` | Nitro boost start |
| `roles` | `List[Role]` | Roles (includes @everyone, sorted by hierarchy) |
| `top_role` | `Role` | Highest role |
| `guild_permissions` | `Permissions` | Computed guild-level permissions |
| `status` | `Status` | Online status |
| `activity` | `Optional[BaseActivity]` | Current activity |
| `voice` | `Optional[VoiceState]` | Voice state if in voice |
| `timed_out_until` | `Optional[datetime]` | Timeout expiry |
| `pending` | `bool` | Hasn't passed membership screening |
| `avatar` | `Optional[Asset]` | User avatar |
| `guild_avatar` | `Optional[Asset]` | Server-specific avatar |

**Raises:** `Forbidden` (bot not in guild), `HTTPException`, `NotFound` (member not in guild).

---

## list_members

**Tool params:** `guild_id: int`, `*, limit: int = 100`

### API Calls

#### `Guild.fetch_members()`

```python
guild = bot.get_guild(guild_id)
members = [m async for m in guild.fetch_members(limit=limit)]
```

```python
async for member in guild.fetch_members(
    *,
    limit: int = 1000,
    after: Snowflake = ...,
) -> AsyncIterator[Member]
```

**Requires:** `Intents.members` privileged intent.

**Notes:**
- Max 1000 per call. For larger guilds, use `after` parameter with the last member's ID for pagination.
- Returns members sorted by ID.

---

## search_members

**Tool params:** `guild_id: int`, `query: str`, `*, limit: int = 10`

### API Calls

#### `Guild.query_members()`

```python
guild = bot.get_guild(guild_id)
members = await guild.query_members(query=query, limit=limit)
```

```python
await guild.query_members(
    query: str = None,
    *,
    limit: int = 5,
    user_ids: List[int] = None,
    presences: bool = False,
    cache: bool = True,
) -> List[Member]
```

**Notes:**
- Searches by username and nickname prefix (case-insensitive).
- Max `limit` is 100.
- Uses the gateway (websocket), not REST API.
- Results are cached by default.
- Can also search by `user_ids` (up to 100).

---

## kick_member

**Tool params:** `guild_id: int`, `user_id: int`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
member = await guild.fetch_member(user_id)
```

#### `Member.kick()` or `Guild.kick()`

```python
await member.kick(*, reason: str = None)
# or
await guild.kick(discord.Object(id=user_id), reason=reason)
```

**Permissions:** `kick_members` required. Bot's top role must be higher than the target's top role.

---

## ban_member

**Tool params:** `guild_id: int`, `user_id: int`, `*, delete_message_seconds: int = 0`, `reason: str | None = None`

### API Calls

#### `Guild.ban()`

```python
guild = bot.get_guild(guild_id)
await guild.ban(
    discord.Object(id=user_id),
    *,
    reason: str = None,
    delete_message_seconds: int = ...,  # 0-604800 (7 days)
)
```

**Permissions:** `ban_members` required.

**Notes:**
- `delete_message_seconds`: Number of seconds of messages to delete (0 = don't delete, max 604800 = 7 days).
- The user does NOT need to be in the guild -- you can ban by ID.
- `delete_message_days` is deprecated in favor of `delete_message_seconds`.

---

## unban_member

**Tool params:** `guild_id: int`, `user_id: int`, `*, reason: str | None = None`

### API Calls

#### `Guild.unban()`

```python
guild = bot.get_guild(guild_id)
await guild.unban(discord.Object(id=user_id), reason=reason)
```

**Permissions:** `ban_members` required.

**Raises:** `NotFound` if the user is not banned.

---

## timeout_member

**Tool params:** `guild_id: int`, `user_id: int`, `duration_seconds: int`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
member = await guild.fetch_member(user_id)
```

#### `Member.timeout()`

```python
import datetime

# Apply timeout
duration = datetime.timedelta(seconds=duration_seconds)
await member.timeout(duration, reason=reason)

# Remove timeout
await member.timeout(None, reason=reason)
```

```python
await member.timeout(
    until: Union[datetime.timedelta, datetime.datetime, None],
    /,
    *,
    reason: str = None,
)
```

**Permissions:** `moderate_members` required.

**Notes:**
- Max duration: 28 days.
- `until` can be a `timedelta` (relative) or `datetime` (absolute, must be UTC-aware).
- Passing `None` removes the timeout.
- Check status: `member.is_timed_out()` -> `bool`, `member.timed_out_until` -> `Optional[datetime]`.

---

## edit_member

**Tool params:** `guild_id: int`, `user_id: int`, `*, nickname: str | None = None`, `mute: bool | None = None`, `deafen: bool | None = None`, `voice_channel_id: int | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
member = await guild.fetch_member(user_id)
```

#### `Member.edit()`

```python
await member.edit(
    *,
    nick: str = ...,
    mute: bool = ...,
    deafen: bool = ...,
    suppress: bool = ...,               # Stage channel only
    roles: List[Role] = ...,            # Replaces ALL roles
    voice_channel: Optional[VoiceChannel] = ...,
    timed_out_until: Optional[datetime] = ...,
    bypass_verification: bool = ...,
    avatar: Optional[bytes] = ...,      # Guild avatar (Nitro required)
    banner: Optional[bytes] = ...,      # Guild banner
    bio: Optional[str] = ...,           # Guild bio
    reason: str = None,
) -> Optional[Member]
```

**Permissions per field:**
| Field | Permission |
|-------|-----------|
| `nick` | `manage_nicknames` |
| `mute` | `mute_members` |
| `deafen` | `deafen_members` |
| `roles` | `manage_roles` |
| `voice_channel` | `move_members` |
| `timed_out_until` | `moderate_members` |
| `bypass_verification` | `moderate_members` |

**Voice channel usage:**
```python
if voice_channel_id:
    vc = guild.get_channel(voice_channel_id)
    await member.edit(voice_channel=vc, reason=reason)

# Disconnect from voice:
await member.edit(voice_channel=None, reason=reason)
```

---

## add_member_roles

**Tool params:** `guild_id: int`, `user_id: int`, `role_ids: list[int]`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
member = await guild.fetch_member(user_id)
roles = [guild.get_role(rid) for rid in role_ids]
```

#### `Member.add_roles()`

```python
await member.add_roles(*roles, reason=reason, atomic=True)
```

```python
await member.add_roles(
    *roles: Snowflake,
    reason: str = None,
    atomic: bool = True,
)
```

**Permissions:** `manage_roles`. Bot's top role must be above all roles being added.

**Notes:**
- `atomic=True` (default): Uses individual API calls per role. If one fails, others may have succeeded.
- `atomic=False`: Replaces the entire role list in one call (adds specified roles to existing ones).
- Roles that the member already has are silently ignored.

---

## remove_member_roles

**Tool params:** `guild_id: int`, `user_id: int`, `role_ids: list[int]`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
member = await guild.fetch_member(user_id)
roles = [guild.get_role(rid) for rid in role_ids]
```

#### `Member.remove_roles()`

```python
await member.remove_roles(*roles, reason=reason, atomic=True)
```

Same semantics as `add_roles()`. Bot's top role must be above all roles being removed.

---

## send_dm

**Tool params:** `user_id: int`, `content: str`

### API Calls

```python
user = bot.get_user(user_id)
if user is None:
    user = await bot.fetch_user(user_id)
```

#### `User.send()` / `Member.send()`

```python
await user.send(content)  # -> Message
```

Both `User` and `Member` inherit from `Messageable`, so `.send()` works on either. This automatically creates a DM channel if one doesn't exist.

Alternatively:
```python
dm_channel = await user.create_dm()  # -> DMChannel
await dm_channel.send(content)
```

**Notes:**
- Sending DMs to bots is not possible.
- Users can disable DMs from server members. This raises `Forbidden`.
- The bot does NOT need to share a guild with the user, but `fetch_user` requires knowing their ID.
