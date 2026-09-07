"""Tests for message tools — verifies registration, schemas, and behavior."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.fastmcp import FastMCP

from discord_mcp.server import mcp
from discord_mcp.tools.messages import register

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_message(
    *,
    id: int = 1000,
    content: str = "hello",
    author_id: int = 42,
    author_name: str = "alice",
    channel_id: int = 100,
    pinned: bool = False,
    tts: bool = False,
):
    msg = MagicMock()
    msg.id = id
    msg.content = content
    msg.author.id = author_id
    msg.author.name = author_name
    msg.channel.id = channel_id
    msg.created_at = "2026-01-01T00:00:00+00:00"
    msg.edited_at = None
    msg.pinned = pinned
    msg.tts = tts
    msg.type = "default"
    msg.jump_url = f"https://discord.com/channels/1/{channel_id}/{id}"
    msg.attachments = []
    msg.embeds = []
    msg.edit = AsyncMock(return_value=msg)
    msg.delete = AsyncMock()
    msg.pin = AsyncMock()
    msg.unpin = AsyncMock()
    msg.add_reaction = AsyncMock()
    msg.remove_reaction = AsyncMock()
    msg.clear_reactions = AsyncMock()
    msg.clear_reaction = AsyncMock()
    return msg


def _tool_fn(name: str):
    return mcp._tool_manager._tools[name].fn


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


class TestMessageToolsRegistration:
    EXPECTED: ClassVar[set[str]] = {
        "send_message",
        "send_file",
        "send_embed",
        "edit_message",
        "delete_message",
        "get_message",
        "get_message_history",
        "pin_message",
        "unpin_message",
        "get_pinned_messages",
        "add_reaction",
        "remove_reaction",
        "clear_reactions",
    }

    def test_register_adds_all_tools(self):
        test_mcp = FastMCP("test")
        register(test_mcp)
        names = {t.name for t in test_mcp._tool_manager.list_tools()}
        assert names == self.EXPECTED

    def test_register_is_idempotent_on_main_server(self):
        names = {t.name for t in mcp._tool_manager.list_tools()}
        assert names >= self.EXPECTED


# ---------------------------------------------------------------------------
# Tool input schemas
# ---------------------------------------------------------------------------


def _get_tool_schema(name: str) -> dict:
    for t in mcp._tool_manager.list_tools():
        if t.name == name:
            return t.parameters
    raise KeyError(name)


class TestMessageToolSchemas:
    def test_send_message_requires_channel_and_content(self):
        schema = _get_tool_schema("send_message")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "content" in required

    def test_edit_message_requires_channel_message_content(self):
        schema = _get_tool_schema("edit_message")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "message_id" in required
        assert "content" in required

    def test_delete_message_requires_channel_and_message(self):
        schema = _get_tool_schema("delete_message")
        required = schema.get("required", [])
        assert "channel_id" in required
        assert "message_id" in required

    def test_get_message_history_has_limit_default(self):
        schema = _get_tool_schema("get_message_history")
        props = schema.get("properties", {})
        assert "limit" in props

    def test_add_reaction_requires_emoji(self):
        schema = _get_tool_schema("add_reaction")
        required = schema.get("required", [])
        assert "emoji" in required
        assert "channel_id" in required
        assert "message_id" in required

    def test_remove_reaction_user_id_optional(self):
        schema = _get_tool_schema("remove_reaction")
        required = schema.get("required", [])
        assert "user_id" not in required

    def test_send_embed_requires_channel_id(self):
        schema = _get_tool_schema("send_embed")
        required = schema.get("required", [])
        assert "channel_id" in required

    def test_send_embed_has_optional_fields(self):
        schema = _get_tool_schema("send_embed")
        props = schema.get("properties", {})
        for key in (
            "title",
            "description",
            "color",
            "fields",
            "footer_text",
            "image_url",
            "thumbnail_url",
        ):
            assert key in props
        required = schema.get("required", [])
        assert "title" not in required
        assert "description" not in required

    def test_clear_reactions_emoji_optional(self):
        schema = _get_tool_schema("clear_reactions")
        required = schema.get("required", [])
        assert "emoji" not in required


# ---------------------------------------------------------------------------
# Behavior tests
# ---------------------------------------------------------------------------


class TestSendMessage:
    async def test_sends_basic_message(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("send_message")(channel_id="100", content="hello")

        channel.send.assert_awaited_once()
        call_kwargs = channel.send.call_args.kwargs
        assert call_kwargs["content"] == "hello"
        assert call_kwargs["tts"] is False
        assert result["id"] == "1000"
        assert result["content"] == "hello"

    async def test_sends_reply(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_message")(channel_id="100", content="reply", reply_to_message_id="999")

        call_kwargs = channel.send.call_args.kwargs
        assert call_kwargs["reference"].message_id == 999

    async def test_sends_tts(self, inject_bot):
        msg = _make_message(tts=True)
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_message")(channel_id="100", content="tts", tts=True)

        call_kwargs = channel.send.call_args.kwargs
        assert call_kwargs["tts"] is True

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("send_message")(channel_id="999", content="hi")


class TestSendFile:
    async def test_sends_local_file(self, inject_bot, tmp_path):
        path = tmp_path / "notes.txt"
        path.write_bytes(b"hello from disk")
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("send_file")(channel_id="100", file_paths=[str(path)])

        call_kwargs = channel.send.call_args.kwargs
        files = call_kwargs["files"]
        assert len(files) == 1
        assert files[0].filename == "notes.txt"
        assert files[0].fp.read() == b"hello from disk"
        # content is only sent when given, so an attachment-only message stays empty.
        assert "content" not in call_kwargs
        assert result["id"] == "1000"

    async def test_sends_several_files_with_content(self, inject_bot, tmp_path):
        first = tmp_path / "a.txt"
        second = tmp_path / "b.txt"
        first.write_bytes(b"a")
        second.write_bytes(b"b")
        channel = MagicMock()
        channel.send = AsyncMock(return_value=_make_message())
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_file")(
            channel_id="100", file_paths=[str(first), str(second)], content="two files"
        )

        call_kwargs = channel.send.call_args.kwargs
        assert [f.filename for f in call_kwargs["files"]] == ["a.txt", "b.txt"]
        assert call_kwargs["content"] == "two files"

    async def test_marks_spoilers(self, inject_bot, tmp_path):
        path = tmp_path / "secret.png"
        path.write_bytes(b"img")
        channel = MagicMock()
        channel.send = AsyncMock(return_value=_make_message())
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_file")(channel_id="100", file_paths=[str(path)], spoiler=True)

        sent = channel.send.call_args.kwargs["files"][0]
        assert sent.filename == "SPOILER_secret.png"

    async def test_sends_reply(self, inject_bot, tmp_path):
        path = tmp_path / "a.txt"
        path.write_bytes(b"a")
        channel = MagicMock()
        channel.send = AsyncMock(return_value=_make_message())
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_file")(
            channel_id="100", file_paths=[str(path)], reply_to_message_id="999"
        )

        assert channel.send.call_args.kwargs["reference"].message_id == 999

    @patch("discord_mcp.tools.messages.aiohttp.ClientSession")
    async def test_downloads_url_and_reuploads(self, mock_session_cls, inject_bot):
        channel = MagicMock()
        channel.send = AsyncMock(return_value=_make_message())
        inject_bot.get_channel.return_value = channel

        resp = MagicMock()
        resp.read = AsyncMock(return_value=b"downloaded-bytes")
        resp.raise_for_status = MagicMock()
        session = MagicMock()
        session.get = MagicMock(
            return_value=MagicMock(
                __aenter__=AsyncMock(return_value=resp),
                __aexit__=AsyncMock(return_value=False),
            )
        )
        mock_session_cls.return_value = MagicMock(
            __aenter__=AsyncMock(return_value=session),
            __aexit__=AsyncMock(return_value=False),
        )

        await _tool_fn("send_file")(
            channel_id="100", file_paths=["https://example.com/pics/cat%20photo.png"]
        )

        sent = channel.send.call_args.kwargs["files"][0]
        # The URL-encoded name is decoded, and the query-free basename is used.
        assert sent.filename == "cat photo.png"
        assert sent.fp.read() == b"downloaded-bytes"

    async def test_rejects_empty_list(self, inject_bot):
        with pytest.raises(ValueError, match="at least one file"):
            await _tool_fn("send_file")(channel_id="100", file_paths=[])

    async def test_rejects_more_than_ten(self, inject_bot):
        with pytest.raises(ValueError, match="at most 10 attachments"):
            await _tool_fn("send_file")(channel_id="100", file_paths=[f"f{i}" for i in range(11)])

    async def test_rejects_missing_file(self, inject_bot, tmp_path):
        channel = MagicMock()
        inject_bot.get_channel.return_value = channel

        missing = str(tmp_path / "nope.txt")
        with pytest.raises(ValueError, match="not an existing file or an http"):
            await _tool_fn("send_file")(channel_id="100", file_paths=[missing])

    async def test_channel_not_found(self, inject_bot, tmp_path):
        path = tmp_path / "a.txt"
        path.write_bytes(b"a")
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("send_file")(channel_id="999", file_paths=[str(path)])


class TestSendEmbed:
    async def test_sends_basic_embed(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("send_embed")(
            channel_id="100", title="Hello", description="World", color=0xFF5733
        )

        channel.send.assert_awaited_once()
        call_kwargs = channel.send.call_args.kwargs
        embed = call_kwargs["embed"]
        assert embed.title == "Hello"
        assert embed.description == "World"
        assert embed.color.value == 0xFF5733
        assert call_kwargs["content"] is None
        assert result["id"] == "1000"

    async def test_sends_embed_with_fields(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        fields = [
            {"name": "Field 1", "value": "Value 1", "inline": True},
            {"name": "Field 2", "value": "Value 2"},
        ]
        await _tool_fn("send_embed")(channel_id="100", fields=fields)

        embed = channel.send.call_args.kwargs["embed"]
        assert len(embed.fields) == 2
        assert embed.fields[0].name == "Field 1"
        assert embed.fields[0].inline is True
        assert embed.fields[1].inline is False

    async def test_sends_embed_with_footer_and_image(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_embed")(
            channel_id="100",
            title="Test",
            footer_text="Footer here",
            image_url="https://example.com/image.png",
            thumbnail_url="https://example.com/thumb.png",
        )

        embed = channel.send.call_args.kwargs["embed"]
        assert embed.footer.text == "Footer here"
        assert embed.image.url == "https://example.com/image.png"
        assert embed.thumbnail.url == "https://example.com/thumb.png"

    async def test_sends_embed_with_author(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_embed")(
            channel_id="100",
            author_name="Author",
            author_url="https://example.com",
            author_icon_url="https://example.com/icon.png",
        )

        embed = channel.send.call_args.kwargs["embed"]
        assert embed.author.name == "Author"
        assert embed.author.url == "https://example.com"
        assert embed.author.icon_url == "https://example.com/icon.png"

    async def test_sends_embed_with_content(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        await _tool_fn("send_embed")(channel_id="100", title="Hi", content="Extra text")

        call_kwargs = channel.send.call_args.kwargs
        assert call_kwargs["content"] == "Extra text"

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("send_embed")(channel_id="999", title="Hi")


class TestEditMessage:
    async def test_edits_message(self, inject_bot):
        msg = _make_message(content="edited")
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("edit_message")(
            channel_id="100", message_id="1000", content="edited"
        )

        msg.edit.assert_awaited_once_with(content="edited")
        assert result["id"] == "1000"

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("edit_message")(channel_id="999", message_id="1", content="x")


class TestDeleteMessage:
    async def test_deletes_message(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("delete_message")(channel_id="100", message_id="1000")

        msg.delete.assert_awaited_once()
        assert "Deleted" in result

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("delete_message")(channel_id="999", message_id="1")


class TestGetMessage:
    async def test_fetches_message(self, inject_bot):
        msg = _make_message(id=500, content="found it")
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("get_message")(channel_id="100", message_id="500")

        channel.fetch_message.assert_awaited_once_with(500)
        assert result["id"] == "500"
        assert result["content"] == "found it"

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("get_message")(channel_id="999", message_id="1")


class TestGetMessageHistory:
    async def test_returns_messages(self, inject_bot):
        msg1 = _make_message(id=1, content="first")
        msg2 = _make_message(id=2, content="second")
        channel = MagicMock()

        async def mock_history(**kwargs):
            for m in [msg1, msg2]:
                yield m

        channel.history = mock_history
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("get_message_history")(channel_id="100")

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

    async def test_passes_before_after(self, inject_bot):
        channel = MagicMock()
        captured_kwargs = {}

        async def mock_history(**kwargs):
            captured_kwargs.update(kwargs)
            return
            yield  # make it an async generator

        channel.history = mock_history
        inject_bot.get_channel.return_value = channel

        await _tool_fn("get_message_history")(
            channel_id="100", limit=10, before_message_id="500", after_message_id="100"
        )

        assert captured_kwargs["limit"] == 10
        assert captured_kwargs["before"].id == 500
        assert captured_kwargs["after"].id == 100

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("get_message_history")(channel_id="999")


class TestPinMessage:
    async def test_pins_message(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("pin_message")(channel_id="100", message_id="1000")

        msg.pin.assert_awaited_once()
        assert "Pinned" in result

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("pin_message")(channel_id="999", message_id="1")


class TestUnpinMessage:
    async def test_unpins_message(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("unpin_message")(channel_id="100", message_id="1000")

        msg.unpin.assert_awaited_once()
        assert "Unpinned" in result

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("unpin_message")(channel_id="999", message_id="1")


class TestGetPinnedMessages:
    async def test_returns_pinned(self, inject_bot):
        msg1 = _make_message(id=1, pinned=True)
        msg2 = _make_message(id=2, pinned=True)
        channel = MagicMock()

        async def mock_pins():
            for m in [msg1, msg2]:
                yield m

        channel.pins = mock_pins
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("get_pinned_messages")(channel_id="100")

        assert len(result) == 2
        assert result[0]["pinned"] is True

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("get_pinned_messages")(channel_id="999")


class TestAddReaction:
    async def test_adds_reaction(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("add_reaction")(channel_id="100", message_id="1000", emoji="👍")

        msg.add_reaction.assert_awaited_once_with("👍")
        assert "Added" in result

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("add_reaction")(channel_id="999", message_id="1", emoji="👍")


class TestRemoveReaction:
    async def test_removes_bot_reaction(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("remove_reaction")(channel_id="100", message_id="1000", emoji="👍")

        msg.remove_reaction.assert_awaited_once_with("👍", inject_bot.user)
        assert "Removed" in result

    async def test_removes_user_reaction(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        await _tool_fn("remove_reaction")(
            channel_id="100", message_id="1000", emoji="👍", user_id="42"
        )

        call_args = msg.remove_reaction.call_args
        assert call_args[0][0] == "👍"
        assert call_args[0][1].id == 42

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("remove_reaction")(channel_id="999", message_id="1", emoji="👍")


class TestClearReactions:
    async def test_clears_all_reactions(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("clear_reactions")(channel_id="100", message_id="1000")

        msg.clear_reactions.assert_awaited_once()
        assert "all reactions" in result

    async def test_clears_specific_emoji(self, inject_bot):
        msg = _make_message()
        channel = MagicMock()
        channel.fetch_message = AsyncMock(return_value=msg)
        inject_bot.get_channel.return_value = channel

        result = await _tool_fn("clear_reactions")(channel_id="100", message_id="1000", emoji="👍")

        msg.clear_reaction.assert_awaited_once_with("👍")
        assert "👍" in result

    async def test_channel_not_found(self, inject_bot):
        inject_bot.get_channel.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await _tool_fn("clear_reactions")(channel_id="999", message_id="1")
