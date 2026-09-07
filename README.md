# Discord MCP Server

[![CI](https://github.com/pavalso/discord-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/pavalso/discord-mcp/actions/workflows/ci.yml)

An [MCP](https://modelcontextprotocol.io) server that exposes Discord bot
operations as tools, so an MCP client (Claude Code, Claude Desktop, or anything
else speaking the protocol) can manage a Discord server directly.

92 tools across 12 domains, built on [discord.py](https://discordpy.readthedocs.io)
and the [`mcp`](https://github.com/modelcontextprotocol/python-sdk) SDK.

## Requirements

| | |
|---|---|
| Python | 3.12 or newer |
| A Discord bot | With a token, invited to your server ([setup](#discord-bot-setup)) |
| FFmpeg | **Only for voice playback.** See [below](#ffmpeg-voice-only) |

Python dependencies (`discord.py`, `mcp`, `pydantic`, `PyNaCl`, `davey`) install
from `pyproject.toml`. FFmpeg does not -- it is a system binary.

## Install

```bash
git clone https://github.com/pavalso/discord-mcp.git
cd discord-mcp

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

### FFmpeg (voice only)

`play_audio` shells out to FFmpeg to decode audio and transcode it to the PCM
discord.py streams. Every other tool works without it, and the voice tools that
only manage connections (`join_voice`, `leave_voice`, `voice_status`,
`set_voice_state`) do too.

```bash
# Windows
winget install Gyan.FFmpeg         # or: choco install ffmpeg
# macOS
brew install ffmpeg
# Debian/Ubuntu
sudo apt install ffmpeg
```

FFmpeg must be on `PATH`. If it is not, point at the binary directly:

```bash
export DISCORD_MCP_FFMPEG="C:/tools/ffmpeg/bin/ffmpeg.exe"
```

`play_audio` checks for the binary before spawning it, so a missing FFmpeg
returns a clear error rather than failing silently inside the player thread.

## Discord bot setup

1. Create an application at the
   [Discord Developer Portal](https://discord.com/developers/applications).
2. Under **Bot**, copy the token.
3. Under **Bot -> Privileged Gateway Intents**, enable **Server Members Intent**
   and **Message Content Intent**. The server requests both, and `connect` fails
   with `PrivilegedIntentsRequired` if they are off.
4. Under **OAuth2 -> URL Generator**, tick `bot`, pick the permissions you want
   the bot to have, and invite it with the generated URL.

The bot can only do what its role permits. Tools that need a permission the bot
lacks fail with `discord.Forbidden`.

## Configure your MCP client

Add the server to your client's MCP config -- `.mcp.json` in the project root
for Claude Code, or `claude_desktop_config.json` for Claude Desktop:

```json
{
  "mcpServers": {
    "discord": {
      "command": "/absolute/path/to/discord-mcp/.venv/bin/python",
      "args": ["-m", "discord_mcp.server"],
      "env": { "DISCORD_BOT_TOKEN": "your-token-here" }
    }
  }
}
```

On Windows the command is `.venv\\Scripts\\python.exe`.

> **Keep the token out of version control.** `.mcp.json` is gitignored for
> exactly this reason. A leaked bot token lets anyone drive your bot; if that
> happens, regenerate it in the Developer Portal immediately.

The server speaks stdio and is started by the client -- there is nothing to run
by hand.

## Usage

Every tool needs a live bot, so `connect` runs first in a session:

```
connect                                  -> Connected as MyBot (ID: 123...)
list_guilds                              -> [{"id": "456...", "name": "My Server"}]
send_message channel_id=789 content="hi"
```

`connect` takes the token from `DISCORD_BOT_TOKEN`; pass one explicitly only if
you have a reason to, since a parameter puts the token in the conversation.
`bot_status` is safe to call at any time and reports `connected: false` instead
of raising when the bot is down.

## Tools

| Domain | Count | Tools |
|--------|-------|-------|
| [Connection](docs/connection.md) | 4 | connect, disconnect, bot_status, change_presence |
| [Messages](docs/messages.md) | 12 | send, embeds, edit, delete, history, pins, reactions |
| [Channels](docs/channels.md) | 10 | list, get, create (text/voice/stage/category/forum), edit, delete, permissions |
| [Threads](docs/threads.md) | 9 | create, edit, delete, list active/archived, join/leave, members |
| [Members](docs/members.md) | 12 | get user/member, list, search, kick, ban, timeout, edit, roles, DM |
| [Roles](docs/roles.md) | 5 | list, get, create, edit, delete |
| [Guilds](docs/guilds.md) | 4 | list, get, edit, leave |
| [Webhooks](docs/webhooks.md) | 5 | list, create, send, edit, delete |
| [Invites](docs/invites.md) | 4 | list, create, delete, get |
| [Emojis](docs/emojis.md) | 8 | list/create/edit/delete emojis and stickers |
| [Scheduled events](docs/scheduled_events.md) | 4 | list, create, edit, delete |
| [Moderation](docs/moderation.md) | 6 | audit log, bans, purge, automod |
| [Voice](docs/voice.md) | 9 | join/leave/move, mute/deafen, status, audio playback |

`docs/` documents every tool against the discord.py calls it makes, plus
references for [core concepts](docs/core_concepts.md),
[permissions](docs/permissions_reference.md), and [enums](docs/enums_reference.md).

## Development

```bash
python -m pytest tests/ -v                       # Full suite
python -m pytest tests/ -k "send_message" -v     # One pattern

ruff check .                                     # Lint
ruff format .                                    # Format
mypy                                             # Type check

# Verify the server loads and count registered tools
python -c "from discord_mcp.server import mcp; print(len(mcp._tool_manager.list_tools()), 'tools')"
```

CI runs all of the above on every push and pull request, with the tests on
Python 3.12 and 3.13.

Tests never touch the network -- discord.py is mocked throughout. See
[CLAUDE.md](CLAUDE.md) for the TDD workflow and code conventions this project
follows.

```
discord_mcp/
├── bot.py          # Bot lifecycle: start_bot, stop_bot, get_bot
├── server.py       # FastMCP entry point, connection tools, module registration
└── tools/          # One module per domain, each exposing register(mcp)
tests/              # Mirrors the source layout
docs/               # Per-module discord.py API reference
```

## License

[MIT](LICENSE)
