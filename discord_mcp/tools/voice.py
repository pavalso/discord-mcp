"""Voice tools — join, move between, leave, inspect, and play audio in voice channels."""

from __future__ import annotations

import logging
import os
import shutil
from typing import cast

import discord
from mcp.server.fastmcp import FastMCP

from discord_mcp.bot import get_bot

log = logging.getLogger(__name__)

#: Channel types the bot can hold a voice connection in.
VOICE_CHANNEL_TYPES = ("voice", "stage_voice")

VoiceChannelLike = discord.VoiceChannel | discord.StageChannel

#: Accepted volume range. 1.0 leaves the source at its own level.
MIN_VOLUME = 0.0
MAX_VOLUME = 2.0

#: ffmpeg flags that let a network stream survive a dropped connection.
STREAM_BEFORE_OPTIONS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

#: Attribute stashed on the audio source so voice_status can report what is playing.
SOURCE_LABEL_ATTR = "mcp_source_label"


def _ffmpeg_executable() -> str:
    """The ffmpeg binary to spawn, overridable for installs that are not on PATH."""
    return os.environ.get("DISCORD_MCP_FFMPEG", "ffmpeg")


def _voice_state_flags(guild: discord.Guild) -> dict:
    """Report the bot's own mute/deaf flags, or None when its voice state is unknown."""
    voice_state = getattr(getattr(guild, "me", None), "voice", None)
    self_mute = getattr(voice_state, "self_mute", None)
    self_deaf = getattr(voice_state, "self_deaf", None)
    return {
        "self_mute": self_mute if isinstance(self_mute, bool) else None,
        "self_deaf": self_deaf if isinstance(self_deaf, bool) else None,
    }


def _playback_flags(voice_client: discord.VoiceClient) -> dict:
    """Report what the connection is currently playing, if anything."""
    label = getattr(getattr(voice_client, "source", None), SOURCE_LABEL_ATTR, None)
    return {
        "playing": bool(voice_client.is_playing()),
        "paused": bool(voice_client.is_paused()),
        "source": label if isinstance(label, str) else None,
    }


def _connection_to_dict(voice_client: discord.VoiceClient, channel: VoiceChannelLike) -> dict:
    """Describe a live voice connection as a serialisable dict."""
    latency = getattr(voice_client, "latency", None)
    return {
        "connected": True,
        "guild_id": str(channel.guild.id),
        "guild_name": channel.guild.name,
        "channel_id": str(channel.id),
        "channel_name": channel.name,
        "latency_ms": round(latency * 1000, 2) if isinstance(latency, (int, float)) else None,
        **_voice_state_flags(channel.guild),
        **_playback_flags(voice_client),
    }


def _require_voice_client(guild_id: str) -> discord.VoiceClient:
    """Return the guild's live voice connection, or explain why there isn't one."""
    bot = get_bot()
    guild = bot.get_guild(int(guild_id))
    if guild is None:
        raise ValueError(f"Guild {guild_id} not found (not in cache).")

    voice_client = cast(discord.VoiceClient | None, guild.voice_client)
    if voice_client is None:
        raise ValueError(f"Not connected to voice in guild {guild_id}.")
    return voice_client


def _check_volume(volume: float) -> None:
    if not MIN_VOLUME <= volume <= MAX_VOLUME:
        raise ValueError(f"volume must be between {MIN_VOLUME} and {MAX_VOLUME} (got {volume}).")


def _build_audio_source(source: str, volume: float) -> discord.PCMVolumeTransformer:
    """Wrap a file path or http(s) URL in an ffmpeg-backed, volume-adjustable source."""
    executable = _ffmpeg_executable()
    if shutil.which(executable) is None and not os.path.isfile(executable):
        raise RuntimeError(
            f"ffmpeg executable '{executable}' not found. Install FFmpeg and put it on "
            "PATH, or set the DISCORD_MCP_FFMPEG env var to its full path."
        )

    is_stream = source.startswith(("http://", "https://"))
    if not is_stream and not os.path.isfile(source):
        raise ValueError(f"Audio source '{source}' is not an existing file or an http(s) URL.")

    audio = discord.FFmpegPCMAudio(
        source,
        executable=executable,
        before_options=STREAM_BEFORE_OPTIONS if is_stream else None,
    )
    transformer = discord.PCMVolumeTransformer(audio, volume=volume)
    setattr(transformer, SOURCE_LABEL_ATTR, source)
    return transformer


