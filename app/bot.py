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
song_queue = []
voice_client = None


@bot.command()
async def play(ctx, *args):
    query = " ".join(args)
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
        song_queue.append((source, query))
        if len(song_queue) == 1:
            # If the queue was previously empty, play the first song
            play_next_song(ctx)
        else:
            await ctx.send(f"Added {query} to the queue")


@bot.command()
async def stop(ctx):
    global voice_client, song_queue
    voice_client.stop()
    song_queue = []
    await voice_client.disconnect()


def play_next_song(ctx):
    global song_queue
    if len(song_queue) > 0:
        source, query = song_queue[0]
        voice_client.play(source, after=lambda e: play_next_song(ctx))
        song_queue = song_queue[1:]
        ctx.send(f"Now playing: {query}")
    else:
        voice_client.stop()


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
