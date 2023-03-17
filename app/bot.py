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
playlist = []


@bot.command()
async def play(ctx, *args):
    global voice_client, playlist
    query = " ".join(args)
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel")
        return
    playlist.append(query)
    if voice_client and voice_client.is_connected():
        await ctx.send(f"Queued {query}")
        return
    voice_client = await ctx.author.voice.channel.connect()
    asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop)


@bot.command()
async def stop(ctx):
    global voice_client, playlist
    playlist = []
    if not voice_client or not voice_client.is_connected():
        await ctx.send("Not currently playing anything.")
        return
    voice_client.stop()
    await voice_client.disconnect()
    voice_client = None
    await ctx.send("Stopped playback and disconnected from voice channel.")


async def play_next_song(ctx):
    global voice_client
    if len(playlist) <= 0:
        await ctx.voice_client.disconnect()
        voice_client = None
        return
    query = playlist.pop(0)
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
        voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(
                play_next_song(ctx), bot.loop
            ).result(),
        )
        await ctx.send(f"Now playing: {query}")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
