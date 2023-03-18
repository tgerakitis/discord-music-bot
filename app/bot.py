"""This is the application entrypoint"""
from distutils.log import debug
import os
import asyncio
import pathlib
import discord
from discord.ext import commands
from cogwatch import watch

PLAYLIST = []
VOICE_CLIENT = None

class DiscordMusicBot(commands.Bot):
    """A discord music bot that finds and plays songs"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=os.getenv("COMMAND_PREFIX", "!"), intents=intents
        )

    @watch(path="app/commands", preload=True)
    async def on_ready(self):
        """Loads all commands when ready"""
        for commands_file in (pathlib.Path(__file__).parent / "commands").glob("*.py"):
            if commands_file.name != "__init__.py":
                await self.load_extension(f"commands.{commands_file.name[:-3]}")
        print("Bot ready.", flush=True)

    async def on_message(self, message):
        """Forwards messages to registered commands"""
        if message.author.bot:
            return
        await self.process_commands(message)


async def main():
    """Run the discord bot"""
    client = DiscordMusicBot()
    await client.start(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
