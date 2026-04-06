# Roles Tools -- discord.py API Reference

Tools in `discord_mcp/tools/roles.py` (5 tools).

---

## list_roles

**Tool params:** `guild_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.roles` (property)

```python
roles = guild.roles  # -> Sequence[Role]
```

Returns all roles sorted by hierarchy (lowest first, `@everyone` at index 0).

**Key Role attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | Role ID |
| `name` | `str` | Role name |
| `color` / `colour` | `Colour` | Role color (`.value` for int) |
| `hoist` | `bool` | Displayed separately in member list |
| `position` | `int` | Position in hierarchy |
| `permissions` | `Permissions` | Role permissions |
| `managed` | `bool` | Managed by an integration (e.g., bot role) |
| `mentionable` | `bool` | Can be mentioned by everyone |
| `unicode_emoji` | `Optional[str]` | Unicode emoji icon |
| `icon` | `Optional[Asset]` | Custom icon image |
| `tags` | `Optional[RoleTags]` | Special role tags |
| `members` | `List[Member]` | Members with this role |
| `created_at` | `datetime` | Creation timestamp |

**Useful bool checks:**
- `role.is_default()` -- `@everyone` role
- `role.is_bot_managed()` -- Auto-created for a bot
- `role.is_premium_subscriber()` -- Nitro Booster role
- `role.is_integration()` -- Managed by an integration
- `role.is_assignable()` -- Can the bot assign this role

**Hierarchy comparison:**
```python
# Use comparison operators, NOT .position
role_a > role_b  # role_a is higher in hierarchy
role_a < role_b  # role_a is lower
# Multiple roles can share the same .position value!
```

---

## get_role

**Tool params:** `guild_id: int`, `role_id: int`

### API Calls

```python
guild = bot.get_guild(guild_id)
role = guild.get_role(role_id)  # -> Optional[Role]
```

Cache lookup, no API call. Returns `None` if role not found.

---

## create_role

**Tool params:** `guild_id: int`, `name: str`, `*, color: int | None = None`, `hoist: bool = False`, `mentionable: bool = False`, `permissions: list[str] | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
```

#### `Guild.create_role()`

```python
await guild.create_role(
    *,
    name: str = ...,
    permissions: Permissions = ...,
    color: Union[Colour, int] = ...,        # or colour
    hoist: bool = ...,
    display_icon: Union[bytes, str] = ...,  # Image bytes or unicode emoji
    mentionable: bool = ...,
    reason: str = None,
) -> Role
```

**Permissions:** `manage_roles` required.

**Converting permission strings to Permissions:**
```python
perms = discord.Permissions()
if permissions:
    perms = discord.Permissions(**{p: True for p in permissions})
```

**Converting color int:**
```python
# Color as integer (e.g., 0xFF0000 for red)
color_obj = discord.Colour(color) if color else discord.Colour.default()
```

**Returns:** The created `Role`.

**Notes:**
- New roles are created at the bottom of the hierarchy (position 1, just above `@everyone`).
- Max 250 roles per guild.

---

## edit_role

**Tool params:** `guild_id: int`, `role_id: int`, `*, name: str | None = None`, `color: int | None = None`, `hoist: bool | None = None`, `mentionable: bool | None = None`, `permissions: list[str] | None = None`, `reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
role = guild.get_role(role_id)
```

#### `Role.edit()`

```python
await role.edit(
    *,
    name: str = ...,
    permissions: Permissions = ...,
    color: Union[Colour, int] = ...,
    colour: Union[Colour, int] = ...,
    hoist: bool = ...,
    display_icon: Union[bytes, str] = ...,
    mentionable: bool = ...,
    position: int = ...,
    reason: str = ...,
) -> Role
```

**Permissions:** `manage_roles`. Bot's top role must be above the target role.

**Notes:**
- Cannot edit roles above the bot's highest role.
- Cannot edit the `@everyone` role's permissions to add `administrator`.
- Editing `position` requires careful handling -- consider using `Role.move()` instead.
- The `managed` and `is_bot_managed()` roles cannot be edited.

**Position management (alternative):**
```python
await role.move(
    *,
    beginning: bool = ...,   # Move to top (below bot's role)
    end: bool = ...,          # Move to bottom (above @everyone)
    above: Role = ...,        # Move above this role
    below: Role = ...,        # Move below this role
    offset: int = 0,          # Additional offset
    reason: str = None,
) -> List[Role]
```

---

## delete_role

**Tool params:** `guild_id: int`, `role_id: int`, `*, reason: str | None = None`

### API Calls

```python
guild = bot.get_guild(guild_id)
role = guild.get_role(role_id)
```

#### `Role.delete()`

```python
await role.delete(*, reason: str = None)
```

**Permissions:** `manage_roles`. Bot's top role must be above the target role.

**Raises:** `Forbidden`, `HTTPException`.

**Warning:** Cannot delete managed roles (bot roles, integration roles, Nitro Booster role). Check `role.managed` before attempting.
