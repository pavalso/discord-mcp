# Channels Tools -- discord.py API Reference

Tools in `discord_mcp/tools/channels.py` (9 tools).

---

## list_channels

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)  # -> Optional[Guild]
```

#### `Guild.channels` (property)

```python
guild.channels  # -> Sequence[abc.GuildChannel]
```

Returns all channels (text, voice, category, forum, stage) sorted by position. Does not include threads.

**Key attributes per channel:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Channel ID |
| `name` | `str` | Channel name |
| `type` | `ChannelType` | `text`, `voice`, `category`, `forum`, `stage_voice`, `news` |
| `position` | `int` | Position in list |
| `category_id` | `Optional[int]` | Parent category ID |
| `nsfw` | `bool` | NSFW flag |

**Filtered properties:**
- `guild.text_channels` -> `List[TextChannel]`
- `guild.voice_channels` -> `List[VoiceChannel]`
- `guild.categories` -> `List[CategoryChannel]`
- `guild.forums` -> `List[ForumChannel]`
- `guild.stage_channels` -> `List[StageChannel]`

---

## get_channel

**Tool params:** `channel_id: int`

### API Calls

```python
channel = bot.get_channel(channel_id)  # -> Optional[Union[abc.GuildChannel, Thread, abc.PrivateChannel]]
```

Returns the channel from cache. The return type depends on the channel:
- `TextChannel` -- text channels
- `VoiceChannel` -- voice channels
- `CategoryChannel` -- categories
- `ForumChannel` -- forum channels
- `StageChannel` -- stage channels
- `Thread` -- threads
- `DMChannel` -- DM channels

**Common attributes across channel types:**

| Attribute | Available on | Type |
|-----------|-------------|------|
| `id` | All | `int` |
| `name` | All guild channels | `str` |
| `type` | All | `ChannelType` |
| `guild` | Guild channels | `Guild` |
| `position` | Guild channels | `int` |
| `category_id` | Text, Voice, Forum, Stage | `Optional[int]` |
| `topic` | Text, Forum | `Optional[str]` |
| `slowmode_delay` | Text, Voice, Forum, Thread | `int` |
| `nsfw` | Text, Voice, Forum | `bool` |
| `bitrate` | Voice, Stage | `int` |
| `user_limit` | Voice, Stage | `int` |
| `jump_url` | All | `str` |
| `mention` | All guild channels | `str` |
| `created_at` | All | `datetime` |

---

## create_text_channel

**Tool params:** `guild_id: int`, `name: str`, `*, topic: str | None = None`, `category_id: int | None = None`, `slowmode_delay: int = 0`, `nsfw: bool = False`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)

# Get category object if specified
category = guild.get_channel(category_id) if category_id else None
```

#### `Guild.create_text_channel()`

```python
await guild.create_text_channel(
    name: str,
    *,
    reason: str = None,
    category: CategoryChannel = None,
    news: bool = False,
    position: int = ...,
    topic: str = ...,
    slowmode_delay: int = ...,          # 0-21600 seconds
    nsfw: bool = ...,
    overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
    default_auto_archive_duration: int = ...,   # 60/1440/4320/10080
    default_thread_slowmode_delay: int = ...,
) -> TextChannel
```

**Permissions:** `manage_channels`. If `category` is set, also needs `manage_channels` in that category.

**Returns:** The created `TextChannel`.

**Raises:** `Forbidden`, `HTTPException`, `InvalidArgument`.

---

## create_voice_channel

**Tool params:** `guild_id: int`, `name: str`, `*, category_id: int | None = None`, `bitrate: int | None = None`, `user_limit: int = 0`, `reason: str | None = None`

### API Calls

#### `Guild.create_voice_channel()`

```python
await guild.create_voice_channel(
    name: str,
    *,
    reason: str = None,
    category: CategoryChannel = None,
    position: int = ...,
    bitrate: int = ...,                 # In bits/sec. Default depends on guild tier
    user_limit: int = ...,              # 0 = unlimited, max 99
    rtc_region: str = ...,              # None = auto
    video_quality_mode: VideoQualityMode = ...,
    overwrites: Mapping = ...,
    nsfw: bool = ...,
) -> VoiceChannel
```

**Permissions:** `manage_channels`.

**Bitrate limits by tier:**
- No boost: 96000
- Tier 1: 128000
- Tier 2: 256000
- Tier 3: 384000

---

## create_category

**Tool params:** `guild_id: int`, `name: str`, `*, reason: str | None = None`

### API Calls

#### `Guild.create_category()`

```python
await guild.create_category(
    name: str,
    *,
    overwrites: Mapping[Union[Role, Member], PermissionOverwrite] = ...,
    reason: str = None,
    position: int = ...,
) -> CategoryChannel
```

**Permissions:** `manage_channels`.

---

## create_forum_channel

**Tool params:** `guild_id: int`, `name: str`, `*, topic: str | None = None`, `category_id: int | None = None`, `slowmode_delay: int = 0`, `nsfw: bool = False`, `reason: str | None = None`

### API Calls

#### `Guild.create_forum()`