def _on_playback_finished(error: Exception | None) -> None:
    """Playback callback — runs off the event loop, so it only logs."""
    if error is not None:
        log.error("Voice playback ended with an error: %s", error)


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def join_voice(
        channel_id: str,
        *,
        self_mute: bool = False,
        self_deaf: bool = True,
    ) -> dict:
        """Connect the bot to a voice or stage channel.

        If the bot is already connected elsewhere in the same guild, it moves to
        the target channel instead of opening a second connection. The mute and
        deaf flags are applied either way.

        Args:
            channel_id: Target voice or stage channel ID.
            self_mute: Join muted, so the bot cannot transmit audio.
            self_deaf: Join deafened, so the bot does not receive audio. Defaults to True.

        Returns:
            The resulting connection, including a "moved" flag that is True when an
            existing connection was relocated rather than newly opened.
        """
        bot = get_bot()
        found = bot.get_channel(int(channel_id))
        if found is None:
            raise ValueError(f"Channel {channel_id} not found (not in cache).")
        channel_type = getattr(found, "type", None)
        if str(channel_type) not in VOICE_CHANNEL_TYPES:
            raise ValueError(f"Channel {channel_id} is not a voice channel (type: {channel_type}).")
        channel = cast(VoiceChannelLike, found)

        existing = cast(discord.VoiceClient | None, channel.guild.voice_client)
        if existing is not None:
            # move_to() carries no voice-state flags, so apply them separately —
            # otherwise the gateway resets the bot to unmuted and undeafened.
            await existing.move_to(channel)
            await channel.guild.change_voice_state(
                channel=channel, self_mute=self_mute, self_deaf=self_deaf
            )
            return {**_connection_to_dict(existing, channel), "moved": True}

        try:
            voice_client = await channel.connect(self_mute=self_mute, self_deaf=self_deaf)
        except RuntimeError as exc:
            raise RuntimeError(
                f"Voice connection failed: {exc}. Voice support requires the PyNaCl "
                "and davey libraries — install them with 'pip install PyNaCl davey', "
                "then restart the server so discord.py picks them up."
            ) from exc

        return {**_connection_to_dict(voice_client, channel), "moved": False}

    @mcp.tool()
    async def set_voice_state(
        guild_id: str,
        *,
        self_mute: bool | None = None,
        self_deaf: bool | None = None,
    ) -> dict:
        """Mute or deafen the bot on an existing voice connection.

        Args:
            guild_id: Guild whose voice connection should be updated.
            self_mute: Set the bot's self-mute flag. Omit to leave it unchanged.
            self_deaf: Set the bot's self-deaf flag. Omit to leave it unchanged.
        """
        if self_mute is None and self_deaf is None:
            raise ValueError("Pass at least one of self_mute or self_deaf.")

        voice_client = _require_voice_client(guild_id)
        channel = cast(VoiceChannelLike, voice_client.channel)
        current = _voice_state_flags(channel.guild)

        resolved_mute = current["self_mute"] if self_mute is None else self_mute
        resolved_deaf = current["self_deaf"] if self_deaf is None else self_deaf

        await channel.guild.change_voice_state(
            channel=channel,
            self_mute=bool(resolved_mute),
            self_deaf=bool(resolved_deaf),
        )
        return {
            **_connection_to_dict(voice_client, channel),
            "self_mute": bool(resolved_mute),
            "self_deaf": bool(resolved_deaf),
        }

    @mcp.tool()
    async def leave_voice(guild_id: str) -> str:
        """Disconnect the bot from its voice channel in a guild.

        Args:
            guild_id: Guild whose voice connection should be closed.
        """
        bot = get_bot()
        guild = bot.get_guild(int(guild_id))
        if guild is None:
            raise ValueError(f"Guild {guild_id} not found (not in cache).")

        voice_client = cast(discord.VoiceClient | None, guild.voice_client)
        if voice_client is None:
            raise ValueError(f"Not connected to voice in guild {guild_id}.")

        channel_name = voice_client.channel.name
        await voice_client.disconnect(force=False)
        return f"Disconnected from voice channel '{channel_name}' in guild {guild_id}."

    @mcp.tool()
    async def voice_status(*, guild_id: str | None = None) -> dict:
        """Report the bot's current voice connections, including playback state.

        Args:
            guild_id: Restrict the report to this guild. Omit to list every connection.
        """
        bot = get_bot()

        if guild_id is not None:
            guild = bot.get_guild(int(guild_id))
            if guild is None:
                raise ValueError(f"Guild {guild_id} not found (not in cache).")
            voice_client = cast(discord.VoiceClient | None, guild.voice_client)
            if voice_client is None:
                return {"connected": False, "guild_id": guild_id}
            return _connection_to_dict(voice_client, voice_client.channel)

        clients = cast(list[discord.VoiceClient], list(bot.voice_clients))
        connections = [_connection_to_dict(vc, vc.channel) for vc in clients]
        return {"connection_count": len(connections), "connections": connections}

    # -----------------------------------------------------------------------
    # Playback
    # -----------------------------------------------------------------------

    @mcp.tool()
    async def play_audio(
        guild_id: str,
        source: str,
        *,
        volume: float = 1.0,
        replace: bool = False,
    ) -> dict:
        """Play an audio file or stream in the guild's current voice channel.

        Requires an existing connection (see join_voice) and FFmpeg on PATH.
        Playback is asynchronous — this returns as soon as it starts.

        Args:
            guild_id: Guild whose voice connection should play the audio.
            source: Local file path, or an http(s) URL FFmpeg can read.
            volume: Playback volume, 0.0 to 2.0. 1.0 is the source's own level.
            replace: Interrupt whatever is already playing. Without it, playing
                over an active source is an error.
        """
        _check_volume(volume)
        voice_client = _require_voice_client(guild_id)

        if voice_client.is_playing() or voice_client.is_paused():
            if not replace:
                raise ValueError(
                    f"Already playing audio in guild {guild_id}. Pass replace=True to "
                    "interrupt it, or call stop_audio first."
                )
            voice_client.stop()

        audio = _build_audio_source(source, volume)
        voice_client.play(audio, after=_on_playback_finished)

        return {
            **_connection_to_dict(voice_client, voice_client.channel),
            "source": source,
            "volume": volume,
        }

    @mcp.tool()
    async def stop_audio(guild_id: str) -> str:
        """Stop playback and discard the current audio source.

        Args:
            guild_id: Guild whose playback should stop.
        """
        voice_client = _require_voice_client(guild_id)
        if not (voice_client.is_playing() or voice_client.is_paused()):
            raise ValueError(f"Nothing is playing in guild {guild_id}.")

        voice_client.stop()
        return f"Stopped playback in guild {guild_id}."

    @mcp.tool()
    async def pause_audio(guild_id: str) -> str:
        """Pause playback, keeping the current audio source for resume_audio.

        Args:
            guild_id: Guild whose playback should pause.
        """
        voice_client = _require_voice_client(guild_id)
        if not voice_client.is_playing():
            raise ValueError(f"Nothing is playing in guild {guild_id}.")

        voice_client.pause()
        return f"Paused playback in guild {guild_id}."

    @mcp.tool()
    async def resume_audio(guild_id: str) -> str:
        """Resume playback that was paused with pause_audio.

        Args:
            guild_id: Guild whose playback should resume.
        """
        voice_client = _require_voice_client(guild_id)
        if not voice_client.is_paused():
            raise ValueError(f"Playback is not paused in guild {guild_id}.")

        voice_client.resume()
        return f"Resumed playback in guild {guild_id}."

    @mcp.tool()
    async def set_volume(guild_id: str, volume: float) -> dict:
        """Change the volume of the audio currently playing.

        Args:
            guild_id: Guild whose playback volume should change.
            volume: Playback volume, 0.0 to 2.0. 1.0 is the source's own level.
        """
        _check_volume(volume)
        voice_client = _require_voice_client(guild_id)

        source = getattr(voice_client, "source", None)
        if source is None:
            raise ValueError(f"Nothing is playing in guild {guild_id}.")
        if not isinstance(source, discord.PCMVolumeTransformer):
            raise ValueError(
                f"The audio playing in guild {guild_id} does not support volume changes."
            )

        source.volume = volume
        return {"guild_id": guild_id, "volume": volume}
