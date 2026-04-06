# Enums Reference

Common discord.py enums used across the MCP tools.

---

## ChannelType

```python
discord.ChannelType.text            # 0 - Text channel
discord.ChannelType.private         # 1 - DM channel
discord.ChannelType.voice           # 2 - Voice channel
discord.ChannelType.group           # 3 - Group DM
discord.ChannelType.category        # 4 - Category
discord.ChannelType.news            # 5 - Announcement channel
discord.ChannelType.news_thread     # 10 - Thread in news channel
discord.ChannelType.public_thread   # 11 - Public thread
discord.ChannelType.private_thread  # 12 - Private thread
discord.ChannelType.stage_voice     # 13 - Stage channel
discord.ChannelType.forum           # 15 - Forum channel
discord.ChannelType.media           # 16 - Media channel
```

---

## VerificationLevel

Used in `edit_guild` tool.

```python
discord.VerificationLevel.none      # No requirements
discord.VerificationLevel.low       # Verified email
discord.VerificationLevel.medium    # Registered for 5+ minutes
discord.VerificationLevel.high      # Member for 10+ minutes (aka "tableflip")
discord.VerificationLevel.highest   # Verified phone (aka "double tableflip")
```

---

## NotificationLevel

Used in `edit_guild` tool.

```python
discord.NotificationLevel.all_messages    # All messages
discord.NotificationLevel.only_mentions   # Only @mentions
```

---

## ContentFilter

Used in `edit_guild` tool.

```python
discord.ContentFilter.disabled      # No scanning
discord.ContentFilter.no_role       # Scan members without roles
discord.ContentFilter.all_members   # Scan all members
```

---

## EntityType

Used in `create_scheduled_event` and `edit_scheduled_event` tools.

```python
discord.EntityType.stage_instance   # Stage channel event
discord.EntityType.voice            # Voice channel event
discord.EntityType.external         # External location event
```

---

## EventStatus

Used in `edit_scheduled_event` tool.

```python
discord.EventStatus.scheduled       # Not started
discord.EventStatus.active          # Currently happening
discord.EventStatus.completed       # Ended
discord.EventStatus.cancelled       # Cancelled
```

**Valid transitions:**
- `scheduled` -> `active` or `cancelled`
- `active` -> `completed`

---

## AuditLogAction

Used in `get_audit_log` tool. See [moderation.md](moderation.md) for full list.

```python
# Access by name
discord.AuditLogAction.ban
discord.AuditLogAction.kick
discord.AuditLogAction.channel_create
# etc.

# Convert from string
action = discord.AuditLogAction[action_name]  # KeyError if invalid
```

---

## AuditLogActionCategory

```python
discord.AuditLogActionCategory.create   # Something was created
discord.AuditLogActionCategory.delete   # Something was deleted
discord.AuditLogActionCategory.update   # Something was updated
```

---

## AutoModRuleTriggerType

Used in `create_automod_rule` tool.

```python
discord.AutoModRuleTriggerType.keyword          # Custom keyword filter
discord.AutoModRuleTriggerType.harmful_link      # Harmful link detection (deprecated)
discord.AutoModRuleTriggerType.spam             # Spam detection
discord.AutoModRuleTriggerType.keyword_preset   # Preset keyword lists
discord.AutoModRuleTriggerType.mention_spam     # Mention spam detection
discord.AutoModRuleTriggerType.member_profile   # Member profile keyword filter
```

---

## AutoModRuleEventType

```python
discord.AutoModRuleEventType.message_send   # Triggered on message send
discord.AutoModRuleEventType.member_update  # Triggered on profile update
```

---

## AutoModRuleActionType

```python
discord.AutoModRuleActionType.block_message              # Block the message
discord.AutoModRuleActionType.send_alert_message          # Send alert to a channel
discord.AutoModRuleActionType.timeout                     # Timeout the user
discord.AutoModRuleActionType.block_member_interactions   # Block member interactions
```

---

## MessageType

