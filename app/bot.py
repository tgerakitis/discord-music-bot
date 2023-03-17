import os
import subprocess

import asyncio
import discord
from discord.ext import commands

from exceptions.youtube_exception import YoutubeException


AUDIO_FILENAME = "audio.mp3"
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -loglevel warning -hide_banner",
}
HTML_PARSER = "html.parser"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!!", intents=intents)
voice_client = None


@bot.command()
async def play(ctx, *args):
    query = " ".join(args)
    print("hui", flush=True)
    global voice_client
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel")
        return
    if voice_client and voice_client.is_connected():
        await voice_client.move_to(ctx.author.voice.channel)
    else:
        voice_client = await ctx.author.voice.channel.connect()
    async with ctx.typing():
        try:
            cmd = f'yt-dlp -f bestaudio -g "ytsearch:{query}"'
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise YoutubeException(
                    f"yt-dlp returned non-zero exit code {process.returncode}"
                )
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stdout.decode().strip(), **FFMPEG_OPTIONS)
            )
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
            return
        ctx.voice_client.play(source)
        await ctx.send(f"Now playing: {query}")


@bot.command()
async def stop(ctx):
    await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
