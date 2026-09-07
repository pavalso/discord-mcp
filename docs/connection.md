# Connection Tools -- discord.py API Reference

Tools defined directly in `discord_mcp/server.py` (4 tools), not in a
`tools/` module. These manage the bot's lifecycle rather than a Discord
resource, so every other tool depends on `connect` having run first.

---

## connect

**Tool params:** `token: str | None = None`

### API Calls

Delegates to `start_bot()` in `discord_mcp/bot.py`:

```python
bot = commands.Bot(command_prefix="!", intents=intents)
asyncio.create_task(bot.start(token))        # Runs in the background
await asyncio.wait_for(ready_event.wait(), timeout=30)
```

**Notes:**
- The token falls back to the `DISCORD_BOT_TOKEN` environment variable. Passing
  it as a parameter puts the token in the MCP conversation -- prefer the env var.
- `bot.start()` never returns while connected, so it runs as a background task.
  The tool waits on an `on_ready` event instead, with a 30-second timeout.
- Calling `connect` while already connected returns the existing bot rather than
  opening a second gateway session.
- Missing token returns an error **string**, not an exception, so the LLM sees
  actionable text.

### Intents

`discord_mcp/bot.py` enables `Intents.default()` plus two privileged intents:

| Intent | Privileged | Needed for |
|--------|------------|------------|
| `message_content` | Yes | Reading `Message.content` in `get_message`, `get_message_history` |
| `members` | Yes | `guild.get_member()`, `list_members`, `search_members` |
| `voice_states` | No (in `default()`) | `Guild.voice_client`, `Member.voice` -- see [voice.md](voice.md) |

Both privileged intents must also be toggled on in the Discord Developer Portal
(Bot -> Privileged Gateway Intents), or `connect` fails with
`PrivilegedIntentsRequired`.

**Raises:** `RuntimeError` (not ready within 30 seconds),
`discord.LoginFailure` (bad token), `discord.PrivilegedIntentsRequired`.

---

## disconnect

**Tool params:** none

### API Calls

```python
await bot.close()                            # Closes the gateway websocket
task.cancel()                                # Cancels the background start task
```

**Notes:**
- Closing the client also tears down any open voice connections.
- Safe to call when not connected; the module-level bot is simply `None`.
- After disconnecting, every other tool raises until `connect` runs again.

---

## bot_status

**Tool params:** none

### API Calls

```python
bot.user                                     # ClientUser
bot.guilds                                   # List[Guild]
bot.latency                                  # float, seconds
```

**Returns:** `{"connected": false}` when the bot is not running, otherwise
`user`, `user_id`, `guild_count`, and `latency_ms`.

**Notes:**
- Never raises -- it catches the `RuntimeError` from `get_bot()` and reports
  `connected: false`. This makes it the safe tool to probe with first.
- `bot.latency` is the gateway heartbeat in **seconds**; the tool reports
  milliseconds.

---

## change_presence

**Tool params:** `*, status: str | None = None`, `activity_type: str | None = None`, `activity_name: str | None = None`

### API Calls

#### `Client.change_presence()`

```python
await bot.change_presence(
    *,
    activity: BaseActivity | None = None,
    status: Status | None = None,
) -> None
```

**Accepted `status` values** (mapped to `discord.Status`):

| Value | Shows as |
|-------|----------|
| `online` | Green. The default when status is `None`. |
| `idle` | Yellow |
| `dnd` | Red (do not disturb) |
| `invisible` | Offline to others; the bot stays connected |

**Accepted `activity_type` values** (mapped to `discord.ActivityType`):

| Value | Renders as |
|-------|------------|
| `playing` | Playing *name* |
| `streaming` | Streaming *name* |
| `listening` | Listening to *name* |
| `watching` | Watching *name* |
| `competing` | Competing in *name* |

**Notes:**
- `activity_name` is required whenever `activity_type` is given; the pair is
  meaningless apart.
- Both arguments are optional. Calling with neither clears the presence back to
  the default.
- Invalid values return an error string naming the valid options, rather than
  raising -- the LLM can correct itself from the message.
- `streaming` renders as a plain activity here. A clickable stream needs
  `discord.Streaming(name=..., url=...)` with a Twitch/YouTube URL, which this
  tool does not expose.
- Presence is global to the bot, not per-guild, and Discord rate-limits presence
  updates (roughly 5 per 20 seconds per session).