```python
discord.MessageType.default                    # Regular message
discord.MessageType.recipient_add              # Group DM: recipient added
discord.MessageType.recipient_remove           # Group DM: recipient removed
discord.MessageType.call                       # Call started
discord.MessageType.channel_name_change        # Group DM: name changed
discord.MessageType.channel_icon_change        # Group DM: icon changed
discord.MessageType.pins_add                   # Message pinned
discord.MessageType.new_member                 # New member joined
discord.MessageType.premium_guild_subscription # Nitro Boost
discord.MessageType.premium_guild_tier_1       # Boost Level 1
discord.MessageType.premium_guild_tier_2       # Boost Level 2
discord.MessageType.premium_guild_tier_3       # Boost Level 3
discord.MessageType.channel_follow_add         # News channel follow
discord.MessageType.thread_created             # Thread created
discord.MessageType.reply                      # Reply to a message
discord.MessageType.chat_input_command         # Slash command
discord.MessageType.thread_starter_message     # Thread starter
discord.MessageType.context_menu_command       # Context menu command
discord.MessageType.auto_moderation_action     # AutoMod action
discord.MessageType.stage_start                # Stage started
discord.MessageType.stage_end                  # Stage ended
discord.MessageType.stage_speaker              # Stage speaker
discord.MessageType.stage_topic                # Stage topic changed
discord.MessageType.guild_application_premium_subscription  # App subscription
discord.MessageType.poll_result                # Poll results
```

---

## WebhookType

```python
discord.WebhookType.incoming           # User-created webhook
discord.WebhookType.channel_follower   # Server follow webhook
discord.WebhookType.application        # Application/interaction webhook
```

---

## InviteTarget

```python
discord.InviteTarget.unknown           # Unknown
discord.InviteTarget.stream            # Voice channel stream
discord.InviteTarget.embedded_application  # Activity in voice channel
```

---

## InviteType

```python
discord.InviteType.guild    # Guild invite
discord.InviteType.group_dm # Group DM invite
discord.InviteType.friend   # Friend invite
```

---

## Status

```python
discord.Status.online       # Online (green)
discord.Status.offline      # Offline (gray)
discord.Status.idle         # Idle (yellow)
discord.Status.dnd          # Do Not Disturb (red)
discord.Status.invisible    # Invisible (appears offline)
```

---

## Colour / Color

```python
discord.Colour.default()        # 0x000000
discord.Colour.red()            # 0xe74c3c
discord.Colour.dark_red()       # 0x992d22
discord.Colour.green()          # 0x2ecc71
discord.Colour.dark_green()     # 0x1f8b4c
discord.Colour.blue()           # 0x3498db
discord.Colour.dark_blue()      # 0x206694
discord.Colour.purple()         # 0x9b59b6
discord.Colour.dark_purple()    # 0x71368a
discord.Colour.gold()           # 0xf1c40f
discord.Colour.orange()         # 0xe67e22
discord.Colour.dark_orange()    # 0xa84300
discord.Colour.teal()           # 0x1abc9c
discord.Colour.dark_teal()      # 0x11806a
discord.Colour.magenta()        # 0xe91e63
discord.Colour.dark_magenta()   # 0xad1457
discord.Colour.greyple()        # 0x99aab5
discord.Colour.dark_grey()      # 0x607d8b
discord.Colour.light_grey()     # 0x979c9f
discord.Colour.blurple()        # 0x5865f2
discord.Colour.og_blurple()     # 0x7289da
discord.Colour.fuchsia()        # 0xeb459e
discord.Colour.yellow()         # 0xfee75c
discord.Colour.dark_theme()     # 0x36393f
discord.Colour.brand_red()      # 0xed4245
discord.Colour.brand_green()    # 0x57f287
discord.Colour.pink()           # 0xeb459f
discord.Colour.nitro_pink()     # 0xf47fff
discord.Colour.from_rgb(r, g, b)
discord.Colour.from_str("#hex")
discord.Colour(0xFF0000)        # From integer
```

---

## ForumLayoutType

```python
discord.ForumLayoutType.not_set       # No default set
discord.ForumLayoutType.list_view     # List layout
discord.ForumLayoutType.gallery_view  # Gallery layout
```

---

## ForumOrderType

```python
discord.ForumOrderType.latest_activity  # Sort by latest activity
discord.ForumOrderType.creation_date    # Sort by creation date
```

---

## StickerFormatType

```python
discord.StickerFormatType.png     # PNG image
discord.StickerFormatType.apng    # Animated PNG
discord.StickerFormatType.lottie  # Lottie animation
discord.StickerFormatType.gif     # GIF image
```

---

## PrivacyLevel

```python
discord.PrivacyLevel.guild_only  # Only guild members can see
```

---

## VideoQualityMode

```python
discord.VideoQualityMode.auto    # Discord chooses quality
discord.VideoQualityMode.full    # 720p
```

---

## NSFWLevel

```python
discord.NSFWLevel.default        # Not evaluated
discord.NSFWLevel.explicit       # Contains explicit content
discord.NSFWLevel.safe           # Confirmed safe
discord.NSFWLevel.age_restricted # May contain explicit content
```

---

## MFALevel

```python
discord.MFALevel.disabled        # No 2FA requirement for moderators
discord.MFALevel.require_2fa     # Moderators must have 2FA enabled
```
