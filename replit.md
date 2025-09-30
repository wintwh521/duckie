# Overview

This is a Discord bot built with discord.py that automatically detects and enlarges custom server emojis in messages. When users send messages containing custom Discord emojis, the bot responds by sending those emojis in an enlarged format using Discord's CDN. The bot serves as a simple, fun utility for Discord servers to emphasize custom emoji usage.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
**Decision:** Built using discord.py with the commands extension
**Rationale:** discord.py is the standard Python library for Discord bot development, providing robust event handling and command processing capabilities. The commands extension adds structured command handling through decorators.

**Key Components:**
- Command prefix: `%` for explicit bot commands
- Intents: Default intents plus message_content enabled to read message text
- Custom help command disabled in favor of simple `%help` implementation

## Message Processing Pipeline
**Decision:** Event-driven architecture using `on_message` event handler
**Rationale:** The core functionality requires analyzing every message for emoji content, making event handlers more suitable than command-based interactions.

**Processing Flow:**
1. Ignore messages from the bot itself (prevent loops)
2. Process any explicit commands first via `bot.process_commands()`
3. Scan message content for custom Discord emojis using regex pattern matching
4. Send enlarged emoji response via Discord CDN URLs embedded in Discord embeds

**Alternatives Considered:**
- Command-only approach: Would require users to explicitly invoke the bot, reducing spontaneity
- Webhook-based approach: Unnecessary complexity for this use case

**Pros:**
- Automatic, seamless user experience
- Supports both static and animated custom Discord emojis
- Minimal user interaction required
- High-quality enlarged images via Discord CDN

**Cons:**
- Processes every message (potential performance consideration at scale)
- Creates additional messages in chat

## Emoji Detection Strategy
**Decision:** Regex-based detection for custom Discord emojis only
**Rationale:** Custom Discord emojis follow a specific format that can be reliably captured with regex, and enlargement is achieved via Discord's CDN.

**Custom Emoji Pattern:** `<(a?):(\w+):(\d+)>` captures:
- Animated flag (optional `a`) - determines if emoji is .gif or .png
- Emoji name
- Unique Discord emoji ID

**Enlargement Method:** Constructs Discord CDN URL `https://cdn.discordapp.com/emojis/{id}.{ext}?size=128` and sends as embed image.

# External Dependencies

## Discord API Integration
- **Library:** discord.py
- **Purpose:** Core Discord bot functionality, event handling, and API communication
- **Authentication:** Bot token via environment variable `DISCORD_BOT_TOKEN`

## Configuration Management
- **Library:** python-dotenv
- **Purpose:** Environment variable management for secure token storage
- **Variable Required:** `DISCORD_BOT_TOKEN`

## Runtime Requirements
- Python 3.11+ (installed via Replit)
- Discord Bot Account with Message Content Intent enabled
- Network connectivity to Discord API endpoints and Discord CDN