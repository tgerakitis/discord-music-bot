"""Commands for music playback"""
import subprocess
import random

import asyncio
import discord
from discord.ext import commands

from bot import PLAYLIST, VOICE_CLIENT
from exceptions.playback_exception import PlaybackException
from exceptions.voice_client_exception import VoiceClientException
from exceptions.youtube_exception import YoutubeException

# CONSTANTS
AUDIO_FILENAME = "audio.mp3"
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -loglevel warning -hide_banner",
}
HTML_PARSER = "html.parser"
KEY_TITLE = "title"
KEY_URL = "url"
KEY_THUMBNAIL = "thumbnail"

THUMBNAILSPLITTER = "SPLITHEREFORTHUMBNAIL123"


class MusicCommands(commands.Cog):
    """All relevant music commands"""

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["add"])
    async def play(self, ctx, *args):
        """Entrypoint"""
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel")
            return
        await self.add_song_to_playlist(ctx, " ".join(args))

        if VOICE_CLIENT and VOICE_CLIENT.is_connected():
            return
        await self.connect_voice_client(ctx)
        asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.client.loop)

    async def is_playing(self, ctx):
        """Helper to check if something is currently plaing"""
        return (
            VOICE_CLIENT and VOICE_CLIENT.is_connected() and VOICE_CLIENT.is_playing()
        )

    @commands.command(aliases=["q", "playlist", "list"])
    async def queue(self, ctx):
        """Render current queue"""
        global PLAYLIST
        if len(PLAYLIST) <= 0:
            await ctx.send(
                "🙉 the PLAYLIST is **EMPTY** 😭 - fill it up **NOW**"
                "!!!11elevenELEVENTHOUSANDONEHUNDRETELEVEN\n"
                "🎶 🎵 🎼 🎹 🎧 🎷 🎺 🎸 🎻 📻 🪕 🎚"
            )
            return
        list_items = []
        playlist = PLAYLIST
        for i, title in enumerate([song[KEY_TITLE] for song in playlist], 1):
            list_items.append(f"{i}. {title}")
        await ctx.send("Playlist:\n>>> {}".format("\n".join(list_items)))

    @commands.command()
    async def stop(self, ctx):
        """Stop playing and disconnect"""
        global PLAYLIST, VOICE_CLIENT
        PLAYLIST = []
        if not await self.is_playing(ctx):
            await ctx.send("Not currently playing anything.")
            return
        VOICE_CLIENT.stop()
        await VOICE_CLIENT.disconnect()
        VOICE_CLIENT = None
        await ctx.send("Stopped playback and disconnected from voice channel.")

    @commands.command(aliases=["next"])
    async def skip(self, ctx):
        """Skip top next song"""
        if not await self.is_playing(ctx):
            await ctx.send("Not currently playing anything.")
            return
        VOICE_CLIENT.stop()
        await ctx.send("Skipping to the next song.")

    @commands.command(aliases=["mv", "switch", "playnext"])
    async def move(self, ctx, *args):
        """Move a song to the top or desired position"""
        global PLAYLIST
        if len(PLAYLIST) <= 1:
            await ctx.send("nothing to move here 🕵️‍♂️ - pls add songs 🙇‍♀️🙇‍♂️")
            return
        if len(args) <= 0 or len(args) >= 3:
            await ctx.send(
                "Please select the playlist index of the songs you want to move!"
            )
            await self.queue(ctx)
            return
        if not all(element.isdigit() for element in args):
            await ctx.send(
                "Please select the playlist index of the songs you want to move!"
            )
        args = [int(x) - 1 for x in list(args)]
        for element in [x for x in args if not 0 <= x <= (len(PLAYLIST) - 1)]:
            await ctx.send(
                f"Song nr {element + 1} does not exist and can not be moved!"
            )
            return
        # if only argument is given, we want to switch with the first song
        if len(args) == 1:
            PLAYLIST.insert(0, PLAYLIST.pop(args[0]))
            await ctx.send(f"Moved {PLAYLIST[0][KEY_TITLE]} to top of the playlist! 🏎💨")
            await self.queue(ctx)
            return
        pos1, pos2 = args
        PLAYLIST[pos1], PLAYLIST[pos2] = (
            PLAYLIST[pos2],
            PLAYLIST[pos1],
        )
        await ctx.send(
            f"Switched {PLAYLIST[pos1][KEY_TITLE]} and"
            f" {PLAYLIST[pos2][KEY_TITLE]}! 🥴💫"
        )
        await self.queue(ctx)

    @commands.command(aliases=["rm", "kill"])
    async def remove(self, ctx, *args):
        """Remove a song"""
        global PLAYLIST
        if not all(element.isdigit() for element in args):
            await ctx.send(
                "Please select the playlist index of the songs you want to move!"
            )
        remove_index = [int(x) - 1 for x in list(args)][0]
        if not 0 <= remove_index <= (len(PLAYLIST) - 1):
            await ctx.send(
                f"Song nr {remove_index + 1} does not exist and can not be removed!"
            )
            return
        removed = PLAYLIST.pop(remove_index)
        await ctx.send(f"Removed {removed[KEY_TITLE]}! ❌")
        await self.queue(ctx)

    @commands.command(aliases=["randomize"])
    async def shuffle(self, ctx):
        """Randomize playlist order"""
        global PLAYLIST
        if len(PLAYLIST) <= 1:
            await ctx.send("Empty Playlist, nothing to shuffle 🤷‍♂️⁉")
            return
        random.shuffle(PLAYLIST)
        await ctx.send("Playlist shuffled 😱🤡🧨")
        await self.queue(ctx)

    async def add_song_to_playlist(self, ctx, query):
        """Adds a song to current playlist"""
        try:
            cmd = (
                f'yt-dlp -f bestaudio -g "ytsearch:{query}"'
                f' --print "%(title)s - %(duration>%H:%M:%S)s{THUMBNAILSPLITTER}%(thumbnail)s"'
            )
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            title, url = stdout.decode().strip().split("\n")
            title, thumbnail_url = title.split(THUMBNAILSPLITTER)
            if process.returncode != 0:
                raise YoutubeException(
                    f"yt-dlp returned non-zero exit code {process.returncode}\n"
                    f"Message: {stdout.decode().strip()}\n"
                    f"Error: {stderr.decode().strip()}"
                )
            PLAYLIST.append(
                {KEY_TITLE: title, KEY_URL: url, KEY_THUMBNAIL: thumbnail_url}
            )
            if not self.is_playing(ctx):
                thumbnail_url = ""
            await ctx.send(f"Queued {title}\n{thumbnail_url}")
        except YoutubeException as exception:
            await ctx.send(f"Error: {str(exception)}")
            return

    async def play_next_song(self, ctx):
        """Plays the next song"""
        global VOICE_CLIENT
        if len(PLAYLIST) <= 0:
            await ctx.send("Playlist empty, disconnecting")
            if VOICE_CLIENT is None:
                return
            await VOICE_CLIENT.disconnect()
            VOICE_CLIENT = None
            return
        if VOICE_CLIENT is None:
            self.connect_voice_client(ctx)
        song = PLAYLIST.pop(0)
        async with ctx.typing():
            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song.get(KEY_URL), **FFMPEG_OPTIONS)
                )
            except PlaybackException as exception:
                await ctx.send(f"Error: {str(exception)}")
                return
            VOICE_CLIENT.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next_song(ctx), self.client.loop
                ).result(),
            )
            await ctx.send(
                f"Now playing: {song.get(KEY_TITLE)}\n{song.get(KEY_THUMBNAIL)}"
            )

    async def connect_voice_client(self, ctx):
        """Connects to voice client if not already coinnected"""
        global VOICE_CLIENT
        if VOICE_CLIENT and VOICE_CLIENT.is_connected():
            return
        voice_channel = ctx.author.voice.channel
        VOICE_CLIENT = await voice_channel.connect()
        # TODO fix case when voice is connected but voice_client is empty
        if not VOICE_CLIENT:
            raise VoiceClientException("Failed to connect to the voice channel")


async def setup(client):
    """Setup cog"""
    await client.add_cog(MusicCommands(client))
