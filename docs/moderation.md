# Moderation Tools -- discord.py API Reference

Tools in `discord_mcp/tools/moderation.py` (6 tools).

---

## get_audit_log

**Tool params:** `guild_id: int`, `*, limit: int = 50`, `user_id: int | None = None`, `action_type: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.audit_logs()`

```python
async for entry in guild.audit_logs(
    *,
    limit: int = 100,                       # None = all entries
    before: Union[Snowflake, datetime] = ...,
    after: Union[Snowflake, datetime] = ...,
    oldest_first: bool = ...,               # True if `after` specified
    user: Snowflake = ...,                  # Filter by moderator
    action: AuditLogAction = ...,           # Filter by action type
) -> AsyncIterator[AuditLogEntry]
```

**Permissions:** `view_audit_log` required.

**Key AuditLogEntry attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Entry ID |
| `action` | `AuditLogAction` | Action performed |
| `user` | `Optional[User]` | Moderator who performed the action |
| `user_id` | `Optional[int]` | Moderator's user ID |
| `target` | `Any` | Target of the action (type varies) |
| `reason` | `Optional[str]` | Audit log reason |
| `extra` | `Any` | Extra info (action-dependent) |
| `created_at` | `datetime` | When the action occurred |
| `category` | `Optional[AuditLogActionCategory]` | `create`, `delete`, or `update` |
| `before` | `AuditLogDiff` | State before the action |
| `after` | `AuditLogDiff` | State after the action |
| `changes` | `AuditLogChanges` | Changes made |

### AuditLogAction Enum (Common Values)

```python
# Guild
discord.AuditLogAction.guild_update

# Channels
discord.AuditLogAction.channel_create
discord.AuditLogAction.channel_update
discord.AuditLogAction.channel_delete

# Permission overwrites
discord.AuditLogAction.overwrite_create
discord.AuditLogAction.overwrite_update
discord.AuditLogAction.overwrite_delete

# Members
discord.AuditLogAction.kick
discord.AuditLogAction.member_prune
discord.AuditLogAction.ban
discord.AuditLogAction.unban
discord.AuditLogAction.member_update
discord.AuditLogAction.member_role_update
discord.AuditLogAction.member_move
discord.AuditLogAction.member_disconnect
discord.AuditLogAction.bot_add

# Roles
discord.AuditLogAction.role_create
discord.AuditLogAction.role_update
discord.AuditLogAction.role_delete

# Invites
discord.AuditLogAction.invite_create
discord.AuditLogAction.invite_update
discord.AuditLogAction.invite_delete

# Webhooks
discord.AuditLogAction.webhook_create
discord.AuditLogAction.webhook_update
discord.AuditLogAction.webhook_delete

# Emojis/Stickers
discord.AuditLogAction.emoji_create
discord.AuditLogAction.emoji_update
discord.AuditLogAction.emoji_delete
discord.AuditLogAction.sticker_create
discord.AuditLogAction.sticker_update
discord.AuditLogAction.sticker_delete

# Messages
discord.AuditLogAction.message_delete
discord.AuditLogAction.message_bulk_delete
discord.AuditLogAction.message_pin
discord.AuditLogAction.message_unpin

# Threads
discord.AuditLogAction.thread_create
discord.AuditLogAction.thread_update
discord.AuditLogAction.thread_delete

# Scheduled Events
discord.AuditLogAction.scheduled_event_create
discord.AuditLogAction.scheduled_event_update
discord.AuditLogAction.scheduled_event_delete

# AutoMod
discord.AuditLogAction.automod_rule_create
discord.AuditLogAction.automod_rule_update
discord.AuditLogAction.automod_rule_delete
discord.AuditLogAction.automod_block_message
discord.AuditLogAction.automod_flag_message
discord.AuditLogAction.automod_timeout_member
```

### Action Type String Conversion

```python
ACTION_TYPE_MAP = {name: member for name, member in discord.AuditLogAction.__members__.items()}
# Usage: ACTION_TYPE_MAP.get(action_type_string)
# e.g., ACTION_TYPE_MAP["ban"] -> discord.AuditLogAction.ban
```

### Usage

```python
entries = []
kwargs = {"limit": limit}
if user_id:
    kwargs["user"] = discord.Object(id=user_id)
if action_type:
    kwargs["action"] = ACTION_TYPE_MAP[action_type]

async for entry in guild.audit_logs(**kwargs):
    entries.append(entry)
```

---

## list_bans

