"""Commands for music playback"""
import subprocess

import asyncio
import discord
from discord.ext import commands

from .exceptions.playback_exception import PlaybackException
from .exceptions.voice_client_exception import VoiceClientException
from .exceptions.youtube_exception import YoutubeException

# CONSTANTS
AUDIO_FILENAME = "audio.mp3"
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -loglevel warning -hide_banner",
}
HTML_PARSER = "html.parser"
KEY_TITLE = "title"
KEY_URL = "url"


class MusicCommands(commands.Cog):
    """All relevant music commands"""

    playlist = []
    voice_client = None

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["add"])
    async def play(self, ctx, *args):
        """Entrypoint"""
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel")
            return
        await self.add_song_to_playlist(ctx, " ".join(args))
        if (
            self.voice_client
            and self.voice_client.is_connected()
            and self.voice_client.is_playing()
        ):
            return
        await self.connect_voice_client(ctx)
        asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.client.loop)

    @commands.command(aliases=["q", "playlist"])
    async def queue(self, ctx):
        """Render current queue"""
        if len(self.playlist) <= 0:
            await ctx.send(
                "🙉 the self.playlist is **EMPTY** 😭 - fill it up **NOW**"
                "!!!11elevenELEVENTHOUSANDONEHUNDRETELEVEN\n"
                "🎶 🎵 🎼 🎹 🎧 🎷 🎺 🎸 🎻 📻 🪕 🎚"
            )
            return
        list_items = []
        for i, title in enumerate([song[KEY_TITLE] for song in self.playlist], 1):
            list_items.append(f"{i}. {title}")
        await ctx.send("Playlist:\n>>> {}".format("\n".join(list_items)))

    @commands.command()
    async def stop(self, ctx):
        """Stop playing and disconnect"""
        self.playlist = []
        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.send("Not currently playing anything.")
            return
        self.voice_client.stop()
        await self.voice_client.disconnect()
        self.voice_client = None
        await ctx.send("Stopped playback and disconnected from voice channel.")

    @commands.command(aliases=["next"])
    async def skip(self, ctx):
        """Skip top next song"""
        if not self.voice_client or not self.voice_client.is_connected():
            await ctx.send("Not currently playing anything.")
            return
        self.voice_client.stop()
        await ctx.send("Skipping to the next song.")

    @commands.command(aliases=["mv"])
    async def move(self, ctx, *args):
        """Move a song to the top or desired position"""
        if len(self.playlist) <= 0:
            await ctx.send("Playlist empty, nothing to move here 🕵️‍♂️")
            return
        if len(args) <= 0:
            await ctx.send("Please select the playlist index of the song you want to move")
            await self.queue(ctx)
            return


    async def add_song_to_playlist(self, ctx, query):
        """Adds a song to current playlist"""
        try:
            cmd = (
                f'yt-dlp -f bestaudio -g "ytsearch:{query}"'
                ' --print "%(title)s - %(duration>%H:%M:%S)s"'
            )
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            title, url = stdout.decode().strip().split("\n")
            if process.returncode != 0:
                raise YoutubeException(
                    f"yt-dlp returned non-zero exit code {process.returncode}\n"
                    f"Message: {stdout.decode().strip()}\n"
                    f"Error: {stderr.decode().strip()}"
                )
            self.playlist.append({KEY_TITLE: title, KEY_URL: url})
            await ctx.send(f"Queued {title}")
        except YoutubeException as exception:
            await ctx.send(f"Error: {str(exception)}")
            return

    async def play_next_song(self, ctx):
        """Plays the next song"""
        if len(self.playlist) <= 0:
            await ctx.send("Playlist empty, disconnecting")
            if self.voice_client is None:
                return
            await self.voice_client.disconnect()
            self.voice_client = None
            return
        if self.voice_client is None:
            self.connect_voice_client(ctx)
        song = self.playlist.pop(0)
        async with ctx.typing():
            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song.get(KEY_URL), **FFMPEG_OPTIONS)
                )
            except PlaybackException as exception:
                await ctx.send(f"Error: {str(exception)}")
                return
            self.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next_song(ctx), self.client.loop
                ).result(),
            )
            await ctx.send(f"Now playing: {song.get(KEY_TITLE)}")

    async def connect_voice_client(self, ctx):
        """Connects to voice client if not already coinnected"""
        if self.voice_client and self.voice_client.is_connected():
            return
        voice_channel = ctx.author.voice.channel
        self.voice_client = await voice_channel.connect()
        if not self.voice_client:
            raise VoiceClientException("Failed to connect to the voice channel")


async def setup(client):
    """Setup cog"""
    await client.add_cog(MusicCommands(client))
