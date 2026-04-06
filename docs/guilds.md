# Guilds Tools -- discord.py API Reference

Tools in `discord_mcp/tools/guilds.py` (3 tools).

---

## list_guilds

**Tool params:** (none)

### API Calls

#### `Client.guilds` (property)

```python
guilds = bot.guilds  # -> Sequence[Guild]
```

Returns all guilds the bot is a member of, from cache.

**Key Guild attributes for listing:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Guild ID |
| `name` | `str` | Guild name |
| `owner_id` | `int` | Guild owner's user ID |
| `member_count` | `Optional[int]` | Member count (needs `members` intent for accuracy) |
| `description` | `Optional[str]` | Guild description |
| `premium_tier` | `int` | Boost level (0-3) |
| `premium_subscription_count` | `int` | Number of boosts |
| `features` | `List[str]` | Enabled features |
| `icon` | `Optional[Asset]` | Guild icon (`.url` for URL) |
| `large` | `bool` | Whether the guild is "large" (250+ members) |
| `created_at` | `datetime` | Creation timestamp |

---

## get_guild

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)  # -> Optional[Guild]
```

Cache lookup. For full details, also consider:
```python
guild = await bot.fetch_guild(guild_id, with_counts=True)
# with_counts=True populates approximate_member_count and approximate_presence_count
```

**Full Guild attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Guild ID |
| `name` | `str` | Guild name |
| `description` | `Optional[str]` | Guild description |
| `owner_id` | `int` | Owner's user ID |
| `owner` | `Optional[Member]` | Owner member (property) |
| `icon` | `Optional[Asset]` | Guild icon |
| `banner` | `Optional[Asset]` | Guild banner |
| `splash` | `Optional[Asset]` | Invite splash image |
| `verification_level` | `VerificationLevel` | Verification requirement |
| `default_notifications` | `NotificationLevel` | Default notification setting |
| `explicit_content_filter` | `ContentFilter` | Explicit content filter level |
| `mfa_level` | `MFALevel` | Moderator 2FA requirement |
| `features` | `List[str]` | Enabled features |
| `premium_tier` | `int` | Boost level (0-3) |
| `premium_subscription_count` | `int` | Number of boosts |
| `preferred_locale` | `Locale` | Primary language |
| `nsfw_level` | `NSFWLevel` | NSFW level |
| `vanity_url_code` | `Optional[str]` | Vanity invite code |
| `member_count` | `Optional[int]` | Total members |
| `max_members` | `Optional[int]` | Max members (only via `fetch_guild`) |
| `afk_timeout` | `int` | AFK timeout in seconds |
| `afk_channel` | `Optional[VoiceChannel]` | AFK voice channel |
| `system_channel` | `Optional[TextChannel]` | System messages channel |
| `rules_channel` | `Optional[TextChannel]` | Rules channel (Community) |
| `approximate_member_count` | `Optional[int]` | Approximate members (via `fetch_guild` with `with_counts`) |
| `approximate_presence_count` | `Optional[int]` | Approximate online (via `fetch_guild` with `with_counts`) |
| `emoji_limit` | `int` | Max custom emojis |
| `sticker_limit` | `int` | Max stickers |
| `filesize_limit` | `int` | Max file upload size (bytes) |
| `bitrate_limit` | `float` | Max voice bitrate |

**Collection properties:**
- `channels` -> `Sequence[abc.GuildChannel]`
- `text_channels` -> `List[TextChannel]`
- `voice_channels` -> `List[VoiceChannel]`
- `categories` -> `List[CategoryChannel]`
- `forums` -> `List[ForumChannel]`
- `threads` -> `Sequence[Thread]`
- `members` -> `Sequence[Member]`
- `roles` -> `Sequence[Role]`
- `emojis` -> `Tuple[Emoji, ...]`
- `stickers` -> `Tuple[GuildSticker, ...]`
- `scheduled_events` -> `Sequence[ScheduledEvent]`
- `me` -> `Member` (the bot's member object)

---

## edit_guild

**Tool params:** `guild_id: int`, `*, name: str | None = None`, `description: str | None = None`, `verification_level: str | None = None`, `default_notifications: str | None = None`, `explicit_content_filter: str | None = None`, `afk_channel_id: int | None = None`, `afk_timeout: int | None = None`, `system_channel_id: int | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.edit()`

```python
await guild.edit(
    *,
    reason: str = ...,
    name: str = ...,
    description: str = ...,
    icon: bytes = ...,
    banner: bytes = ...,
    splash: bytes = ...,
    discovery_splash: bytes = ...,
    community: bool = ...,
    afk_channel: Optional[VoiceChannel] = ...,
    owner: Snowflake = ...,                          # Transfer ownership
    afk_timeout: int = ...,                          # 60, 300, 900, 1800, 3600
    default_notifications: NotificationLevel = ...,
    verification_level: VerificationLevel = ...,
    explicit_content_filter: ContentFilter = ...,
    vanity_code: str = ...,
    system_channel: Optional[TextChannel] = ...,
    system_channel_flags: SystemChannelFlags = ...,
    preferred_locale: Locale = ...,
    rules_channel: Optional[TextChannel] = ...,
    public_updates_channel: Optional[TextChannel] = ...,
    premium_progress_bar_enabled: bool = ...,
    discoverable: bool = ...,
    invites_disabled: bool = ...,
    widget_enabled: bool = ...,
    widget_channel: Optional[abc.GuildChannel] = ...,
    mfa_level: MFALevel = ...,
    raid_alerts_disabled: bool = ...,
    safety_alerts_channel: Optional[TextChannel] = ...,
) -> Guild
```

**Permissions:** `manage_guild` required.

### Enum Conversions

**VerificationLevel:**
```python
discord.VerificationLevel.none        # No requirements
discord.VerificationLevel.low         # Must have verified email
discord.VerificationLevel.medium      # Must be registered for 5+ minutes
discord.VerificationLevel.high        # Must be a member for 10+ minutes
discord.VerificationLevel.highest     # Must have a verified phone number
```

**NotificationLevel:**
```python
discord.NotificationLevel.all_messages    # Every message triggers notification
discord.NotificationLevel.only_mentions   # Only @mentions trigger notifications
```

**ContentFilter:**
```python
discord.ContentFilter.disabled              # No scanning
discord.ContentFilter.no_role               # Scan members without roles
discord.ContentFilter.all_members           # Scan everyone
```

**Converting string params to enums:**
```python
VERIFICATION_MAP = {
    "none": discord.VerificationLevel.none,
    "low": discord.VerificationLevel.low,
    "medium": discord.VerificationLevel.medium,
    "high": discord.VerificationLevel.high,
    "highest": discord.VerificationLevel.highest,
}

NOTIFICATION_MAP = {
    "all_messages": discord.NotificationLevel.all_messages,
    "only_mentions": discord.NotificationLevel.only_mentions,
}

CONTENT_FILTER_MAP = {
    "disabled": discord.ContentFilter.disabled,
    "members_without_roles": discord.ContentFilter.no_role,
    "all_members": discord.ContentFilter.all_members,
}
```

**Channel references:**
```python
kwargs = {}
if afk_channel_id is not None:
    kwargs["afk_channel"] = guild.get_channel(afk_channel_id)
if system_channel_id is not None:
    kwargs["system_channel"] = guild.get_channel(system_channel_id)

await guild.edit(**kwargs, reason=reason)
```

**AFK timeout valid values:** 60, 300, 900, 1800, 3600 (seconds).
