# Permissions Reference

## discord.Permissions

A 53-bit integer bit field. Each permission is a boolean flag. All tool parameters that accept permission names use these as strings.

### All Permission Flags

| Permission Name | Description | Category |
|----------------|-------------|----------|
| `create_instant_invite` | Create channel invites | General |
| `kick_members` | Kick members | General |
| `ban_members` | Ban members | General |
| `administrator` | All permissions, bypass channel overwrites | General |
| `manage_channels` | Create/edit/delete channels | General |
| `manage_guild` | Edit guild settings | General |
| `add_reactions` | Add reactions to messages | Text |
| `view_audit_log` | View audit log | General |
| `priority_speaker` | Priority speaker in voice | Voice |
| `stream` | Go Live in voice channels | Voice |
| `view_channel` / `read_messages` | View channels (both names work) | General |
| `send_messages` | Send messages in text channels | Text |
| `send_tts_messages` | Send TTS messages | Text |
| `manage_messages` | Delete/pin others' messages | Text |
| `embed_links` | Auto-embed links | Text |
| `attach_files` | Upload files | Text |
| `read_message_history` | Read message history | Text |
| `mention_everyone` | @everyone and @here | Text |
| `use_external_emojis` / `external_emojis` | Use emojis from other servers | Text |
| `view_guild_insights` | View guild insights | General |
| `connect` | Connect to voice channels | Voice |
| `speak` | Speak in voice channels | Voice |
| `mute_members` | Mute members in voice | Voice |
| `deafen_members` | Deafen members in voice | Voice |
| `move_members` | Move members between voice channels | Voice |
| `use_voice_activation` | Use voice activity detection | Voice |
| `change_nickname` | Change own nickname | General |
| `manage_nicknames` | Change other members' nicknames | General |
| `manage_roles` / `manage_permissions` | Manage roles and channel permissions | General |
| `manage_webhooks` | Create/edit/delete webhooks | General |
| `manage_expressions` / `manage_emojis` / `manage_emojis_and_stickers` | Manage emojis, stickers, soundboard | General |
| `use_application_commands` | Use slash commands | Text |
| `request_to_speak` | Request to speak in stage channels | Stage |
| `manage_events` | Create/edit/delete scheduled events | Events |
| `manage_threads` | Delete/archive/edit threads | Text |
| `create_public_threads` | Create public threads | Text |
| `create_private_threads` | Create private threads | Text |
| `use_external_stickers` / `external_stickers` | Use stickers from other servers | Text |
| `send_messages_in_threads` | Send messages in threads | Text |
| `use_embedded_activities` | Use activities in voice channels | Voice |
| `moderate_members` | Timeout members | General |
| `view_creator_monetization_analytics` | View monetization analytics | General |
| `use_soundboard` | Use soundboard in voice | Voice |
| `create_expressions` | Create emojis, stickers, soundboard sounds | General |
| `create_events` | Create scheduled events | Events |
| `use_external_sounds` | Use sounds from other servers | Voice |
| `send_voice_messages` | Send voice messages | Text |
| `set_voice_channel_status` | Set voice channel status | Voice |
| `send_polls` / `create_polls` | Create polls | Text |
| `use_external_apps` | Use external apps | Apps |
| `pin_messages` | Pin messages in channels | Text |
| `bypass_slowmode` | Bypass slowmode restrictions | Text |

### Preset Permission Groups

```python
discord.Permissions.none()              # All False
discord.Permissions.all()               # All True
discord.Permissions.all_channel()       # All channel-specific
discord.Permissions.general()           # "General" UI section
discord.Permissions.membership()        # "Membership" UI section
discord.Permissions.text()              # "Text" UI section
discord.Permissions.voice()             # "Voice" UI section
discord.Permissions.stage()             # "Stage Channel" UI section
discord.Permissions.stage_moderator()   # manage_channels + mute_members + move_members
discord.Permissions.elevated()          # All perms requiring 2FA
discord.Permissions.apps()              # "Apps" UI section
discord.Permissions.events()            # "Events" UI section
discord.Permissions.advanced()          # "Advanced" UI section (administrator)
```

### Creating Permissions from Strings

```python
# From a list of permission name strings
def permissions_from_strings(perm_names: list[str]) -> discord.Permissions:
    return discord.Permissions(**{name: True for name in perm_names})

# Example
perms = permissions_from_strings(["send_messages", "read_messages", "add_reactions"])
```

### Checking Permissions

```python
perms = member.guild_permissions

perms.administrator          # True/False
perms.manage_channels        # True/False

# Check multiple
perms.is_superset(discord.Permissions(send_messages=True, read_messages=True))

# Iterate all set permissions
for perm, value in perms:
    if value:
        print(perm)
```

---

## discord.PermissionOverwrite

Channel-specific permission overrides. Unlike `Permissions`, values are tristate: `True` (allow), `False` (deny), `None` (inherit).

### Creating Overwrites

```python
# From kwargs
overwrite = discord.PermissionOverwrite(
    send_messages=True,       # Explicitly allow
    manage_messages=False,    # Explicitly deny
    # everything else = None (inherit from role)
)

# From allow/deny lists
overwrite = discord.PermissionOverwrite()
for perm in allow_list:
    setattr(overwrite, perm, True)
for perm in deny_list:
    setattr(overwrite, perm, False)
```

### Converting to/from Permissions Pair

```python
# Get the allow/deny Permissions objects
allow, deny = overwrite.pair()

# Create from allow/deny
overwrite = discord.PermissionOverwrite.from_pair(allow_perms, deny_perms)
```

### Applying to Channels

```python
# Set overwrite for a role or member
await channel.set_permissions(
    target,                     # Role or Member
    overwrite=overwrite,
    reason="Updated permissions",
)

# Or use keyword arguments directly
await channel.set_permissions(
    target,
    send_messages=True,
    manage_messages=False,
    reason="Updated permissions",
)

# Remove all overwrites for a target
await channel.set_permissions(target, overwrite=None)
```

### Reading Channel Overwrites

```python
# Get all overwrites
overwrites = channel.overwrites  # Dict[Union[Role, Member, Object], PermissionOverwrite]

# Get overwrite for specific target
ow = channel.overwrites_for(role_or_member)  # -> PermissionOverwrite

# Resolve effective permissions
effective = channel.permissions_for(member)  # -> Permissions
```

---

## Permission Hierarchy

Discord resolves permissions in this order:

1. **Administrator** overrides everything (always grants all permissions)
2. **Guild-level role permissions** are unioned across all of the member's roles
3. **Channel-level @everyone overwrite** is applied
4. **Channel-level role overwrites** are unioned, then applied
5. **Channel-level member overwrite** is applied last (highest priority)

The bot can only manage roles and overwrites **below its highest role** in the hierarchy.
