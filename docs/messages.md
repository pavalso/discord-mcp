# Messages Tools -- discord.py API Reference

Tools in `discord_mcp/tools/messages.py` (11 tools).

---

## send_message

**Tool params:** `channel_id: int`, `content: str`, `*, tts: bool = False`, `reply_to_message_id: int | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)  # -> Optional[Union[TextChannel, VoiceChannel, Thread, ...]]
```

#### `Messageable.send()`

```python
await channel.send(
    content: str = None,
    *,
    tts: bool = False,
    embed: Embed = None,
    embeds: List[Embed] = None,
    file: File = None,
    files: List[File] = None,
    stickers: Sequence[Union[GuildSticker, StickerItem]] = None,
    delete_after: float = None,
    nonce: Union[str, int] = None,
    allowed_mentions: AllowedMentions = None,
    reference: Union[Message, MessageReference, PartialMessage] = None,
    mention_author: bool = None,
    view: View = None,
    suppress_embeds: bool = False,
    silent: bool = False,
    poll: Poll = None,
) -> Message
```

**Permissions:** `send_messages` in the channel. `send_tts_messages` for TTS.

**For replies:** Use `reference` parameter:
```python
# Create reference from message ID
ref = discord.MessageReference(message_id=reply_to_message_id, channel_id=channel_id)
await channel.send(content, reference=ref)

# Or fetch the message first
msg = await channel.fetch_message(reply_to_message_id)
await channel.send(content, reference=msg)
```

**Returns:** `Message` object with attributes:
- `id` (int), `content` (str), `author` (Member/User), `channel`, `guild`
- `created_at` (datetime), `edited_at` (Optional[datetime])
- `tts` (bool), `pinned` (bool), `type` (MessageType)
- `embeds` (List[Embed]), `attachments` (List[Attachment])
- `reactions` (List[Reaction]), `mentions` (List[User])
- `jump_url` (str)

---

## edit_message

**Tool params:** `channel_id: int`, `message_id: int`, `content: str`

### API Calls

```python
channel = bot.get_channel(channel_id)
message = await channel.fetch_message(message_id)
```

#### `Message.edit()`

```python
await message.edit(
    *,
    content: str = ...,
    embed: Embed = ...,
    embeds: List[Embed] = ...,
    attachments: List[Attachment] = ...,
    suppress: bool = False,
    delete_after: float = None,
    allowed_mentions: AllowedMentions = ...,
    view: View = ...,
) -> Message
```

**Permissions:** Can only edit own messages' content. `manage_messages` needed to suppress embeds on others' messages.

**Returns:** The edited `Message`.

---

## delete_message

**Tool params:** `channel_id: int`, `message_id: int`

### API Calls

```python
channel = bot.get_channel(channel_id)
message = await channel.fetch_message(message_id)
```

#### `Message.delete()`

```python
await message.delete(*, delay: float = None)
```

**Permissions:** No permission needed for own messages. `manage_messages` required for others' messages.

---

## get_message

**Tool params:** `channel_id: int`, `message_id: int`

### API Calls

#### `Messageable.fetch_message()`

```python
message = await channel.fetch_message(message_id)  # -> Message
```

**Permissions:** `read_message_history` required.

**Raises:** `NotFound` (message deleted or invalid ID), `Forbidden`, `HTTPException`.

**Key Message attributes to serialize:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Message ID |
| `content` | `str` | Text content (empty without `message_content` intent) |
| `author.id` | `int` | Author's user ID |
| `author.name` | `str` | Author's username |
| `channel.id` | `int` | Channel ID |
| `created_at` | `datetime` | Creation timestamp (UTC) |
| `edited_at` | `Optional[datetime]` | Last edit timestamp |
| `pinned` | `bool` | Whether pinned |
| `tts` | `bool` | Whether TTS |
| `type` | `MessageType` | Message type |
| `attachments` | `List[Attachment]` | File attachments |
| `embeds` | `List[Embed]` | Embedded content |
| `reactions` | `List[Reaction]` | Reactions on the message |
| `jump_url` | `str` | URL to jump to message |

---

