# Invites Tools -- discord.py API Reference

Tools in `discord_mcp/tools/invites.py` (4 tools).

---

## list_invites

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.invites()`

```python
invites = await guild.invites()  # -> List[Invite]
```

**Permissions:** `manage_guild` required.

Returns all active invites for the guild, including metadata only available from this endpoint.

**Key Invite attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | `str` | Invite code (URL fragment) |
| `id` | `str` | Same as `code` (property) |
| `url` | `str` | Full invite URL (property) |
| `guild` | `Optional[Guild]` | Guild the invite is for |
| `channel` | `Optional[GuildChannel]` | Target channel |
| `inviter` | `Optional[User]` | User who created the invite |
| `max_age` | `Optional[int]` | Max age in seconds (0 = never expires) |
| `max_uses` | `Optional[int]` | Max uses (0 = unlimited) |
| `uses` | `Optional[int]` | Current use count |
| `temporary` | `Optional[bool]` | Grants temporary membership |
| `created_at` | `Optional[datetime]` | When created |
| `expires_at` | `Optional[datetime]` | When it expires (None = never) |
| `type` | `InviteType` | Invite type |
| `target_type` | `InviteTarget` | Target type (stream, embedded app, etc.) |
| `target_user` | `Optional[User]` | Target user for stream invites |
| `scheduled_event` | `Optional[ScheduledEvent]` | Associated event |

**Notes:**
- `uses`, `max_uses`, `max_age`, `created_at`, `temporary` are only available from `Guild.invites()`, not from `Client.fetch_invite()`.
- `str(invite)` returns the invite URL.

---

## create_invite

**Tool params:** `channel_id: int`, `*, max_age: int = 86400`, `max_uses: int = 0`, `temporary: bool = False`, `unique: bool = True`, `reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)
```

#### `abc.GuildChannel.create_invite()`

```python
invite = await channel.create_invite(
    *,
    reason: str = None,
    max_age: int = 0,           # Seconds until expiry. 0 = never. Default in API is 86400 (24h)
    max_uses: int = 0,          # Max uses. 0 = unlimited
    temporary: bool = False,    # Kick on disconnect if no role assigned
    unique: bool = True,        # Always create new invite vs. reuse existing similar one
    target_type: InviteTarget = None,
    target_user: User = None,
    target_application_id: int = None,
    guest: bool = False,
) -> Invite
```

**Permissions:** `create_instant_invite` required.

**Notes:**
- Available on `TextChannel`, `VoiceChannel`, `StageChannel`, `ForumChannel`, and `CategoryChannel`.
- `unique=False` may return an existing invite with similar parameters instead of creating a new one.
- `max_age=0` creates an invite that never expires.

---

## delete_invite

**Tool params:** `invite_code: str`

### API Calls

#### Option 1: Using `Client.delete_invite()`

```python
invite = await bot.fetch_invite(invite_code)
await bot.delete_invite(invite, reason=reason)
```

#### Option 2: Using `Invite.delete()`

```python
invite = await bot.fetch_invite(invite_code)
await invite.delete(reason=reason)
```

**Permissions:** `manage_channels` required on the invite's channel, or `manage_guild` for any invite.

**Raises:** `NotFound` (invalid invite code), `Forbidden`, `HTTPException`.

---

## get_invite

**Tool params:** `invite_code: str`

### API Calls

#### `Client.fetch_invite()`

```python
invite = await bot.fetch_invite(
    invite_code,                             # Code or full URL
    *,
    with_counts: bool = True,                # Include member/presence counts
    with_expiration: bool = True,            # Include expiration info
    scheduled_event_id: int = None,          # Include specific event
) -> Invite
```

**Notes:**
- `invite_code` can be just the code (`"abc123"`) or a full URL (`"https://discord.gg/abc123"`).
- `with_counts=True` populates `approximate_member_count` and `approximate_presence_count`.
- This does NOT return `uses`, `max_uses`, `created_at` -- those are only from `Guild.invites()`.
- Does not require any special permissions.

**Raises:** `NotFound` (invalid/expired invite), `HTTPException`.