**Tool params:** `guild_id: int`, `*, limit: int = 100`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.bans()`

```python
async for ban_entry in guild.bans(
    *,
    limit: int = 1000,
    before: Snowflake = ...,
    after: Snowflake = ...,
) -> AsyncIterator[BanEntry]
```

**Permissions:** `ban_members` required.

**BanEntry is a NamedTuple:**

| Field | Type | Description |
|-------|------|-------------|
| `reason` | `Optional[str]` | Ban reason |
| `user` | `User` | Banned user |

**Usage:**
```python
bans = [entry async for entry in guild.bans(limit=limit)]
# Access: entry.user, entry.reason
```

**Single ban lookup:**
```python
ban = await guild.fetch_ban(discord.Object(id=user_id))  # -> BanEntry
# Raises NotFound if user is not banned
```

---

## purge_messages

**Tool params:** `channel_id: int`, `limit: int`, `*, user_id: int | None = None`, `contains: str | None = None`, `before_message_id: int | None = None`, `after_message_id: int | None = None`, `reason: str | None = None`

### API Calls

```python
channel = bot.get_channel(channel_id)
```

#### `TextChannel.purge()` / `Thread.purge()`

```python
deleted = await channel.purge(
    *,
    limit: int = 100,
    check: Callable[[Message], bool] = ...,     # Filter function
    before: Union[Snowflake, datetime] = None,
    after: Union[Snowflake, datetime] = None,
    around: Union[Snowflake, datetime] = None,
    oldest_first: bool = None,
    bulk: bool = True,                          # Use bulk delete API
    reason: str = None,
) -> List[Message]
```

**Permissions:** `manage_messages` and `read_message_history` required.

**Returns:** `List[Message]` -- the messages that were deleted.

### Building the Check Function

```python
def make_check(user_id=None, contains=None):
    def check(message: discord.Message) -> bool:
        if user_id and message.author.id != user_id:
            return False
        if contains and contains not in message.content:
            return False
        return True
    return check

kwargs = {"limit": limit, "reason": reason}

if user_id or contains:
    kwargs["check"] = make_check(user_id=user_id, contains=contains)
if before_message_id:
    kwargs["before"] = discord.Object(id=before_message_id)
if after_message_id:
    kwargs["after"] = discord.Object(id=after_message_id)

deleted = await channel.purge(**kwargs)
```

**Notes:**
- `bulk=True` (default) uses Discord's bulk delete endpoint, which is faster but only works on messages less than 14 days old.
- If messages are older than 14 days, they are deleted individually (slower, rate-limited).
- Max bulk delete: 100 messages per API call. `purge()` handles pagination internally.
- The `check` function is called for each message. Return `True` to delete, `False` to keep.

---

## list_automod_rules

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.fetch_automod_rules()`

```python
rules = await guild.fetch_automod_rules()  # -> List[AutoModRule]
```

**Permissions:** `manage_guild` required.

**Key AutoModRule attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Rule ID |
| `name` | `str` | Rule name |
| `guild` | `Guild` | Owning guild |
| `creator_id` | `int` | Creator's user ID |
| `trigger` | `AutoModTrigger` | Trigger configuration |
| `enabled` | `bool` | Whether enabled |
| `event_type` | `AutoModRuleEventType` | `message_send` or `member_update` |
| `actions` | `List[AutoModRuleAction]` | Actions taken when triggered (property) |
| `exempt_role_ids` | `Set[int]` | Exempt role IDs |
| `exempt_channel_ids` | `Set[int]` | Exempt channel IDs |
| `exempt_roles` | `List[Role]` | Exempt roles (property) |
| `exempt_channels` | `List[Channel]` | Exempt channels (property) |
| `creator` | `Optional[Member]` | Creator member (property) |

**AutoModTrigger attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | `AutoModRuleTriggerType` | `keyword`, `spam`, `keyword_preset`, `mention_spam`, `member_profile` |
| `keyword_filter` | `List[str]` | Trigger keywords (max 1000, each up to 60 chars) |
| `regex_patterns` | `List[str]` | Regex patterns (max 10, each up to 260 chars, Rust syntax) |
| `presets` | `AutoModPresets` | Preset filters (profanity, sexual_content, slurs) |
| `allow_list` | `List[str]` | Exempt words |
| `mention_limit` | `int` | Max mentions before triggering (max 50) |
| `mention_raid_protection` | `bool` | Mention raid protection enabled |

---

## create_automod_rule

