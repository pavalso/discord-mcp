# Emojis & Stickers Tools -- discord.py API Reference

Tools in `discord_mcp/tools/emojis.py` (8 tools).

---

## list_emojis

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.emojis` (property)

```python
emojis = guild.emojis  # -> Tuple[Emoji, ...]
```

Returns cached emojis. For fresh data:
```python
emojis = await guild.fetch_emojis()  # -> List[Emoji]
```

**Key Emoji attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Emoji ID |
| `name` | `str` | Emoji name |
| `animated` | `bool` | Whether animated (GIF) |
| `available` | `bool` | Whether usable (may be False if guild lost boost level) |
| `managed` | `bool` | Managed by Twitch integration |
| `require_colons` | `bool` | Must use colons in client |
| `guild_id` | `int` | Owning guild ID |
| `url` | `str` | CDN URL (property) |
| `roles` | `List[Role]` | Roles that can use this emoji (empty = everyone) |
| `user` | `Optional[User]` | Creator (only via `fetch_emoji`, needs `manage_emojis`) |
| `created_at` | `datetime` | Creation timestamp |

**String representation:**
- Static: `<:name:id>` 
- Animated: `<a:name:id>`

---

## create_emoji

**Tool params:** `guild_id: int`, `name: str`, `image_url: str`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

**Step 1: Fetch image bytes from URL:**
```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get(image_url) as resp:
        image_data = await resp.read()  # -> bytes
```

#### `Guild.create_custom_emoji()`

```python
emoji = await guild.create_custom_emoji(
    *,
    name: str,
    image: bytes,                   # Image data (JPG, PNG, GIF only)
    roles: List[Role] = ...,        # Roles that can use this emoji
    reason: str = None,
) -> Emoji
```

**Permissions:** `manage_emojis` (or `manage_expressions`) required.

**Limits:**
- Max 50 static + 50 animated emojis (base)
- With `MORE_EMOJI` feature (boost level): up to 200 each
- Image must be under 256 KB
- Supported formats: JPG, PNG, GIF (animated = GIF)
- Name must be at least 2 characters, alphanumeric + underscores

**Raises:** `Forbidden`, `HTTPException`, `InvalidArgument`.

---

## delete_emoji

**Tool params:** `guild_id: int`, `emoji_id: int`, `*, reason: str | None = None`

### API Calls

#### Option 1: Using `Guild.delete_emoji()`

```python
guild = bot.get_guild(guild_id)
await guild.delete_emoji(discord.Object(id=emoji_id), reason=reason)
```

#### Option 2: Using `Emoji.delete()`

```python
emoji = await guild.fetch_emoji(emoji_id)
await emoji.delete(reason=reason)
```

**Permissions:** `manage_emojis` (or `manage_expressions`) required.

**Raises:** `Forbidden`, `HTTPException`.

---

## list_stickers

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.stickers` (property)

```python
stickers = guild.stickers  # -> Tuple[GuildSticker, ...]
```

For fresh data:
```python
stickers = await guild.fetch_stickers()  # -> List[GuildSticker]
```

**Key GuildSticker attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Sticker ID |
| `name` | `str` | Sticker name |
| `description` | `str` | Sticker description |
| `emoji` | `str` | Related emoji name (for autosuggestion) |
| `format` | `StickerFormatType` | `png`, `apng`, `lottie`, `gif` |
| `available` | `bool` | Whether usable |
| `guild_id` | `int` | Owning guild ID |
| `user` | `Optional[User]` | Creator |
| `url` | `str` | CDN URL (property) |
| `created_at` | `datetime` | Creation timestamp |

---

## delete_sticker

**Tool params:** `guild_id: int`, `sticker_id: int`, `*, reason: str | None = None`

### API Calls

#### Option 1: Using `Guild.delete_sticker()`

```python
guild = bot.get_guild(guild_id)
await guild.delete_sticker(discord.Object(id=sticker_id), reason=reason)
```

#### Option 2: Using `GuildSticker.delete()`

```python
sticker = await guild.fetch_sticker(sticker_id)
await sticker.delete(reason=reason)
```

**Permissions:** `manage_emojis_and_stickers` (or `manage_expressions`) required.

**Raises:** `Forbidden`, `HTTPException`.

---

## edit_emoji

**Tool params:** `guild_id: str`, `emoji_id: str`, `*, name: str | None = None`, `role_ids: list[str] | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(int(guild_id))
emoji = await guild.fetch_emoji(int(emoji_id))
```

#### `Emoji.edit()`

```python
emoji = await emoji.edit(
    *,
    name: str = MISSING,                # 2-32 characters
    roles: Sequence[Snowflake] = MISSING,
    reason: str | None = None,
) -> Emoji
```

**Permissions:** `manage_expressions` required.

**Notes:**
- Only the fields given are sent, so a rename does not clear an existing role
  restriction.
- `role_ids` resolves each ID through the guild, raising
  `Role {id} not found in guild {guild}.` for an unknown one rather than
  silently dropping it.
- An **empty** `role_ids` list clears the restriction and makes the emoji usable
  by everyone; omitting the argument leaves the restriction as it is.
- The emoji image cannot be changed. Delete and recreate instead.

---

## create_sticker

**Tool params:** `guild_id: str`, `name: str`, `description: str`, `emoji: str`, `image_url: str`, `*, reason: str | None = None`

### API Calls

The image is downloaded with `aiohttp`, then wrapped in a `discord.File`:

```python
async with aiohttp.ClientSession() as session, session.get(image_url) as resp:
    image_data = await resp.read()
```

#### `Guild.create_sticker()`

```python
sticker = await guild.create_sticker(
    *,
    name: str,                          # 2-30 characters
    description: str,                   # 2-100 characters
    emoji: str,                         # Unicode emoji acting as the tag
    file: File,
    reason: str | None = None,
) -> GuildSticker
```

**Permissions:** `manage_expressions` required.

**Notes:**
- Unlike `create_emoji`, which takes raw `bytes`, this needs a `discord.File`;
  the downloaded bytes are wrapped in `io.BytesIO`.
- Discord limits: PNG, APNG, GIF or Lottie, at most 512KB, exactly 320x320.
- `emoji` is a unicode emoji (`"😀"`), not the name of a custom one.
- Sticker slots are limited by the guild's boost tier (5 at tier 0).

**Raises:** `Forbidden`, `HTTPException` (bad image, or slots full).

---

## edit_sticker

**Tool params:** `guild_id: str`, `sticker_id: str`, `*, name: str | None = None`, `description: str | None = None`, `emoji: str | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(int(guild_id))
sticker = await guild.fetch_sticker(int(sticker_id))
```

#### `GuildSticker.edit()`

```python
sticker = await sticker.edit(
    *,
    name: str = MISSING,                # 2-30 characters
    description: str = MISSING,         # Empty, or 2-100 characters
    emoji: str = MISSING,               # Unicode emoji tag
    reason: str | None = None,
) -> GuildSticker
```

**Permissions:** `manage_expressions` required.

**Notes:**
- Only the fields given are sent, so editing the description leaves the name and
  emoji tag alone.
- The sticker image cannot be changed. Delete and recreate instead.
