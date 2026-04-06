# Webhooks Tools -- discord.py API Reference

Tools in `discord_mcp/tools/webhooks.py` (5 tools).

---

## list_webhooks

**Tool params:** `*, channel_id: int | None = None`, `guild_id: int | None = None`

At least one of `channel_id` or `guild_id` is required. If both provided, `channel_id` takes priority.

### API Calls

#### Channel webhooks:

```python
channel = bot.get_channel(channel_id)
webhooks = await channel.webhooks()  # -> List[Webhook]
```

**Permissions:** `manage_webhooks` in the channel.

#### Guild webhooks:

```python
guild = bot.get_guild(guild_id)
webhooks = await guild.webhooks()  # -> List[Webhook]
```

**Permissions:** `manage_webhooks` guild-wide.

**Key Webhook attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Webhook ID |
| `type` | `WebhookType` | `incoming`, `channel_follower`, `application` |
| `token` | `Optional[str]` | Webhook token (None for non-incoming) |
| `name` | `Optional[str]` | Webhook name |
| `guild_id` | `Optional[int]` | Guild ID |
| `channel_id` | `Optional[int]` | Channel ID |
| `user` | `Optional[User]` | Creator |
| `url` | `str` | Full webhook URL (property) |
| `avatar` | `Optional[Asset]` | Webhook avatar |
| `created_at` | `datetime` | Creation timestamp |
| `source_guild` | `Optional[PartialWebhookGuild]` | For channel follower webhooks |
| `source_channel` | `Optional[PartialWebhookChannel]` | For channel follower webhooks |

---

## create_webhook

**Tool params:** `channel_id: int`, `name: str`, `*, reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)
```

#### `TextChannel.create_webhook()` / `VoiceChannel.create_webhook()` / `ForumChannel.create_webhook()`

```python
webhook = await channel.create_webhook(
    *,
    name: str,
    avatar: bytes = None,    # Avatar image bytes
    reason: str = None,
) -> Webhook
```

**Permissions:** `manage_webhooks` required.

**Notes:**
- Max 15 webhooks per channel.
- `name` cannot be "clyde" (case-insensitive).
- Webhook names must be 1-80 characters.

---

## send_webhook_message

**Tool params:** `webhook_id: int`, `content: str`, `*, username: str | None = None`, `avatar_url: str | None = None`, `thread_id: int | None = None`

### API Calls

```python
webhook = await bot.fetch_webhook(webhook_id)  # -> Webhook
```

#### `Webhook.send()`

```python
message = await webhook.send(
    content: str = ...,
    *,
    username: str = ...,            # Override display name
    avatar_url: Any = ...,          # Override avatar URL
    tts: bool = False,
    ephemeral: bool = False,        # Only for interaction webhooks
    file: File = ...,
    files: List[File] = ...,
    embed: Embed = ...,
    embeds: List[Embed] = ...,
    allowed_mentions: AllowedMentions = ...,
    view: View = ...,
    thread: Snowflake = ...,        # Send to a specific thread
    thread_name: str = ...,         # Create a new thread (ForumChannel only)
    wait: bool = False,             # If True, returns the Message
    suppress_embeds: bool = False,
    silent: bool = False,
    applied_tags: Sequence[ForumTag] = ...,
    poll: Poll = ...,
) -> Optional[WebhookMessage]
```

**Notes:**
- Set `wait=True` to get the created `WebhookMessage` back. Without it, returns `None`.
- `username` and `avatar_url` override the webhook's default name/avatar for this message only.
- `thread` sends the message to an existing thread. Pass `discord.Object(id=thread_id)`.
- `thread_name` creates a new thread in a `ForumChannel`. Mutually exclusive with `thread`.

**Usage:**
```python
kwargs = {"wait": True}
if username:
    kwargs["username"] = username
if avatar_url:
    kwargs["avatar_url"] = avatar_url
if thread_id:
    kwargs["thread"] = discord.Object(id=thread_id)

message = await webhook.send(content, **kwargs)
```

---

## edit_webhook

**Tool params:** `webhook_id: int`, `*, name: str | None = None`, `channel_id: int | None = None`, `reason: str | None = None`

### API Calls

```python
webhook = await bot.fetch_webhook(webhook_id)
```

#### `Webhook.edit()`

```python
webhook = await webhook.edit(
    *,
    reason: str = None,
    name: str = ...,
    avatar: bytes = ...,        # New avatar image bytes, None to remove
    channel: Snowflake = None,  # Move to different channel (requires auth)
    prefer_auth: bool = True,
) -> Webhook
```

**Notes:**
- Moving a webhook to a different channel (`channel` parameter) requires the webhook to be authenticated (fetched with bot token, not just token-based).
- `prefer_auth=True` (default) uses bot token authentication when available.

**Usage:**
```python
kwargs = {"reason": reason}
if name:
    kwargs["name"] = name
if channel_id:
    kwargs["channel"] = discord.Object(id=channel_id)

updated = await webhook.edit(**kwargs)
```

---

## delete_webhook

**Tool params:** `webhook_id: int`, `*, reason: str | None = None`

### API Calls

```python
webhook = await bot.fetch_webhook(webhook_id)
```

#### `Webhook.delete()`

```python
await webhook.delete(
    *,
    reason: str = None,
    prefer_auth: bool = True,
)
```

**Permissions:** `manage_webhooks` required (when using bot auth).

**Notes:**
- Webhook can also be deleted using just its token (no bot auth needed):
  ```python
  partial = discord.Webhook.partial(id=webhook_id, token=webhook_token, session=...)
  await partial.delete()
  ```
