# Threads Tools -- discord.py API Reference

Tools in `discord_mcp/tools/threads.py` (8 tools).

---

## create_thread

**Tool params:** `channel_id: int`, `name: str`, `*, message_id: int | None = None`, `auto_archive_duration: int = 1440`, `slowmode_delay: int = 0`, `reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)  # -> TextChannel or ForumChannel
```

#### `TextChannel.create_thread()`

```python
await channel.create_thread(
    *,
    name: str,
    message: Snowflake = None,         # Attach thread to this message
    auto_archive_duration: int = ...,   # 60, 1440, 4320, or 10080 minutes
    type: ChannelType = None,           # public_thread or private_thread
    reason: str = None,
    invitable: bool = True,             # For private threads: allow non-mods to invite
    slowmode_delay: int = None,         # 0-21600 seconds
) -> Thread
```

**Permissions:**
- Creating from a message: `create_public_threads`
- Without a message: `create_public_threads` (public) or `create_private_threads` (private)

**Notes:**
- If `message` is provided, creates a thread attached to that message. The thread inherits the message's channel.
- `auto_archive_duration` valid values: 60 (1 hour), 1440 (1 day), 4320 (3 days), 10080 (7 days). Some values require guild boosts.
- Threads created from a message have the same ID as the message.

#### `ForumChannel.create_thread()` (different return type!)

```python
result = await channel.create_thread(
    *,
    name: str,
    auto_archive_duration: int = ...,
    slowmode_delay: int = None,
    content: str = None,                # At least one of content/embed/file required
    tts: bool = False,
    embed: Embed = None,
    embeds: List[Embed] = None,
    file: File = None,
    files: List[File] = None,
    allowed_mentions: AllowedMentions = None,
    applied_tags: Sequence[ForumTag] = ...,
    view: View = None,
    suppress_embeds: bool = False,
    silent: bool = False,
    reason: str = None,
) -> Tuple[Thread, Message]  # Named tuple with .thread and .message
```

**Important:** Forum threads MUST include starter content (content, embed, or file).

**Usage for message_id parameter:**
```python
if message_id:
    ref = discord.Object(id=message_id)
    thread = await channel.create_thread(name=name, message=ref, ...)
else:
    thread = await channel.create_thread(name=name, ...)
```

---

## edit_thread

**Tool params:** `thread_id: int`, `*, name: str | None = None`, `archived: bool | None = None`, `locked: bool | None = None`, `slowmode_delay: int | None = None`, `auto_archive_duration: int | None = None`, `reason: str | None = None`

### API Calls

```python
thread = bot.get_channel(thread_id)  # -> Thread
```

#### `Thread.edit()`

```python
await thread.edit(
    *,
    name: str = ...,
    archived: bool = ...,
    locked: bool = ...,                 # Locked threads can't be unarchived by non-mods
    invitable: bool = ...,              # Private threads only
    pinned: bool = ...,                 # Pin in a forum channel
    slowmode_delay: int = ...,
    auto_archive_duration: int = ...,   # 60/1440/4320/10080
    applied_tags: Sequence[ForumTag] = ...,
    reason: str = None,
) -> Thread
```

**Permissions:** `manage_threads` required. Thread creator can edit `name`, `archived`, and `auto_archive_duration` without this permission.

**Returns:** The edited `Thread`.

---

## delete_thread

**Tool params:** `thread_id: int`, `*, reason: str | None = None`

### API Calls

```python
thread = bot.get_channel(thread_id)
```

#### `Thread.delete()`

```python
await thread.delete(*, reason: str = None)
```

**Permissions:** `manage_threads` required.

---

## list_active_threads

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.active_threads()`

```python
threads = await guild.active_threads()  # -> List[Thread]
```

Returns all active (non-archived) threads the bot can access. This is an API call, not cache-based.

**Key Thread attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Thread ID |
| `name` | `str` | Thread name |
| `parent_id` | `int` | Parent channel ID |
| `owner_id` | `int` | Creator's user ID |
| `archived` | `bool` | Whether archived |
| `locked` | `bool` | Whether locked |
| `auto_archive_duration` | `int` | Minutes until auto-archive |
| `archive_timestamp` | `datetime` | When last archived/created |
| `message_count` | `int` | Approximate message count |
| `member_count` | `int` | Member count (caps at 50) |
| `slowmode_delay` | `int` | Slowmode in seconds |
| `type` | `ChannelType` | `public_thread`, `private_thread`, `news_thread` |
| `created_at` | `Optional[datetime]` | Creation time (None for threads before Jan 9 2022) |

**Properties:**
- `parent` -> `Optional[Union[ForumChannel, TextChannel]]`
- `owner` -> `Optional[Member]`
- `applied_tags` -> `List[ForumTag]` (forum threads only)

---

## join_thread

**Tool params:** `thread_id: int`

### API Calls

```python
thread = bot.get_channel(thread_id)
```

#### `Thread.join()`

```python
await thread.join()
```

**Permissions:** `send_messages_in_threads`. For private threads, also needs `manage_threads` or an invitation.

---

## leave_thread

**Tool params:** `thread_id: int`

### API Calls

```python
thread = bot.get_channel(thread_id)
```

#### `Thread.leave()`

```python
await thread.leave()
```

No special permissions required.

---

## add_thread_member

**Tool params:** `thread_id: int`, `user_id: int`

### API Calls

```python
thread = bot.get_channel(thread_id)
user = discord.Object(id=user_id)
```

#### `Thread.add_user()`

```python
await thread.add_user(user)  # user: Snowflake
```

**Permissions:** `send_messages_in_threads` required. The thread must not be archived.

---

## remove_thread_member

**Tool params:** `thread_id: int`, `user_id: int`

### API Calls

```python
thread = bot.get_channel(thread_id)
user = discord.Object(id=user_id)
```

#### `Thread.remove_user()`

```python
await thread.remove_user(user)  # user: Snowflake
```

**Permissions:** `manage_threads` required, or the bot must be the thread creator.
