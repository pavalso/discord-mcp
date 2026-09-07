# Voice Tools -- discord.py API Reference

Tools in `discord_mcp/tools/voice.py` (9 tools).

Unlike the other modules, voice was documented after implementation, so the
**Tool params** below are the real signatures: snowflakes are passed as `str`.

---

## Runtime requirements

Voice is the only part of this server that needs more than `discord.py` itself.

| Requirement | Why | Install |
|-------------|-----|---------|
| `PyNaCl` | Encrypts the RTP voice packets. Without it `VoiceChannel.connect()` raises `RuntimeError`. | `pip install PyNaCl` (already a project dependency) |
| `davey` | discord.py's DAVE (end-to-end encryption) binding. Recent discord.py refuses to open a voice connection without it and logs `davey is not installed, voice will NOT be supported` at startup. | `pip install davey` (already a project dependency) |
| FFmpeg | Decodes the audio source and transcodes it to the PCM discord.py sends. **Not pip-installable** -- it is a system binary. | See below |

FFmpeg must be on `PATH`, or its full path given in the `DISCORD_MCP_FFMPEG`
environment variable:

```bash
# Windows
winget install Gyan.FFmpeg          # or: choco install ffmpeg
# macOS
brew install ffmpeg
# Debian/Ubuntu
sudo apt install ffmpeg

# Not on PATH? Point at it directly:
export DISCORD_MCP_FFMPEG="C:/tools/ffmpeg/bin/ffmpeg.exe"
```

`_build_audio_source()` checks for the binary with `shutil.which()` before
spawning it, so a missing FFmpeg surfaces as a clear error from `play_audio`
rather than a silent failure inside the player thread.

### Intents

No privileged intent is needed. `voice_states` is part of
`discord.Intents.default()`, so the bot in `discord_mcp/bot.py` already receives
the voice state updates that keep `Guild.voice_client` and `Member.voice`
accurate.

---

## join_voice

**Tool params:** `channel_id: str`, `*, self_mute: bool = False`, `self_deaf: bool = True`

### API Calls

```python
channel = bot.get_channel(int(channel_id))   # VoiceChannel or StageChannel
```

#### `VoiceChannel.connect()`

```python
voice_client = await channel.connect(
    *,
    timeout: float = 30.0,
    reconnect: bool = True,
    self_mute: bool = False,
    self_deaf: bool = False,
) -> VoiceClient
```

**Permissions:** `connect` on the target channel (plus `speak` to later transmit).

#### `VoiceClient.move_to()` -- when already connected in the guild

```python
await voice_client.move_to(channel)          # -> None
```

**Notes:**
- One voice connection per guild. If the bot is already connected in the guild,
  the tool calls `move_to()` and returns `"moved": True` instead of opening a
  second connection.
- `move_to()` carries **no** voice-state flags -- the gateway resets the bot to
  unmuted/undeafened. The tool therefore follows it with
  `Guild.change_voice_state(channel=..., self_mute=..., self_deaf=...)` so the
  requested flags survive a move.
- `self_deaf` defaults to `True`: the bot has no use for inbound audio (this
  server does not implement voice receive) and deafening reduces bandwidth.
- Stage channels connect the same way, but the bot joins as an audience member.
  Speaking requires `StageChannel` moderator permissions and
  `Guild.me.edit(suppress=False)`, which this tool does not do.

**Raises:** `ValueError` (channel not in cache, or not a voice/stage channel),
`RuntimeError` (PyNaCl/davey missing -- re-raised with install instructions),
`asyncio.TimeoutError`, `discord.ClientException` (already connected).

---

## set_voice_state

**Tool params:** `guild_id: str`, `*, self_mute: bool | None = None`, `self_deaf: bool | None = None`

### API Calls

#### `Guild.change_voice_state()`

```python
await guild.change_voice_state(
    *,
    channel: abc.Snowflake | None,           # None disconnects
    self_mute: bool = False,
    self_deaf: bool = False,
) -> None
```

**Notes:**
- Both flags are optional, but at least one must be given.
- `change_voice_state()` sends an absolute state, not a patch, so the tool reads
  the current flags off `Guild.me.voice` and re-sends the unchanged one.
- The bot's own state lives on `Guild.me.voice` (a `VoiceState`); it is `None`
  when the bot is not in a channel.
- `self_mute`/`self_deaf` are the bot's own choice. The server-side `mute`/`deaf`
  set by a moderator is a different pair of flags -- change those with
  `edit_member` from `tools/members.py`.

---

## leave_voice

**Tool params:** `guild_id: str`

### API Calls

```python
guild = bot.get_guild(int(guild_id))
voice_client = guild.voice_client
```

#### `VoiceClient.disconnect()`

```python
await voice_client.disconnect(*, force: bool = False) -> None
```

**Notes:**
- `force=False` closes the websocket cleanly and stops any playback first.
  `force=True` tears the connection down even if the handshake is wedged.
- Disconnecting stops playback; there is no need to call `stop_audio` first.

**Raises:** `ValueError` (guild not cached, or no active connection).

---

## voice_status

**Tool params:** `*, guild_id: str | None = None`

### API Calls

