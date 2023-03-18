import os
import subprocess

import asyncio
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

from exceptions.youtube_exception import YoutubeException
from exceptions.voice_client_exception import VoiceClientException


AUDIO_FILENAME = "audio.mp3"
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -loglevel warning -hide_banner",
}
HTML_PARSER = "html.parser"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=os.getenv("COMMAND_PREFIX", "!"), intents=intents)
voice_client = None

KEY_TITLE = "title"
KEY_URL = "url"
playlist = []


@bot.command(aliases=["add"])
async def play(ctx, *args):
    global playlist, voice_client
    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel")
        return
    await add_song_to_playlist(ctx, " ".join(args))
    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        return
    await connect_voice_client(ctx)
    asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop)


@bot.command(aliases=["queue", "playlist"])
async def q(ctx):
    global playlist
    if len(playlist) <= 0:
        await ctx.send(
            "🙉 the playlist is **EMPTY** 😭 - fill it up **NOW**!!!!111elevenELEVENTHOUSANDONEHUNDRETELEVEN\n🎶 🎵 🎼 🎹 🎧 🎷 🎺 🎸 🎻 📻 🪕 🎚"
        )
        return
    list_items = []
    for (i, title) in enumerate([song[KEY_TITLE] for song in playlist], 1):
        list_items.append(f"{i}. {title}")
    await ctx.send("Playlist:\n>>> {}".format("\n".join(list_items)))


@bot.command()
async def stop(ctx):
    global playlist, voice_client
    playlist = []
    if not voice_client or not voice_client.is_connected():
        await ctx.send("Not currently playing anything.")
        return
    voice_client.stop()
    await voice_client.disconnect()
    voice_client = None
    await ctx.send("Stopped playback and disconnected from voice channel.")


@bot.command(aliases=["next"])
async def skip(ctx):
    global playlist, voice_client
    if not voice_client or not voice_client.is_connected():
        await ctx.send("Not currently playing anything.")
        return
    voice_client.stop()
    await ctx.send("Skipping to the next song.")


async def add_song_to_playlist(ctx, query):
    global playlist
    try:
        cmd = f'yt-dlp -f bestaudio -g "ytsearch:{query}" --print "%(title)s - %(duration>%H:%M:%S)s"'
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        title, url = stdout.decode().strip().split("\n")
        if process.returncode != 0:
            raise YoutubeException(
                f"yt-dlp returned non-zero exit code {process.returncode}"
            )
        playlist.append({KEY_TITLE: title, KEY_URL: url})
        await ctx.send(f"Queued {title}")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
        return


async def play_next_song(ctx):
    global playlist, voice_client
    if len(playlist) <= 0:
        await ctx.send("Playlist empty, disconnecting")
        if voice_client == None:
            return
        await voice_client.disconnect()
        voice_client = None
        return
    if voice_client == None:
        connect_voice_client(ctx)
    song = playlist.pop(0)
    async with ctx.typing():
        try:
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song.get(KEY_URL), **FFMPEG_OPTIONS)
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
        await ctx.send(f"Now playing: {song.get(KEY_TITLE)}")


async def connect_voice_client(ctx):
    global voice_client
    if voice_client and voice_client.is_connected():
        return
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()
    if not voice_client:
        raise VoiceClientException("Failed to connect to the voice channel")


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