## get_message_history

**Tool params:** `channel_id: int`, `*, limit: int = 50`, `before_message_id: int | None = None`, `after_message_id: int | None = None`

### API Calls

#### `Messageable.history()`

```python
async for message in channel.history(
    *,
    limit: int = 100,
    before: Union[Snowflake, datetime] = None,
    after: Union[Snowflake, datetime] = None,
    around: Union[Snowflake, datetime] = None,
    oldest_first: bool = None,
) -> AsyncIterator[Message]
```

**Permissions:** `read_message_history` required.

**Usage with IDs:**
```python
# Convert message IDs to Object for before/after
messages = []
kwargs = {"limit": limit}
if before_message_id:
    kwargs["before"] = discord.Object(id=before_message_id)
if after_message_id:
    kwargs["after"] = discord.Object(id=after_message_id)

async for msg in channel.history(**kwargs):
    messages.append(msg)
```

**Notes:**
- `oldest_first` defaults to `True` when `after` is specified, `False` otherwise.
- `around` returns up to `limit` messages around the target (not compatible with `before`/`after`).

---

## pin_message

**Tool params:** `channel_id: int`, `message_id: int`

### API Calls

```python
message = await channel.fetch_message(message_id)
```

#### `Message.pin()`

```python
await message.pin(*, reason: str = None)
```

**Permissions:** `manage_messages` required. Max **50 pins** per channel.

**Raises:** `Forbidden`, `NotFound`, `HTTPException`.

---

## unpin_message

**Tool params:** `channel_id: int`, `message_id: int`

### API Calls

```python
message = await channel.fetch_message(message_id)
```

#### `Message.unpin()`

```python
await message.unpin(*, reason: str = None)
```

**Permissions:** `manage_messages` required.

---

## get_pinned_messages

**Tool params:** `channel_id: int`

### API Calls

#### `Messageable.pins()`

```python
# Async iterator (v2.6+)
pinned = []
async for msg in channel.pins():
    pinned.append(msg)
```

**Permissions:** `view_channel` and `read_message_history`.

**Note:** Each `Message` returned has `pinned_at` property set (only available from `pins()`). Parameters: `limit=50`, `before=None`, `oldest_first=False`.

---

## add_reaction

**Tool params:** `channel_id: int`, `message_id: int`, `emoji: str`

### API Calls

```python
message = await channel.fetch_message(message_id)
```

#### `Message.add_reaction()`

```python
await message.add_reaction(emoji)  # emoji: Union[Emoji, Reaction, PartialEmoji, str]
```

**Permissions:** `read_message_history` required. `add_reactions` required if no one has reacted with this emoji yet.

**Emoji formats:**
- Unicode: `"\U0001f44d"` or `"\N{THUMBS UP SIGN}"` or `"👍"`
- Custom: `"<:name:id>"` or `"<a:name:id>"` (animated)
- `discord.PartialEmoji(name="name", id=123456)`

---

## remove_reaction

**Tool params:** `channel_id: int`, `message_id: int`, `emoji: str`, `*, user_id: int | None = None`

### API Calls

```python
message = await channel.fetch_message(message_id)
```

#### `Message.remove_reaction()`

```python
await message.remove_reaction(emoji, member)  # member: Union[Member, abc.Snowflake]
```

**Permissions:**
- Removing own reaction: no special permission needed
- Removing others' reactions: `manage_messages` required

**Usage:**
```python
if user_id:
    user = discord.Object(id=user_id)
    await message.remove_reaction(emoji, user)
else:
    await message.remove_reaction(emoji, bot.user)
```

---

## clear_reactions

**Tool params:** `channel_id: int`, `message_id: int`, `*, emoji: str | None = None`

### API Calls

```python
message = await channel.fetch_message(message_id)
```

#### `Message.clear_reactions()` / `Message.clear_reaction()`

```python
# Clear ALL reactions
await message.clear_reactions()

# Clear reactions for a specific emoji
await message.clear_reaction(emoji)  # emoji: Union[Emoji, Reaction, PartialEmoji, str]
```

**Permissions:** `manage_messages` required for both.
