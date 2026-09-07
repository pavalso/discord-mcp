"""Tests for voice tools — registration, schemas, and behavior."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools import voice as voice_module
from discord_mcp.tools.voice import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _call(name: str, **kwargs):
    return mcp._tool_manager._tools[name].fn(**kwargs)


def _make_guild(
    *,
    id: int = 111,
    name: str = "Test Guild",
    voice_client=None,
    self_mute: bool | None = False,
    self_deaf: bool | None = True,
) -> MagicMock:
    guild = MagicMock()
    guild.id = id
    guild.name = name
    guild.voice_client = voice_client
    guild.change_voice_state = AsyncMock()
    guild.me.voice.self_mute = self_mute
    guild.me.voice.self_deaf = self_deaf
    return guild


def _make_voice_channel(
    *,
    id: int = 200,
    name: str = "General Voice",
    type: str = "voice",
    guild: MagicMock | None = None,
) -> MagicMock:
    ch = MagicMock()
    ch.id = id
    ch.name = name
    ch.type = type
    ch.guild = guild if guild is not None else _make_guild()
    ch.connect = AsyncMock()
    return ch


def _make_voice_client(
    *,
    channel: MagicMock | None = None,
    latency: float = 0.02,
    playing: bool = False,
    paused: bool = False,
    source=None,
) -> MagicMock:
    vc = MagicMock()
    vc.channel = channel if channel is not None else _make_voice_channel()
    vc.guild = vc.channel.guild
    vc.latency = latency
    vc.source = source
    vc.is_connected.return_value = True
    vc.is_playing.return_value = playing
    vc.is_paused.return_value = paused
    vc.move_to = AsyncMock()
    vc.disconnect = AsyncMock()
    return vc


def _make_volume_source(volume: float = 1.0) -> discord.PCMVolumeTransformer:
    """A real PCMVolumeTransformer so isinstance checks in set_volume hold."""
    original = MagicMock(spec=discord.AudioSource)
    original.is_opus.return_value = False
    return discord.PCMVolumeTransformer(original, volume=volume)


def _connected_guild(
    *,
    guild_id: int = 111,
    playing: bool = False,
    paused: bool = False,
    source=None,
) -> tuple[MagicMock, MagicMock]:
    """A guild with a live voice connection. Returns (guild, voice_client)."""
    guild = _make_guild(id=guild_id)
    channel = _make_voice_channel(guild=guild)
    vc = _make_voice_client(channel=channel, playing=playing, paused=paused, source=source)
    guild.voice_client = vc
    return guild, vc


class TestVoiceToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "join_voice",
        "leave_voice",
        "voice_status",
        "set_voice_state",
        "play_audio",
        "stop_audio",
        "pause_audio",
        "resume_audio",
        "set_volume",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestVoiceToolSchemas:
    def test_join_voice_requires_channel_id(self):
        schema = _get_tool_schema("join_voice")
        assert schema.get("required", []) == ["channel_id"]

    def test_join_voice_optional_fields(self):
        props = _get_tool_schema("join_voice").get("properties", {})
        for field in ("self_mute", "self_deaf"):
            assert field in props

    def test_join_voice_defaults_to_deafened(self):
        props = _get_tool_schema("join_voice").get("properties", {})
        assert props["self_deaf"]["default"] is True
        assert props["self_mute"]["default"] is False

    def test_leave_voice_requires_guild_id(self):
        schema = _get_tool_schema("leave_voice")
        assert schema.get("required", []) == ["guild_id"]

    def test_voice_status_has_no_required_fields(self):
        schema = _get_tool_schema("voice_status")
        assert schema.get("required", []) == []
        assert "guild_id" in schema.get("properties", {})

    def test_set_voice_state_requires_guild_id(self):
        schema = _get_tool_schema("set_voice_state")
        assert schema.get("required", []) == ["guild_id"]
        props = schema.get("properties", {})
        for field in ("self_mute", "self_deaf"):
            assert props[field]["default"] is None

    def test_play_audio_requires_guild_and_source(self):
        schema = _get_tool_schema("play_audio")
        assert schema.get("required", []) == ["guild_id", "source"]

    def test_play_audio_optional_fields(self):
        props = _get_tool_schema("play_audio").get("properties", {})
        assert props["volume"]["default"] == 1.0
        assert props["replace"]["default"] is False

    @pytest.mark.parametrize("name", ["stop_audio", "pause_audio", "resume_audio"])
    def test_playback_control_requires_guild_id(self, name):
        assert _get_tool_schema(name).get("required", []) == ["guild_id"]

    def test_set_volume_requires_guild_and_volume(self):
        schema = _get_tool_schema("set_volume")
        assert schema.get("required", []) == ["guild_id", "volume"]


class TestJoinVoice:
    async def test_connects_to_voice_channel(self, inject_bot):
        guild = _make_guild(id=111, name="Test Guild", voice_client=None)
        channel = _make_voice_channel(id=200, name="General Voice", guild=guild)
        channel.connect.return_value = _make_voice_client(channel=channel)
        inject_bot.get_channel.return_value = channel

        result = await _call("join_voice", channel_id="200")

        assert result["connected"] is True
        assert result["moved"] is False
        assert result["channel_id"] == "200"
        assert result["channel_name"] == "General Voice"
        assert result["guild_id"] == "111"
        channel.connect.assert_awaited_once_with(self_mute=False, self_deaf=True)

    async def test_passes_mute_and_deaf_flags(self, inject_bot):
        channel = _make_voice_channel()
        channel.connect.return_value = _make_voice_client(channel=channel)
        inject_bot.get_channel.return_value = channel

        await _call("join_voice", channel_id="200", self_mute=True, self_deaf=False)

        channel.connect.assert_awaited_once_with(self_mute=True, self_deaf=False)

    async def test_reports_latency(self, inject_bot):
        channel = _make_voice_channel()
        channel.connect.return_value = _make_voice_client(channel=channel, latency=0.025)
        inject_bot.get_channel.return_value = channel

        result = await _call("join_voice", channel_id="200")

        assert result["latency_ms"] == 25.0

    async def test_reports_voice_state_flags(self, inject_bot):
        guild = _make_guild(self_mute=False, self_deaf=True)
        channel = _make_voice_channel(guild=guild)
        channel.connect.return_value = _make_voice_client(channel=channel)
        inject_bot.get_channel.return_value = channel

        result = await _call("join_voice", channel_id="200")

        assert result["self_mute"] is False
        assert result["self_deaf"] is True

    async def test_reports_playback_state(self, inject_bot):
        channel = _make_voice_channel()
        channel.connect.return_value = _make_voice_client(channel=channel)
        inject_bot.get_channel.return_value = channel

        result = await _call("join_voice", channel_id="200")

        assert result["playing"] is False
        assert result["paused"] is False
        assert result["source"] is None

    async def test_accepts_stage_channel(self, inject_bot):
        channel = _make_voice_channel(id=300, name="Stage", type="stage_voice")
        channel.connect.return_value = _make_voice_client(channel=channel)
        inject_bot.get_channel.return_value = channel

        result = await _call("join_voice", channel_id="300")

        assert result["channel_id"] == "300"

    async def test_moves_when_already_connected_in_guild(self, inject_bot):
        old_channel = _make_voice_channel(id=199, name="Old Voice")
        existing = _make_voice_client(channel=old_channel)
        guild = _make_guild(id=111, voice_client=existing)
        target = _make_voice_channel(id=200, name="General Voice", guild=guild)
        inject_bot.get_channel.return_value = target

        result = await _call("join_voice", channel_id="200")

        existing.move_to.assert_awaited_once_with(target)
        target.connect.assert_not_awaited()
        assert result["moved"] is True
        assert result["channel_id"] == "200"
        assert result["channel_name"] == "General Voice"

    async def test_move_applies_mute_and_deaf_flags(self, inject_bot):
        """move_to() carries no flags, so they must be sent as a voice state update."""
        existing = _make_voice_client(channel=_make_voice_channel(id=199))
        guild = _make_guild(id=111, voice_client=existing)
        target = _make_voice_channel(id=200, guild=guild)
        inject_bot.get_channel.return_value = target

        await _call("join_voice", channel_id="200", self_mute=True, self_deaf=True)

        guild.change_voice_state.assert_awaited_once_with(
            channel=target, self_mute=True, self_deaf=True
        )

    async def test_move_can_undeafen(self, inject_bot):
        existing = _make_voice_client(channel=_make_voice_channel(id=199))
        guild = _make_guild(id=111, voice_client=existing)
        target = _make_voice_channel(id=200, guild=guild)
        inject_bot.get_channel.return_value = target

        await _call("join_voice", channel_id="200", self_deaf=False)

        guild.change_voice_state.assert_awaited_once_with(
            channel=target, self_mute=False, self_deaf=False
        )

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _call("join_voice", channel_id="999")

    async def test_rejects_non_voice_channel(self, inject_bot):
        channel = _make_voice_channel(id=400, name="general", type="text")
        inject_bot.get_channel.return_value = channel

        with pytest.raises(ValueError, match="not a voice channel"):
            await _call("join_voice", channel_id="400")

    async def test_missing_pynacl_gives_actionable_error(self, inject_bot):
        channel = _make_voice_channel()
        channel.connect.side_effect = RuntimeError("PyNaCl library needed in order to use voice")
        inject_bot.get_channel.return_value = channel

        with pytest.raises(RuntimeError, match="PyNaCl"):
            await _call("join_voice", channel_id="200")


class TestSetVoiceState:
    async def test_undeafens_without_moving(self, inject_bot):
        guild, vc = _connected_guild()
        inject_bot.get_guild.return_value = guild

        result = await _call("set_voice_state", guild_id="111", self_deaf=False)

        guild.change_voice_state.assert_awaited_once_with(
            channel=vc.channel, self_mute=False, self_deaf=False
        )
        vc.move_to.assert_not_awaited()
        assert result["self_deaf"] is False

    async def test_preserves_unspecified_flag(self, inject_bot):
        guild, vc = _connected_guild()
        guild.me.voice.self_mute = True
        guild.me.voice.self_deaf = True
        inject_bot.get_guild.return_value = guild

        await _call("set_voice_state", guild_id="111", self_deaf=False)

        guild.change_voice_state.assert_awaited_once_with(
            channel=vc.channel, self_mute=True, self_deaf=False
        )

    async def test_requires_at_least_one_flag(self, inject_bot):
        guild, _ = _connected_guild()
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="at least one"):
            await _call("set_voice_state", guild_id="111")

    async def test_not_connected(self, inject_bot):
        inject_bot.get_guild.return_value = _make_guild(id=111, voice_client=None)

        with pytest.raises(ValueError, match="Not connected"):
            await _call("set_voice_state", guild_id="111", self_deaf=False)

    async def test_guild_not_found(self, inject_bot):
        inject_bot.get_guild.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _call("set_voice_state", guild_id="999", self_deaf=False)


class TestLeaveVoice:
    async def test_disconnects(self, inject_bot):
        channel = _make_voice_channel(id=200, name="General Voice")
        vc = _make_voice_client(channel=channel)
        inject_bot.get_guild.return_value = _make_guild(id=111, voice_client=vc)

        result = await _call("leave_voice", guild_id="111")

        vc.disconnect.assert_awaited_once()
        assert "General Voice" in result

    async def test_guild_not_found(self, inject_bot):
        inject_bot.get_guild.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _call("leave_voice", guild_id="999")

    async def test_not_connected(self, inject_bot):
        inject_bot.get_guild.return_value = _make_guild(id=111, voice_client=None)

        with pytest.raises(ValueError, match="Not connected"):
            await _call("leave_voice", guild_id="111")


class TestVoiceStatus:
    async def test_reports_guild_connection(self, inject_bot):
        channel = _make_voice_channel(id=200, name="General Voice")
        vc = _make_voice_client(channel=channel)
        inject_bot.get_guild.return_value = _make_guild(id=111, voice_client=vc)

        result = await _call("voice_status", guild_id="111")

        assert result["connected"] is True
        assert result["channel_id"] == "200"
        assert result["guild_id"] == "111"

    async def test_reports_playback(self, inject_bot):
        source = _make_volume_source()
        setattr(source, voice_module.SOURCE_LABEL_ATTR, "clip.mp3")
        guild, _ = _connected_guild(playing=True, source=source)
        inject_bot.get_guild.return_value = guild

        result = await _call("voice_status", guild_id="111")

        assert result["playing"] is True
        assert result["paused"] is False
        assert result["source"] == "clip.mp3"

    async def test_reports_guild_not_connected(self, inject_bot):
        inject_bot.get_guild.return_value = _make_guild(id=111, voice_client=None)

        result = await _call("voice_status", guild_id="111")

        assert result["connected"] is False
        assert result["guild_id"] == "111"

    async def test_guild_not_found(self, inject_bot):
        inject_bot.get_guild.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _call("voice_status", guild_id="999")

    async def test_lists_all_connections(self, inject_bot):
        vc1 = _make_voice_client(channel=_make_voice_channel(id=200, name="A"))
        vc2 = _make_voice_client(channel=_make_voice_channel(id=201, name="B"))
        inject_bot.voice_clients = [vc1, vc2]

        result = await _call("voice_status")

        assert result["connection_count"] == 2
        assert [c["channel_name"] for c in result["connections"]] == ["A", "B"]

    async def test_no_connections(self, inject_bot):
        inject_bot.voice_clients = []

        result = await _call("voice_status")

        assert result["connection_count"] == 0
        assert result["connections"] == []


class TestBuildAudioSource:
    def test_wraps_local_file(self, tmp_path):
        clip = tmp_path / "clip.mp3"
        clip.write_bytes(b"not really audio")

        with patch.object(voice_module.discord, "FFmpegPCMAudio") as ffmpeg:
            ffmpeg.return_value = MagicMock(
                spec=discord.AudioSource, **{"is_opus.return_value": False}
            )
            source = voice_module._build_audio_source(str(clip), 0.5)

        ffmpeg.assert_called_once_with(str(clip), executable="ffmpeg", before_options=None)
        assert source.volume == 0.5
        assert getattr(source, voice_module.SOURCE_LABEL_ATTR) == str(clip)

    def test_adds_reconnect_options_for_streams(self):
        with patch.object(voice_module.discord, "FFmpegPCMAudio") as ffmpeg:
            ffmpeg.return_value = MagicMock(
                spec=discord.AudioSource, **{"is_opus.return_value": False}
            )
            voice_module._build_audio_source("https://example.com/stream.mp3", 1.0)

        _, kwargs = ffmpeg.call_args
        assert kwargs["before_options"] == voice_module.STREAM_BEFORE_OPTIONS

    def test_honours_ffmpeg_env_override(self, tmp_path, monkeypatch):
        fake_ffmpeg = tmp_path / "ffmpeg.exe"
        fake_ffmpeg.write_bytes(b"")
        clip = tmp_path / "clip.mp3"
        clip.write_bytes(b"")
        monkeypatch.setenv("DISCORD_MCP_FFMPEG", str(fake_ffmpeg))

        with patch.object(voice_module.discord, "FFmpegPCMAudio") as ffmpeg:
            ffmpeg.return_value = MagicMock(
                spec=discord.AudioSource, **{"is_opus.return_value": False}
            )
            voice_module._build_audio_source(str(clip), 1.0)

        _, kwargs = ffmpeg.call_args
        assert kwargs["executable"] == str(fake_ffmpeg)

    def test_missing_ffmpeg_gives_actionable_error(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DISCORD_MCP_FFMPEG", str(tmp_path / "nope.exe"))

        with pytest.raises(RuntimeError, match="DISCORD_MCP_FFMPEG"):
            voice_module._build_audio_source("clip.mp3", 1.0)

    def test_rejects_missing_file(self, tmp_path):
        with pytest.raises(ValueError, match="not an existing file"):
            voice_module._build_audio_source(str(tmp_path / "absent.mp3"), 1.0)


class TestPlayAudio:
    async def test_plays_source(self, inject_bot):
        guild, vc = _connected_guild()
        inject_bot.get_guild.return_value = guild
        built = _make_volume_source()

        with patch.object(voice_module, "_build_audio_source", return_value=built) as build:
            result = await _call("play_audio", guild_id="111", source="clip.mp3")

        build.assert_called_once_with("clip.mp3", 1.0)
        vc.play.assert_called_once()
        assert vc.play.call_args.args[0] is built
        assert vc.play.call_args.kwargs["after"] is voice_module._on_playback_finished
        assert result["source"] == "clip.mp3"
        assert result["volume"] == 1.0

    async def test_passes_volume(self, inject_bot):
        guild, _ = _connected_guild()
        inject_bot.get_guild.return_value = guild

        with patch.object(voice_module, "_build_audio_source") as build:
            await _call("play_audio", guild_id="111", source="clip.mp3", volume=0.25)

        build.assert_called_once_with("clip.mp3", 0.25)

    async def test_rejects_out_of_range_volume(self, inject_bot):
        guild, _ = _connected_guild()
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="volume must be between"):
            await _call("play_audio", guild_id="111", source="clip.mp3", volume=5.0)

    async def test_refuses_to_interrupt_by_default(self, inject_bot):
        guild, vc = _connected_guild(playing=True)
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="replace=True"):
            await _call("play_audio", guild_id="111", source="clip.mp3")

        vc.play.assert_not_called()

    async def test_refuses_to_interrupt_paused_playback(self, inject_bot):
        guild, _ = _connected_guild(paused=True)
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="replace=True"):
            await _call("play_audio", guild_id="111", source="clip.mp3")

    async def test_replace_stops_current_playback(self, inject_bot):
        guild, vc = _connected_guild(playing=True)
        inject_bot.get_guild.return_value = guild

        with patch.object(voice_module, "_build_audio_source"):
            await _call("play_audio", guild_id="111", source="clip.mp3", replace=True)

        vc.stop.assert_called_once()
        vc.play.assert_called_once()

    async def test_requires_voice_connection(self, inject_bot):
        inject_bot.get_guild.return_value = _make_guild(id=111, voice_client=None)

        with pytest.raises(ValueError, match="Not connected"):
            await _call("play_audio", guild_id="111", source="clip.mp3")

    async def test_guild_not_found(self, inject_bot):
        inject_bot.get_guild.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _call("play_audio", guild_id="999", source="clip.mp3")


class TestPlaybackControls:
    async def test_stop(self, inject_bot):
        guild, vc = _connected_guild(playing=True)
        inject_bot.get_guild.return_value = guild

        result = await _call("stop_audio", guild_id="111")

        vc.stop.assert_called_once()
        assert "Stopped" in result

    async def test_stop_when_idle(self, inject_bot):
        guild, vc = _connected_guild()
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="Nothing is playing"):
            await _call("stop_audio", guild_id="111")

        vc.stop.assert_not_called()

    async def test_pause(self, inject_bot):
        guild, vc = _connected_guild(playing=True)
        inject_bot.get_guild.return_value = guild

        await _call("pause_audio", guild_id="111")

        vc.pause.assert_called_once()

    async def test_pause_when_idle(self, inject_bot):
        guild, _ = _connected_guild()
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="Nothing is playing"):
            await _call("pause_audio", guild_id="111")

    async def test_resume(self, inject_bot):
        guild, vc = _connected_guild(paused=True)
        inject_bot.get_guild.return_value = guild

        await _call("resume_audio", guild_id="111")

        vc.resume.assert_called_once()

    async def test_resume_when_not_paused(self, inject_bot):
        guild, _ = _connected_guild(playing=True)
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="not paused"):
            await _call("resume_audio", guild_id="111")


class TestSetVolume:
    async def test_changes_volume(self, inject_bot):
        source = _make_volume_source(volume=1.0)
        guild, _ = _connected_guild(playing=True, source=source)
        inject_bot.get_guild.return_value = guild

        result = await _call("set_volume", guild_id="111", volume=0.4)

        assert source.volume == 0.4
        assert result["volume"] == 0.4

    async def test_rejects_out_of_range(self, inject_bot):
        guild, _ = _connected_guild(playing=True, source=_make_volume_source())
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="volume must be between"):
            await _call("set_volume", guild_id="111", volume=-1.0)

    async def test_nothing_playing(self, inject_bot):
        guild, _ = _connected_guild()
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="Nothing is playing"):
            await _call("set_volume", guild_id="111", volume=0.5)

    async def test_source_without_volume_support(self, inject_bot):
        guild, _ = _connected_guild(playing=True, source=MagicMock(spec=discord.AudioSource))
        inject_bot.get_guild.return_value = guild

        with pytest.raises(ValueError, match="does not support volume"):
            await _call("set_volume", guild_id="111", volume=0.5)


class TestPlaybackCallback:
    def test_logs_errors(self, caplog):
        with caplog.at_level("ERROR"):
            voice_module._on_playback_finished(RuntimeError("ffmpeg died"))
        assert "ffmpeg died" in caplog.text

    def test_silent_on_clean_finish(self, caplog):
        with caplog.at_level("ERROR"):
            voice_module._on_playback_finished(None)
        assert caplog.text == ""
