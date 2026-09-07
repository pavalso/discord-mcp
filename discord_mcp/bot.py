"""Discord bot client lifecycle management.

Manages the discord.py bot instance that runs in the background,
providing the MCP tools with a live connection to Discord.
"""

from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)

_bot: commands.Bot | None = None
_bot_task: asyncio.Task | None = None


def _create_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    return commands.Bot(command_prefix="!", intents=intents)


async def start_bot(token: str) -> commands.Bot:
    """Start the Discord bot in a background task and wait until it's ready."""
    global _bot, _bot_task

    if _bot is not None and _bot.is_ready():
        return _bot

    _bot = _create_bot()

    ready_event = asyncio.Event()

    @_bot.event
    async def on_ready() -> None:
        log.info("Discord bot connected as %s", _bot.user)
        ready_event.set()

    _bot_task = asyncio.create_task(_bot.start(token))

    try:
        await asyncio.wait_for(ready_event.wait(), timeout=30)
    except TimeoutError as exc:
        _bot_task.cancel()
        raise RuntimeError("Discord bot failed to connect within 30 seconds") from exc

    return _bot


async def stop_bot() -> None:
    """Gracefully shut down the bot."""
    global _bot, _bot_task

    if _bot is not None:
        await _bot.close()
        _bot = None

    if _bot_task is not None:
        _bot_task.cancel()
        _bot_task = None


def get_bot() -> commands.Bot:
    """Get the running bot instance. Raises if bot is not started."""
    if _bot is None or not _bot.is_ready():
        raise RuntimeError("Discord bot is not connected. Call the 'connect' tool first.")
    return _bot
