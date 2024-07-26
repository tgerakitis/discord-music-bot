"""Commands for music playback"""
import json
import os
import random
import subprocess
from pathlib import Path

import asyncio
import discord
from discord.ext import commands
from bot import PLAYLIST, VOICE_CLIENT
from exceptions.playback_exception import PlaybackException
from exceptions.voice_client_exception import VoiceClientException
from exceptions.youtube_exception import YoutubeException
from helpers.sanitize_path import sanitize_path

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
PLAYLIST_FOLDER = os.getenv("PLAYLIST_FOLDER", "/playlists")
THUMBNAILSPLITTER = "SPLITHEREFORTHUMBNAIL123"


class MusicCommands(commands.Cog):
    """All relevant music commands"""

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["add"])
    async def play(self, ctx: commands.Context, *args):
        """Entrypoint"""
        if not ctx.author.voice:
            await ctx.send("You are not in a voice channel")
            return
        await self.add_song_to_playlist(ctx, " ".join(args))

        if await self.voice_connected():
            return
        await self.connect_voice_client(ctx)
        asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.client.loop)

    async def is_playing(self):
        """Helper to check if something is currently plaing"""
        return (await self.voice_connected()) and VOICE_CLIENT.is_playing()

    async def voice_connected(self):
        """Helper to check the client is currently connected"""
        return VOICE_CLIENT and VOICE_CLIENT.is_connected()

    @commands.command(aliases=["q", "playlist", "list"])
    async def queue(self, ctx: commands.Context):
        """Render current queue"""
        global PLAYLIST
        if len(PLAYLIST) <= 0:
            await ctx.send(
                "🙉 the PLAYLIST is **EMPTY** 😭 - fill it up **NOW**"
                "!!!11elevenELEVENTHOUSANDONEHUNDRETELEVEN\n"
                "🎶 🎵 🎼 🎹 🎧 🎷 🎺 🎸 🎻 📻 🪕 🎚"
            )
            return
        await self.render_playlist(ctx, "Current", PLAYLIST)

    async def render_playlist(self, ctx, playlist_name: str, playlist: list[dict]):
        list_items = "".join(
            [
                f"\n{song[1]+1}. {song[0].get(KEY_TITLE)}"
                for song in zip(playlist, range(len(playlist)))
            ]
        )
        await ctx.send(
            embed=discord.Embed(
                title=f"{playlist_name} Playlist", description=f">>> {list_items}"
            )
        )

    @commands.command(aliases=[])
    async def stop(self, ctx: commands.Context):
        """Stop playing and disconnect"""
        global PLAYLIST, VOICE_CLIENT
        PLAYLIST = []
        if not (await self.is_playing()):
            await ctx.send("Not currently playing anything.")
            return
        await VOICE_CLIENT.stop()
        await VOICE_CLIENT.disconnect()
        VOICE_CLIENT = None
        await ctx.send("Stopped playback and disconnected from voice channel.")

    @commands.command(aliases=["next"])
    async def skip(self, ctx: commands.Context):
        """Skip top next song"""
        if not await self.is_playing():
            await ctx.send("Not currently playing anything.")
            return
        VOICE_CLIENT.stop()
        await ctx.send("Skipping to the next song.")

    @commands.command(aliases=["mv", "switch", "playnext"])
    async def move(self, ctx: commands.Context, *args):
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
        # if only one argument is given, we want to switch with the first song
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
    async def remove(self, ctx: commands.Context, *args):
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
    async def shuffle(self, ctx: commands.Context):
        """Randomize playlist order"""
        global PLAYLIST
        if len(PLAYLIST) <= 1:
            await ctx.send("Empty Playlist, nothing to shuffle 🤷‍♂️⁉")
            return
        random.shuffle(PLAYLIST)
        await ctx.send("Playlist shuffled 😱🤡🧨")
        await self.queue(ctx)

    async def add_song_to_playlist(self, ctx: commands.Context, query):
        """Adds a song to current playlist"""
        try:
            cmd = (
                f'yt-dlp -f bestaudio --cookies /cookies.txt -g "ytsearch:{query}"'
                f' --print "%(title)s - %(duration>%H:%M:%S)s{THUMBNAILSPLITTER}%(thumbnail)s"'
            )
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if len(stdout) <= 0 or len(stdout.decode().strip().split("\n")) < 2:
                await ctx.send(f"🤷‍♀️ 404 when looking for 😖 >>> {query} <<< ❓N̴̪̾̈́̚Ȧ̴͖́͆N̴̥̏̽̎Ḯ̵̪̘̝⁉ 😭 pls try another query")
                raise YoutubeException(
                    f"yt-dlp returned something strange"
                    f"Message: {stdout.decode().strip()}\n"
                    f"Error: {stderr.decode().strip()}"
                )
                return
            if process.returncode != 0:
                raise YoutubeException(
                    f"yt-dlp returned non-zero exit code {process.returncode}\n"
                    f"Message: {stdout.decode().strip()}\n"
                    f"Error: {stderr.decode().strip()}"
                )
            title, url = stdout.decode().strip().split("\n")
            title, thumbnail_url = title.split(THUMBNAILSPLITTER)
            PLAYLIST.append(
                {KEY_TITLE: title, KEY_URL: url, KEY_THUMBNAIL: thumbnail_url}
            )
            if not await self.is_playing():
                thumbnail_url = ""
            await ctx.send(f"Queued {title}\n{thumbnail_url}")
        except YoutubeException as exception:
            await ctx.send(f"Youtube ❌ Error: {str(exception)}")
            return
        except BaseException as exception:
            await ctx.send(f"Generic 🤡 Error: {str(exception)}")
            return

    async def play_next_song(self, ctx: commands.Context):
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
            await self.connect_voice_client(ctx)
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

    async def connect_voice_client(self, ctx: commands.Context):
        """Connects to voice client if not already coinnected"""
        global VOICE_CLIENT
        if await self.voice_connected():
            return
        voice_channel = ctx.author.voice.channel
        VOICE_CLIENT = await voice_channel.connect()
        if not VOICE_CLIENT:
            raise VoiceClientException("Failed to connect to the voice channel")

    @commands.command(aliases=["save"])
    async def save_playlist_to_file(self, ctx: commands.Context, filename):
        """
        Save the global variable PLAYLIST to a file in the 'playlists' folder.
        """
        with self.save_open(filename, "w") as f:
            json.dump(PLAYLIST, f)
            await ctx.send(
                embed=discord.Embed(title=f"successfully saved {Path(f.name).stem}")
            )

    def save_open(self, filename: str, mode: str):
        """
        Method to safely open a file, makes sure that the PLAYLIST_FOLDER exists and then sanitizes the filename

        |Mode|Meaning|
        |:-|:-|
        |'r'|open for reading (default)|
        |'w'|open for writing, truncating the file first|
        |'x'|create a new file and open it for writing|
        |'a'|open for writing, appending to the end of the file if it exists|
        |'b'|binary mode|
        |'t'|text mode (default)|
        |'+'|open a disk file for updating (reading and writing)|
        """
        os.makedirs(PLAYLIST_FOLDER, exist_ok=True)
        return open(f"{PLAYLIST_FOLDER}/{sanitize_path(filename)}", mode)

    @commands.command(aliases=["playlists"])
    async def list_stored_playlists(self, ctx: commands.Context):
        """
        List all files in the 'playlists' folder.
        """
        await ctx.send(
            embed=discord.Embed(description="\n".join(os.listdir(PLAYLIST_FOLDER)))
        )

    @commands.command(aliases=["load"])
    async def load_playlist(self, ctx: commands.Context, filename):
        """
        Load the contents of a file in the 'playlists' folder into the global variable PLAYLIST.
        """
        global PLAYLIST
        with self.save_open(filename, "r") as f:
            playlist_temp: list[dict] = json.load(f)
            PLAYLIST = playlist_temp
            await self.queue(ctx)
        await self.play_next_song(ctx)

    @commands.command(aliases=["addtoplaylist"])
    async def add_song_to_stored_playlist(self, ctx: commands.Context, filename, songs):
        """
        Add one or multiple songs to a file in the 'playlists' folder.
        """
        global PLAYLIST
        if isinstance(songs, str):
            PLAYLIST.append(songs)
        elif isinstance(songs, list):
            PLAYLIST.extend(songs)
        await self.save_playlist_to_file(filename)

    @commands.command(aliases=[])
    async def remove_song_from_stored_playlist(
        self, ctx: commands.Context, filename, songs
    ):
        """
        Remove one or multiple songs from a file in the 'playlists' folder.
        """
        # global PLAYLIST
        # if isinstance(songs, str):
        #     songs = [songs]
        # PLAYLIST = [song for song in PLAYLIST if song not in songs]
        # await self.save_playlist_to_file(filename)
        await ctx.send(
            embed=discord.Embed(description=f"Feature currently unavailable")
        )

    @commands.command(aliases=[])
    async def rename_stored_playlist(
        self, ctx: commands.Context, old_filename, new_filename
    ):
        """
        Rename a playlist file.
        """
        os.rename(
            f"{PLAYLIST_FOLDER}/{old_filename}", f"{PLAYLIST_FOLDER}/{new_filename}"
        )
        await ctx.send(
            embed=discord.Embed(title=f"Renamed {old_filename} to {new_filename}")
        )

    @commands.command(aliases=[])
    async def show_stored_playlist(self, ctx: commands.Context, filename):
        """
        Show the contents of a playlist file.
        """
        with self.save_open(filename, "r") as f:
            playlist: list[dict] = json.load(f.read())
            await self.render_playlist(ctx, filename, playlist)

    @commands.command(aliases=[])
    async def show_all_playlists(self, ctx: commands.Context):
        """
        Show the contents of all playlist files.
        """
        playlists = os.listdir(PLAYLIST_FOLDER)
        for playlist in playlists:
            with self.save_open(playlist, "r") as f:
                playlist_temp: list[dict] = json.load(f)
            playlist_temp = "\n".join([song.get(KEY_TITLE) for song in playlist_temp])
            await ctx.send(
                embed=discord.Embed(title=playlist, description=f"{playlist_temp}")
            )

    @commands.command(aliases=[])
    async def get_stored_playlist_length(self, ctx: commands.Context):
        """
        Get the length of the playlist.
        """
        playlists = os.listdir(PLAYLIST_FOLDER)
        for playlist in playlists:
            with self.save_open(playlist, "r") as f:
                await ctx.send(
                    embed=discord.Embed(
                        description=f"The length of {playlist} is {len(f.read().splitlines())}"
                    )
                )

    @commands.command(aliases=["delete"])
    async def delete_stored_playlist(self, ctx: commands.Context, filename):
        """
        Delete a playlist file.
        """
        await ctx.send(
            f"Are you sure you want to delete {filename}? This action cannot be undone. (yes/no)"
        )
        if await self.prompt_user_bool():
            os.remove(f"{PLAYLIST_FOLDER}/{filename}")
            print(f"{filename} has been deleted.")
        else:
            print(f"{filename} was not deleted.")

    async def prompt_user_bool(self):
        """
        Prompt the user for input and return their response.
        """

        def check(message):
            return message.author == self.client.user and message.content.lower() in [
                "yes",
                "no",
            ]

        message = await self.client.wait_for(
            "message",
            check=check,
        )
        return message.content.lower() == "yes"


async def setup(client):
    """Setup cog"""
    await client.add_cog(MusicCommands(client))
