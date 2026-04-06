# Discord MCP Server — Development Guide

## Project overview

A Python MCP (Model Context Protocol) server that exposes Discord bot operations as MCP tools, built on `discord.py` and the `mcp` SDK (FastMCP).

## Quick reference

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_bot.py -v

# Run tests matching a pattern
python -m pytest tests/ -k "test_send_message" -v

# Verify server loads and list tools
python -c "from discord_mcp.server import mcp; print(len(mcp._tool_manager.list_tools()), 'tools')"
```

## Project structure

```
discord_mcp/
├── bot.py                  # Bot lifecycle (start_bot, stop_bot, get_bot)
├── server.py               # FastMCP entry point, connection tools, module registration
└── tools/                  # One file per domain, each with a register(mcp) function
    ├── messages.py          # send, edit, delete, reactions, history, pins
    ├── channels.py          # create/edit/delete text, voice, category, forum channels
    ├── threads.py           # create, edit, archive, join/leave, member management
    ├── members.py           # fetch, kick, ban, timeout, role assignment, DM
    ├── roles.py             # list, create, edit, delete roles
    ├── guilds.py            # list, info, edit guild settings
    ├── webhooks.py          # create, send, edit, delete webhooks
    ├── invites.py           # create, list, delete, get invites
    ├── emojis.py            # emojis and stickers
    ├── scheduled_events.py  # guild scheduled events
    └── moderation.py        # audit log, automod, purge, bans
tests/
├── conftest.py             # Shared fixtures (mock bot, inject_bot, mcp_server)
├── test_bot.py             # Bot lifecycle unit tests
├── test_server.py          # Server setup, tool registration, connection tools
└── test_tools_*.py         # Per-domain: registration, schema validation, NotImplementedError
```

## Development principles

### Test-driven development

This project follows strict TDD. Every tool has three layers of tests that must pass:

1. **Registration tests** — verify the tool is registered with the correct name
2. **Schema tests** — verify required/optional parameters and their types
3. **Behavior tests** — currently assert `NotImplementedError`; replace with real assertions when implementing

**Before implementing any tool**, its tests already exist. When you implement a tool:
- The `NotImplementedError` test for that tool will break — replace it with tests that verify the actual behavior (correct return values, proper discord.py API calls via mocks, error handling).
- Add new test cases for edge cases and error paths.
- Run `python -m pytest tests/ -v` and confirm **all 159+ tests pass** before considering the work done.

### When writing or modifying code

- **Always run the full test suite** after any change: `python -m pytest tests/ -v`
- Never leave failing tests. If a change breaks existing tests, fix them as part of the same change.
- New functionality must have corresponding tests. No untested code.
- Use `unittest.mock` (MagicMock, AsyncMock, patch) for discord.py API calls — never make real Discord API calls in tests.
- Test files mirror source files: `tools/messages.py` → `tests/test_tools_messages.py`

### Code quality standards

- Type annotations on all function signatures (use `from __future__ import annotations`).
- Async functions for all tool implementations (discord.py is async).
- Use `get_bot()` from `discord_mcp.bot` inside tool implementations to get the live bot instance.
- Keep tools focused — each tool does one thing. Avoid God-tools that take a `mode` parameter.
- All tools must have docstrings with `Args:` sections — these become the MCP tool descriptions shown to LLMs.
- Keyword-only arguments (after `*`) for optional parameters in tool signatures.
- Always include `reason: str | None = None` on tools that perform moderation or destructive actions (for Discord audit logs).

### Implementing a tool (checklist)

1. Read the existing test for the tool in `tests/test_tools_<module>.py`
2. Implement the tool body in `discord_mcp/tools/<module>.py`
3. Replace the `NotImplementedError` test with proper behavior tests
4. Add edge-case tests (not found, permission denied, invalid input)
5. Run `python -m pytest tests/ -v` — all green