```python
guild.voice_client                           # Optional[VoiceClient] -- one guild
bot.voice_clients                            # List[VoiceProtocol]  -- every guild
```

**Key VoiceClient attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `channel` | `VoiceChannel` / `StageChannel` | Channel currently connected to |
| `guild` | `Guild` | Guild the connection belongs to |
| `latency` | `float` | Websocket latency in **seconds** (reported as `latency_ms`) |
| `average_latency` | `float` | Average of recent heartbeat latencies |
| `source` | `Optional[AudioSource]` | Audio currently loaded |
| `is_connected()` | `bool` | Whether the voice websocket is up |
| `is_playing()` | `bool` | Audio is actively being sent |
| `is_paused()` | `bool` | Audio is loaded but suspended |

**Notes:**
- With `guild_id`, returns a single connection dict, or `{"connected": false,
  "guild_id": ...}` when the bot is not in voice there -- not an error.
- Without `guild_id`, returns `{"connection_count": n, "connections": [...]}`.
- The reported `source` is the original path/URL, stashed on the
  `PCMVolumeTransformer` as `mcp_source_label` when playback started;
  discord.py itself does not retain it.

---

## play_audio

**Tool params:** `guild_id: str`, `source: str`, `*, volume: float = 1.0`, `replace: bool = False`

### API Calls

#### `discord.FFmpegPCMAudio`

```python
audio = discord.FFmpegPCMAudio(
    source,                                  # File path, URL, or file-like object
    *,
    executable: str = "ffmpeg",
    pipe: bool = False,
    stderr: IO[bytes] = None,
    before_options: str = None,              # ffmpeg args BEFORE -i
    options: str = None,                     # ffmpeg args AFTER -i
)
```

#### `discord.PCMVolumeTransformer`

```python
audio = discord.PCMVolumeTransformer(original, volume=1.0)
audio.volume = 0.5                           # Adjustable while playing
```

#### `VoiceClient.play()`

```python
voice_client.play(
    source: AudioSource,
    *,
    after: Callable[[Optional[Exception]], None] = None,
) -> None
```

**Permissions:** `speak` on the connected channel.

**Notes:**
- `play()` is **not** a coroutine. It returns immediately and streams from a
  separate thread; the tool reports that playback started, not that it finished.
- The `after` callback also runs on that thread, off the event loop, so it must
  not touch discord.py state. `_on_playback_finished()` only logs.
- http(s) sources get `-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5`
  as `before_options` so a dropped stream is retried instead of ending playback.
- Sources that are neither an existing file nor an http(s) URL are rejected up
  front, rather than failing inside the player thread where the error would only
  reach the log.
- Playing while audio is active raises unless `replace=True`, which calls
  `stop()` first. discord.py would otherwise raise `ClientException`.
- `volume` is validated against `MIN_VOLUME`/`MAX_VOLUME` (0.0--2.0). Above 1.0
  amplifies and can clip.

**Raises:** `ValueError` (no connection, bad source, already playing without
`replace`, volume out of range), `RuntimeError` (FFmpeg not found).

---

## stop_audio

**Tool params:** `guild_id: str`

### API Calls

```python
voice_client.stop() -> None
```

**Notes:**
- Discards the source; playback cannot be resumed afterwards. Use `pause_audio`
  to keep it.
- Errors when nothing is playing or paused, rather than silently succeeding.
- The connection stays open -- use `leave_voice` to close it.

---

## pause_audio

**Tool params:** `guild_id: str`

### API Calls

```python
voice_client.pause() -> None
```

**Notes:**
- Keeps the `AudioSource` loaded so `resume_audio` can continue it.
- Requires audio to be actively playing (`is_playing()`); pausing when already
  paused is an error.
- For an FFmpeg stream, pausing does not pause the remote source -- a live
  stream will have moved on by the time it resumes.

---

## resume_audio

**Tool params:** `guild_id: str`

### API Calls

```python
voice_client.resume() -> None
```

**Notes:** Requires `is_paused()`; resuming a connection that is not paused is
an error.

---

## set_volume

**Tool params:** `guild_id: str`, `volume: float`

### API Calls

```python
source = voice_client.source                 # Must be a PCMVolumeTransformer
source.volume = volume
```

**Notes:**
- Applies to the audio already playing; it does not persist to the next
  `play_audio` call, which takes its own `volume`.
- Only works because `play_audio` wraps every source in a
  `PCMVolumeTransformer`. A raw `FFmpegPCMAudio` (or an `FFmpegOpusAudio`, which
  cannot be volume-transformed at all) is rejected with a clear error.
- Same 0.0--2.0 range as `play_audio`.

---

## Not implemented

| Capability | Why |
|------------|-----|
| Voice receive / recording | discord.py has no supported receive API; it needs a third-party extension. |
| Playback queues | Each connection holds one source at a time. Queueing would need state and an `after` callback that schedules onto the event loop. |
| Seek / track position | `AudioSource` exposes no position. Seeking means re-spawning FFmpeg with `-ss`. |
| Stage speaker promotion | The bot joins a stage as audience. Speaking needs `Guild.me.edit(suppress=False)` plus stage moderator permissions. |
| Soundboard | Not covered by this module. |
