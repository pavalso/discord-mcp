# Emojis & Stickers Tools -- discord.py API Reference

Tools in `discord_mcp/tools/emojis.py` (5 tools).

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

## Additional Reference: Editing Emojis/Stickers

Not currently a tool, but available if needed:

```python
# Edit emoji
emoji = await guild.fetch_emoji(emoji_id)
await emoji.edit(name="new_name", roles=[role1, role2], reason="rename")

# Edit sticker
sticker = await guild.fetch_sticker(sticker_id)
await sticker.edit(
    name="new_name",                    # 2-30 characters
    description="new description",      # Empty or 2-100 characters
    emoji="smile",                      # Related emoji name
    reason="update",
)
```
