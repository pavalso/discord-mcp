# Scheduled Events Tools -- discord.py API Reference

Tools in `discord_mcp/tools/scheduled_events.py` (4 tools).

---

## list_scheduled_events

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.scheduled_events` (property)

```python
events = guild.scheduled_events  # -> Sequence[ScheduledEvent]
```

For fresh data with user counts:
```python
events = await guild.fetch_scheduled_events(with_counts=True)  # -> List[ScheduledEvent]
```

**Key ScheduledEvent attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Event ID |
| `name` | `str` | Event name |
| `description` | `Optional[str]` | Event description |
| `entity_type` | `EntityType` | `stage_instance`, `voice`, `external` |
| `start_time` | `datetime` | Scheduled start time (UTC-aware) |
| `end_time` | `Optional[datetime]` | Scheduled end time |
| `status` | `EventStatus` | `scheduled`, `active`, `completed`, `cancelled` |
| `privacy_level` | `PrivacyLevel` | Privacy level |
| `user_count` | `int` | Interested user count |
| `creator` | `Optional[User]` | Event creator |
| `creator_id` | `Optional[int]` | Creator's user ID |
| `location` | `Optional[str]` | External event location |
| `channel` | `Optional[Union[VoiceChannel, StageChannel]]` | Channel for voice/stage events (property) |
| `guild` | `Optional[Guild]` | Owning guild (property) |
| `cover_image` | `Optional[Asset]` | Cover image (property) |
| `url` | `str` | Event URL (property) |

---

## create_scheduled_event

**Tool params:** `guild_id: int`, `name: str`, `start_time: str` (ISO 8601), `entity_type: str` ("stage_instance" | "voice" | "external"), `*, description: str | None = None`, `end_time: str | None = None` (ISO 8601), `channel_id: int | None = None`, `location: str | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.create_scheduled_event()`

```python
event = await guild.create_scheduled_event(
    *,
    name: str,
    start_time: datetime,           # Must be timezone-aware (UTC)
    entity_type: EntityType = ...,  # Determines required fields
    privacy_level: PrivacyLevel = ...,
    channel: Snowflake = ...,       # Required for voice/stage_instance
    location: str = ...,            # Required for external
    end_time: datetime = ...,       # Required for external, optional otherwise
    description: str = ...,
    image: bytes = ...,             # Cover image
    reason: str = None,
) -> ScheduledEvent
```

**Permissions:** `manage_events` required.

### Entity Type Requirements

| Entity Type | `channel_id` | `location` | `end_time` |
|------------|-------------|----------|----------|
| `stage_instance` | Required | N/A | Optional |
| `voice` | Required | N/A | Optional |
| `external` | N/A | Required | **Required** |

### EntityType Enum

```python
discord.EntityType.stage_instance  # Stage channel event
discord.EntityType.voice           # Voice channel event
discord.EntityType.external        # External/location-based event
```

### Datetime Conversion

```python
from datetime import datetime, timezone

# Parse ISO 8601 string to timezone-aware datetime
def parse_iso(iso_string: str) -> datetime:
    dt = datetime.fromisoformat(iso_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

start = parse_iso(start_time)
```

### Entity Type String Conversion

```python
ENTITY_TYPE_MAP = {
    "stage_instance": discord.EntityType.stage_instance,
    "voice": discord.EntityType.voice,
    "external": discord.EntityType.external,
}
```

**Usage:**
```python
kwargs = {
    "name": name,
    "start_time": parse_iso(start_time),
    "entity_type": ENTITY_TYPE_MAP[entity_type],
    "reason": reason,
}

if description:
    kwargs["description"] = description
if end_time:
    kwargs["end_time"] = parse_iso(end_time)
if channel_id:
    kwargs["channel"] = discord.Object(id=channel_id)
if location:
    kwargs["location"] = location

event = await guild.create_scheduled_event(**kwargs)
```

---

## edit_scheduled_event

**Tool params:** `guild_id: int`, `event_id: int`, `*, name: str | None = None`, `description: str | None = None`, `start_time: str | None = None` (ISO 8601), `end_time: str | None = None` (ISO 8601), `status: str | None = None` ("scheduled" | "active" | "completed" | "cancelled"), `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
event = guild.get_scheduled_event(event_id)
# or
event = await guild.fetch_scheduled_event(event_id)
```

#### `ScheduledEvent.edit()`

```python
event = await event.edit(
    *,
    name: str = ...,
    description: str = ...,
    channel: Optional[Snowflake] = ...,
    start_time: datetime = ...,         # Timezone-aware
    end_time: datetime = ...,           # Timezone-aware
    privacy_level: PrivacyLevel = ...,
    entity_type: EntityType = ...,
    status: EventStatus = ...,
    image: bytes = ...,
    location: str = ...,
    reason: str = None,
) -> ScheduledEvent
```

**Permissions:** `manage_events` required.

### EventStatus Enum and Transitions

```python
discord.EventStatus.scheduled   # Not started yet
discord.EventStatus.active      # Currently happening
discord.EventStatus.completed   # Ended (cannot transition back)
discord.EventStatus.cancelled   # Cancelled (cannot transition back)
```

**Valid status transitions:**
- `scheduled` -> `active` (start the event)
- `scheduled` -> `cancelled` (cancel before starting)
- `active` -> `completed` (end the event)

**Convenience methods (alternative to setting status):**
```python
await event.start(reason=reason)    # scheduled -> active
await event.end(reason=reason)      # active -> completed
await event.cancel(reason=reason)   # scheduled -> cancelled
```

### Status String Conversion

```python
EVENT_STATUS_MAP = {
    "scheduled": discord.EventStatus.scheduled,
    "active": discord.EventStatus.active,
    "completed": discord.EventStatus.completed,
    "cancelled": discord.EventStatus.cancelled,
}
```

---

## delete_scheduled_event

**Tool params:** `guild_id: int`, `event_id: int`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
event = guild.get_scheduled_event(event_id)
# or
event = await guild.fetch_scheduled_event(event_id)
```

#### `ScheduledEvent.delete()`

```python
await event.delete(*, reason: str = None)
```

**Permissions:** `manage_events` required.

**Raises:** `Forbidden`, `HTTPException`.

---

## Additional Reference: Event Users

Not currently a tool, but available:

```python
# Get users interested in an event
async for user in event.users(limit=100, oldest_first=True):
    print(user.name)
```

Returns `User` objects. Requires `Intents.members` for complete info.
