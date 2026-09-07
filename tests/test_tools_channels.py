"""Tests for channel tools — registration, schemas, and behavior."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.channels import register


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


def _make_channel(
    *,
    id: int = 100,
    name: str = "general",
    type: str = "text",
    position: int = 0,
    category_id: int | None = None,
    topic: str | None = None,
    nsfw: bool = False,
    slowmode_delay: int = 0,
    bitrate: int | None = None,
    user_limit: int | None = None,
) -> MagicMock:
    ch = MagicMock()
    ch.id = id
    ch.name = name
    ch.type = type
    ch.position = position
    ch.category_id = category_id
    ch.topic = topic
    ch.nsfw = nsfw
    ch.slowmode_delay = slowmode_delay
    if bitrate is not None:
        ch.bitrate = bitrate
    if user_limit is not None:
        ch.user_limit = user_limit
    ch.edit = AsyncMock(return_value=ch)
    ch.delete = AsyncMock()
    ch.set_permissions = AsyncMock()
    ch.guild = MagicMock()
    return ch


class TestChannelToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "list_channels",
        "get_channel",
        "create_text_channel",
        "create_voice_channel",
        "create_category",
        "create_forum_channel",
        "edit_channel",
        "delete_channel",
        "set_channel_permissions",
    }

    def test_all_tools_registered(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED


class TestChannelToolSchemas:
    def test_list_channels_requires_guild_id(self):
        schema = _get_tool_schema("list_channels")
        assert "guild_id" in schema.get("required", [])

    def test_create_text_channel_requires_guild_and_name(self):
        schema = _get_tool_schema("create_text_channel")
        required = schema.get("required", [])
        assert "guild_id" in required
        assert "name" in required

    def test_create_text_channel_optional_fields(self):
        schema = _get_tool_schema("create_text_channel")
        props = schema.get("properties", {})
        for field in ("topic", "category_id", "slowmode_delay", "nsfw", "reason"):
            assert field in props

    def test_create_voice_channel_has_bitrate_and_user_limit(self):
        schema = _get_tool_schema("create_voice_channel")
        props = schema.get("properties", {})
        assert "bitrate" in props
        assert "user_limit" in props

    def test_edit_channel_only_requires_channel_id(self):
        schema = _get_tool_schema("edit_channel")
        required = schema.get("required", [])
        assert required == ["channel_id"]

    def test_edit_channel_has_bitrate_and_user_limit(self):
        schema = _get_tool_schema("edit_channel")
        props = schema.get("properties", {})
        assert "bitrate" in props
        assert "user_limit" in props

    def test_set_channel_permissions_requires_target(self):
        schema = _get_tool_schema("set_channel_permissions")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "target_id" in required
        assert "target_type" in required


class TestListChannels:
    async def test_returns_all_channels(self, inject_bot):
        ch1 = _make_channel(id=1, name="general", position=0)
        ch2 = _make_channel(
            id=2, name="voice", type="voice", position=1, bitrate=64000, user_limit=10
        )
        inject_bot.get_guild.return_value = MagicMock(channels=[ch1, ch2])

        result = await mcp._tool_manager._tools["list_channels"].fn(guild_id="111")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "general"
        assert result[1]["id"] == "2"

    async def test_guild_not_found(self, inject_bot):
        inject_bot.get_guild.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await mcp._tool_manager._tools["list_channels"].fn(guild_id="999")


class TestGetChannel:
    async def test_returns_channel_dict(self, inject_bot):
        ch = _make_channel(id=42, name="info", topic="Welcome!")
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["get_channel"].fn(channel_id="42")

        assert result["id"] == "42"
        assert result["name"] == "info"
        assert result["topic"] == "Welcome!"

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await mcp._tool_manager._tools["get_channel"].fn(channel_id="999")


class TestCreateTextChannel:
    async def test_creates_channel(self, inject_bot):
        created = _make_channel(id=50, name="new-channel", topic="hello")
        guild = MagicMock()
        guild.create_text_channel = AsyncMock(return_value=created)
        guild.get_channel.return_value = None
        inject_bot.get_guild.return_value = guild

        result = await mcp._tool_manager._tools["create_text_channel"].fn(
            guild_id="111", name="new-channel", topic="hello"
        )

        assert result["id"] == "50"
        assert result["name"] == "new-channel"
        guild.create_text_channel.assert_awaited_once_with(
            "new-channel",
            topic="hello",
            category=None,
            slowmode_delay=0,
            nsfw=False,
            reason=None,
        )

    async def test_creates_with_category(self, inject_bot):
        cat = MagicMock()
        created = _make_channel(id=51, name="in-cat")
        guild = MagicMock()
        guild.get_channel.return_value = cat
        guild.create_text_channel = AsyncMock(return_value=created)
        inject_bot.get_guild.return_value = guild

        await mcp._tool_manager._tools["create_text_channel"].fn(
            guild_id="111", name="in-cat", category_id="200"
        )

        guild.create_text_channel.assert_awaited_once()
        call_kwargs = guild.create_text_channel.call_args
        assert call_kwargs.kwargs["category"] is cat

    async def test_guild_not_found(self, inject_bot):
        inject_bot.get_guild.return_value = None
        with pytest.raises(ValueError):
            await mcp._tool_manager._tools["create_text_channel"].fn(guild_id="999", name="x")


class TestCreateVoiceChannel:
    async def test_creates_channel(self, inject_bot):
        created = _make_channel(id=60, name="vc", type="voice", bitrate=64000, user_limit=10)
        guild = MagicMock()
        guild.create_voice_channel = AsyncMock(return_value=created)
        guild.get_channel.return_value = None
        inject_bot.get_guild.return_value = guild

        result = await mcp._tool_manager._tools["create_voice_channel"].fn(
            guild_id="111", name="vc", bitrate=64000, user_limit=10
        )

        assert result["id"] == "60"
        guild.create_voice_channel.assert_awaited_once()

    async def test_omits_bitrate_when_none(self, inject_bot):
        created = _make_channel(id=61, name="vc2", type="voice", bitrate=64000, user_limit=0)
        guild = MagicMock()
        guild.create_voice_channel = AsyncMock(return_value=created)
        guild.get_channel.return_value = None
        inject_bot.get_guild.return_value = guild

        await mcp._tool_manager._tools["create_voice_channel"].fn(guild_id="111", name="vc2")

        call_kwargs = guild.create_voice_channel.call_args.kwargs
        assert "bitrate" not in call_kwargs


class TestCreateCategory:
    async def test_creates_category(self, inject_bot):
        created = _make_channel(id=70, name="My Category", type="category")
        guild = MagicMock()
        guild.create_category = AsyncMock(return_value=created)
        inject_bot.get_guild.return_value = guild

        result = await mcp._tool_manager._tools["create_category"].fn(
            guild_id="111", name="My Category", reason="organizing"
        )

        assert result["id"] == "70"
        guild.create_category.assert_awaited_once_with("My Category", reason="organizing")


class TestCreateForumChannel:
    async def test_creates_forum(self, inject_bot):
        created = _make_channel(id=80, name="help-forum", topic="Ask questions")
        guild = MagicMock()
        guild.create_forum = AsyncMock(return_value=created)
        guild.get_channel.return_value = None
        inject_bot.get_guild.return_value = guild

        result = await mcp._tool_manager._tools["create_forum_channel"].fn(
            guild_id="111", name="help-forum", topic="Ask questions"
        )

        assert result["id"] == "80"
        guild.create_forum.assert_awaited_once_with(
            "help-forum",
            topic="Ask questions",
            category=None,
            slowmode_delay=0,
            nsfw=False,
            reason=None,
        )


class TestEditChannel:
    async def test_edits_channel(self, inject_bot):
        ch = _make_channel(id=100, name="updated")
        ch.edit = AsyncMock(return_value=ch)
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["edit_channel"].fn(
            channel_id="100", name="updated", nsfw=True, reason="cleanup"
        )

        assert result["name"] == "updated"
        ch.edit.assert_awaited_once_with(name="updated", nsfw=True, reason="cleanup")

    async def test_only_passes_provided_fields(self, inject_bot):
        ch = _make_channel(id=101, name="old")
        ch.edit = AsyncMock(return_value=ch)
        inject_bot.get_channel.return_value = ch

        await mcp._tool_manager._tools["edit_channel"].fn(channel_id="101", name="new")

        ch.edit.assert_awaited_once_with(name="new")

    async def test_handles_none_return(self, inject_bot):
        ch = _make_channel(id=102, name="unchanged")
        ch.edit = AsyncMock(return_value=None)
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["edit_channel"].fn(
            channel_id="102", name="unchanged"
        )

        assert result["name"] == "unchanged"

    async def test_edits_voice_channel_user_limit_and_bitrate(self, inject_bot):
        ch = _make_channel(id=103, name="vc", type="voice", bitrate=96000, user_limit=15)
        ch.edit = AsyncMock(return_value=ch)
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["edit_channel"].fn(
            channel_id="103", user_limit=15, bitrate=96000, reason="set limits"
        )

        assert result["user_limit"] == 15
        assert result["bitrate"] == 96000
        ch.edit.assert_awaited_once_with(user_limit=15, bitrate=96000, reason="set limits")

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None
        with pytest.raises(ValueError):
            await mcp._tool_manager._tools["edit_channel"].fn(channel_id="999")


class TestDeleteChannel:
    async def test_deletes_channel(self, inject_bot):
        ch = _make_channel(id=100, name="doomed")
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["delete_channel"].fn(channel_id="100", reason="bye")

        assert "doomed" in result
        ch.delete.assert_awaited_once_with(reason="bye")

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None
        with pytest.raises(ValueError):
            await mcp._tool_manager._tools["delete_channel"].fn(channel_id="999")


class TestSetChannelPermissions:
    async def test_sets_role_permissions(self, inject_bot):
        role = MagicMock()
        ch = _make_channel(id=100, name="secured")
        ch.guild.get_role.return_value = role
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["set_channel_permissions"].fn(
            channel_id="100",
            target_id="200",
            target_type="role",
            allow=["send_messages"],
            deny=["manage_messages"],
        )

        assert "Updated permissions" in result
        ch.set_permissions.assert_awaited_once()
        call_kwargs = ch.set_permissions.call_args
        overwrite = call_kwargs.kwargs["overwrite"]
        assert isinstance(overwrite, discord.PermissionOverwrite)

    async def test_sets_member_permissions(self, inject_bot):
        member = MagicMock()
        ch = _make_channel(id=100, name="secured")
        ch.guild.get_member.return_value = member
        inject_bot.get_channel.return_value = ch

        result = await mcp._tool_manager._tools["set_channel_permissions"].fn(
            channel_id="100",
            target_id="300",
            target_type="member",
            allow=["read_messages"],
        )

        assert "Updated permissions" in result

    async def test_fetches_member_if_not_cached(self, inject_bot):
        member = MagicMock()
        ch = _make_channel(id=100, name="secured")
        ch.guild.get_member.return_value = None
        ch.guild.fetch_member = AsyncMock(return_value=member)
        inject_bot.get_channel.return_value = ch

        await mcp._tool_manager._tools["set_channel_permissions"].fn(
            channel_id="100", target_id="300", target_type="member"
        )

        ch.guild.fetch_member.assert_awaited_once_with(300)  # int after conversion

    async def test_invalid_target_type(self, inject_bot):
        ch = _make_channel(id=100)
        inject_bot.get_channel.return_value = ch

        with pytest.raises(ValueError, match="target_type"):
            await mcp._tool_manager._tools["set_channel_permissions"].fn(
                channel_id="100", target_id="200", target_type="invalid"
            )

    async def test_role_not_found(self, inject_bot):
        ch = _make_channel(id=100)
        ch.guild.get_role.return_value = None
        inject_bot.get_channel.return_value = ch

        with pytest.raises(ValueError, match="Role"):
            await mcp._tool_manager._tools["set_channel_permissions"].fn(
                channel_id="100", target_id="200", target_type="role"
            )

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None
        with pytest.raises(ValueError):
            await mcp._tool_manager._tools["set_channel_permissions"].fn(
                channel_id="999", target_id="200", target_type="role"
            )
