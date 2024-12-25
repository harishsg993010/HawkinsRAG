import os
import hashlib
from typing import Any, Dict, List, Optional
from ..utils.loader_registry import BaseLoader

class DiscordLoader(BaseLoader):
    """Loader for Discord channels."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Discord loader with configuration."""
        super().__init__(config)
        if not os.environ.get("DISCORD_TOKEN"):
            raise ValueError("DISCORD_TOKEN environment variable required")

        self.token = os.environ.get("DISCORD_TOKEN")

    @staticmethod
    def _format_message(message):
        """Format a Discord message with all metadata."""
        return {
            "message_id": str(message.id),
            "content": message.content,
            "author": {
                "id": str(message.author.id),
                "name": message.author.name,
                "discriminator": message.author.discriminator,
            },
            "created_at": message.created_at.isoformat(),
            "attachments": [
                {
                    "id": str(attachment.id),
                    "filename": attachment.filename,
                    "url": attachment.url,
                    "proxy_url": attachment.proxy_url,
                    "size": attachment.size,
                    "height": attachment.height,
                    "width": attachment.width,
                }
                for attachment in message.attachments
            ],
            "embeds": [
                {
                    "title": embed.title,
                    "description": embed.description,
                    "url": embed.url,
                    "timestamp": embed.timestamp.isoformat() if embed.timestamp else None,
                    "color": embed.color,
                    "fields": [
                        {
                            "name": field.name,
                            "value": field.value,
                            "inline": field.inline,
                        }
                        for field in embed.fields
                    ],
                }
                for embed in message.embeds
            ],
        }

    def load(self, source: str) -> Any:
        """Load content from Discord channel."""
        try:
            import discord
            from discord.ext import commands
        except ImportError:
            raise ImportError(
                "Discord client required. Install with: pip install discord.py"
            )

        channel_id = source
        messages: List[Dict[str, Any]] = []

        class DiscordClient(discord.Client):
            async def setup_hook(self) -> None:
                self.tree = discord.app_commands.CommandTree(self)

            async def on_ready(self) -> None:
                try:
                    channel = self.get_channel(int(channel_id))
                    if not isinstance(channel, discord.TextChannel):
                        raise ValueError(
                            f"Channel {channel_id} is not a text channel. "
                            "Only text channels are supported."
                        )

                    # Get channel threads
                    threads = {thread.id: thread for thread in channel.threads}

                    # Get messages from main channel
                    async for message in channel.history(limit=None):
                        messages.append(DiscordLoader._format_message(message))
                        # Get messages from related thread if exists
                        if message.id in threads:
                            async for thread_message in threads[message.id].history(limit=None):
                                messages.append(DiscordLoader._format_message(thread_message))

                except Exception as e:
                    print(f"Error loading Discord content: {e}")
                finally:
                    await self.close()

        # Set up client with message content intent
        intents = discord.Intents.default()
        intents.message_content = True
        client = DiscordClient(intents=intents)

        # Run client
        client.run(self.token)

        # Format all messages into text
        content = "\n\n".join(
            f"[{msg['created_at']}] {msg['author']['name']}: {msg['content']}"
            for msg in messages
        )

        doc_id = hashlib.sha256((content + channel_id).encode()).hexdigest()
        metadata = {"url": channel_id}

        return {
            "doc_id": doc_id,
            "data": [
                {
                    "content": content,
                    "meta_data": metadata,
                }
            ],
        }