**Tool params:** `guild_id: int`, `name: str`, `trigger_type: str` ("keyword" | "spam" | "keyword_preset" | "mention_spam"), `actions: list[dict]`, `*, enabled: bool = True`, `keyword_filter: list[str] | None = None`, `regex_patterns: list[str] | None = None`, `exempt_role_ids: list[int] | None = None`, `exempt_channel_ids: list[int] | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.create_automod_rule()`

```python
rule = await guild.create_automod_rule(
    *,
    name: str,
    event_type: AutoModRuleEventType,
    trigger: AutoModTrigger,
    actions: List[AutoModRuleAction],
    enabled: bool = False,
    exempt_roles: Sequence[Snowflake] = ...,
    exempt_channels: Sequence[Snowflake] = ...,
    reason: str = ...,
) -> AutoModRule
```

**Permissions:** `manage_guild` required.

### Building the Trigger

```python
TRIGGER_TYPE_MAP = {
    "keyword": discord.AutoModRuleTriggerType.keyword,
    "spam": discord.AutoModRuleTriggerType.spam,
    "keyword_preset": discord.AutoModRuleTriggerType.keyword_preset,
    "mention_spam": discord.AutoModRuleTriggerType.mention_spam,
}

# Keyword trigger
trigger = discord.AutoModTrigger(
    type=TRIGGER_TYPE_MAP[trigger_type],
    keyword_filter=keyword_filter,          # For "keyword" type
    regex_patterns=regex_patterns,          # For "keyword" type
)

# Keyword preset trigger
trigger = discord.AutoModTrigger(
    type=discord.AutoModRuleTriggerType.keyword_preset,
    presets=discord.AutoModPresets(profanity=True, sexual_content=True, slurs=True),
)

# Mention spam trigger
trigger = discord.AutoModTrigger(
    type=discord.AutoModRuleTriggerType.mention_spam,
    mention_limit=5,
)
```

### Building Actions

Actions come as `list[dict]` from the tool. Each dict has a `type` and type-specific fields:

```python
def build_action(action_dict: dict) -> discord.AutoModRuleAction:
    action_type = action_dict["type"]
    
    if action_type == "block_message":
        return discord.AutoModRuleAction(
            custom_message=action_dict.get("custom_message"),
        )
    elif action_type == "send_alert_message":
        return discord.AutoModRuleAction(
            channel_id=action_dict["channel_id"],
        )
    elif action_type == "timeout":
        import datetime
        return discord.AutoModRuleAction(
            duration=datetime.timedelta(seconds=action_dict["duration_seconds"]),
        )
    else:
        return discord.AutoModRuleAction()

actions_list = [build_action(a) for a in actions]
```

### AutoModRuleAction Types

| Type | Parameters | Description |
|------|-----------|-------------|
| `block_message` | `custom_message: Optional[str]` | Block the message |
| `send_alert_message` | `channel_id: int` | Send alert to a channel |
| `timeout` | `duration: timedelta` | Timeout the user (max 28 days) |
| `block_member_interactions` | (none) | Block member interactions |

### Full Usage

```python
trigger = discord.AutoModTrigger(
    type=TRIGGER_TYPE_MAP[trigger_type],
    keyword_filter=keyword_filter,
    regex_patterns=regex_patterns,
)

actions_list = [build_action(a) for a in actions]

exempt_roles_objs = [discord.Object(id=rid) for rid in (exempt_role_ids or [])]
exempt_channels_objs = [discord.Object(id=cid) for cid in (exempt_channel_ids or [])]

rule = await guild.create_automod_rule(
    name=name,
    event_type=discord.AutoModRuleEventType.message_send,
    trigger=trigger,
    actions=actions_list,
    enabled=enabled,
    exempt_roles=exempt_roles_objs,
    exempt_channels=exempt_channels_objs,
    reason=reason,
)
```

### Trigger Type Limits

| Trigger Type | Max Rules per Guild |
|-------------|-------------------|
| `keyword` | 6 |
| `spam` | 1 |
| `keyword_preset` | 1 |
| `mention_spam` | 1 |
| `member_profile` | 1 |

---

## delete_automod_rule

**Tool params:** `guild_id: int`, `rule_id: int`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
rule = await guild.fetch_automod_rule(rule_id)
```

#### `AutoModRule.delete()`

```python
await rule.delete(*, reason: str = None)
```

**Permissions:** `manage_guild` required.

**Raises:** `Forbidden`, `HTTPException`.
