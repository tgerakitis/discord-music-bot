import asyncio
from discord.ext import commands
import os
from cogwatch import watch

class ExampleBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!')

    @watch(path='commands', preload=True) # This is all you need to add.
    async def on_ready(self):
        print('Bot ready.')

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)


async def main():
    client = ExampleBot()
    await client.start(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == '__main__':
    asyncio.run(main())