```python
await guild.create_forum(
    name: str,
    *,
    topic: str = ...,                              # "Guidelines" in UI, up to 4096 chars
    position: int = ...,
    category: CategoryChannel = None,
    slowmode_delay: int = ...,                     # Between thread creation
    nsfw: bool = ...,
    media: bool = ...,                             # True creates a media channel
    overwrites: Mapping = ...,
    reason: str = None,
    default_auto_archive_duration: int = ...,
    default_thread_slowmode_delay: int = ...,
    default_sort_order: ForumOrderType = ...,
    default_reaction_emoji: PartialEmoji = ...,
    default_layout: ForumLayoutType = ...,
    available_tags: Sequence[ForumTag] = ...,
) -> ForumChannel
```

**Permissions:** `manage_channels`.

**Note:** Forum threads require a starter message. Use `ForumChannel.create_thread()` which returns `Tuple[Thread, Message]`.

---

## edit_channel

**Tool params:** `channel_id: int`, `*, name: str | None = None`, `topic: str | None = None`, `position: int | None = None`, `nsfw: bool | None = None`, `slowmode_delay: int | None = None`, `reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)
```

#### `abc.GuildChannel.edit()` / type-specific `.edit()`

The available parameters depend on the channel type:

**TextChannel.edit():**
```python
await channel.edit(
    *,
    reason: str = None,
    name: str = ...,
    topic: str = ...,
    position: int = ...,
    nsfw: bool = ...,
    sync_permissions: bool = ...,
    category: Optional[CategoryChannel] = ...,
    slowmode_delay: int = ...,          # 0-21600
    type: ChannelType = ...,            # Convert between text/news
    overwrites: Mapping = ...,
    default_auto_archive_duration: int = ...,
    default_thread_slowmode_delay: int = ...,
) -> Optional[TextChannel]
```

**VoiceChannel.edit():**
```python
await channel.edit(
    *,
    reason: str = None,
    name: str = ...,
    bitrate: int = ...,
    nsfw: bool = ...,
    user_limit: int = ...,
    position: int = ...,
    sync_permissions: bool = ...,
    category: Optional[CategoryChannel] = ...,
    slowmode_delay: int = ...,
    overwrites: Mapping = ...,
    rtc_region: Optional[str] = ...,
    video_quality_mode: VideoQualityMode = ...,
    status: Optional[str] = ...,        # Up to 500 chars
) -> Optional[VoiceChannel]
```

**CategoryChannel.edit():**
```python
await channel.edit(
    *,
    reason: str = None,
    name: str = ...,
    position: int = ...,
    nsfw: bool = ...,
    overwrites: Mapping = ...,
) -> Optional[CategoryChannel]
```

**ForumChannel.edit():**
```python
await channel.edit(
    *,
    reason: str = None,
    name: str = ...,
    topic: str = ...,
    position: int = ...,
    nsfw: bool = ...,
    sync_permissions: bool = ...,
    category: Optional[CategoryChannel] = ...,
    slowmode_delay: int = ...,
    overwrites: Mapping = ...,
    default_auto_archive_duration: int = ...,
    available_tags: Sequence[ForumTag] = ...,
    default_thread_slowmode_delay: int = ...,
    default_reaction_emoji: Optional[PartialEmoji] = ...,
    default_layout: ForumLayoutType = ...,
    default_sort_order: Optional[ForumOrderType] = ...,
    require_tag: bool = ...,
) -> Optional[ForumChannel]
```

**Permissions:** `manage_channels`.

**Returns:** `Optional[Channel]` -- the updated channel, or `None` if no changes were made.

---

## delete_channel

**Tool params:** `channel_id: int`, `*, reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)
```

#### `abc.GuildChannel.delete()`

```python
await channel.delete(*, reason: str = None)
```

**Permissions:** `manage_channels`.

**Raises:** `Forbidden`, `NotFound`, `HTTPException`.

**Warning:** This is irreversible. All messages and sub-channels (for categories) are lost.

---

## set_channel_permissions

**Tool params:** `channel_id: int`, `target_id: int`, `target_type: str` ("role" | "member"), `*, allow: list[str] | None = None`, `deny: list[str] | None = None`, `reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)

# Resolve target
if target_type == "role":
    target = channel.guild.get_role(target_id)
elif target_type == "member":
    target = channel.guild.get_member(target_id) or await channel.guild.fetch_member(target_id)
```

#### `abc.GuildChannel.set_permissions()`

```python
# Method 1: Using keyword arguments
await channel.set_permissions(
    target,                             # Union[Member, Role]
    *,
    reason: str = None,
    # Individual permission kwargs:
    send_messages=True,
    read_messages=True,
    # ... any permission name as kwarg
)

# Method 2: Using PermissionOverwrite object
overwrite = discord.PermissionOverwrite()
for perm in allow_list:
    setattr(overwrite, perm, True)
for perm in deny_list:
    setattr(overwrite, perm, False)

await channel.set_permissions(target, overwrite=overwrite, reason=reason)

# Method 3: Reset to default (remove overwrite)
await channel.set_permissions(target, overwrite=None, reason=reason)
```

**Permissions:** `manage_roles` in the channel.

**Notes:**
- Setting a permission to `None` in a `PermissionOverwrite` means "inherit" (no override).
- `True` = explicitly allow, `False` = explicitly deny.
- See [permissions_reference.md](permissions_reference.md) for all valid permission names.
