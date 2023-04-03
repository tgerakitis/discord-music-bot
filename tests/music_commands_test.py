from unittest.mock import Mock

import sys
sys.path.append("/workspace")
from app.commands.music_commands import KEY_TITLE, KEY_URL, MusicCommands
from app.bot import PLAYLIST

async def test_play_command():
    print("hallo2", flush=True)
    ctx = Mock()
    ctx.author.voice = True
    args = ["song_name"]
    await MusicCommands().play(MusicCommands(), ctx, *args)
    assert len(PLAYLIST) == 1
    assert PLAYLIST[0][KEY_TITLE] == "song_name"
    assert VOICE_CLIENT.is_connected()

async def test_queue_command():
    ctx = Mock()
    await MusicCommands.queue(MusicCommands(), ctx)
    # Check if the bot sends a message containing "PLAYLIST is **EMPTY**" if the playlist is empty
    # Check if the bot sends a message containing "Current Playlist" if the playlist is not empty

async def test_stop_command():
    global PLAYLIST, VOICE_CLIENT
    ctx = Mock()
    PLAYLIST = [{KEY_TITLE: "song_name", KEY_URL: "song_url"}]
    VOICE_CLIENT = Mock()
    await MusicCommands.stop(MusicCommands(), ctx)
    assert len(PLAYLIST) == 0
    assert VOICE_CLIENT.stop.called
    assert VOICE_CLIENT.disconnect.called
    assert VOICE_CLIENT is None

async def test_skip_command():
    global VOICE_CLIENT
    ctx = Mock()
    VOICE_CLIENT = Mock()
    await MusicCommands.skip(MusicCommands(), ctx)
    assert VOICE_CLIENT.stop.called

async def test_move_command():
    global PLAYLIST
    ctx = Mock()
    PLAYLIST = [
        {KEY_TITLE: "song1", KEY_URL: "song1_url"},
        {KEY_TITLE: "song2", KEY_URL: "song2_url"},
        {KEY_TITLE: "song3", KEY_URL: "song3_url"},
    ]
    args = ["2"]
    await MusicCommands.move(MusicCommands(), ctx, *args)
    assert PLAYLIST == [
        {KEY_TITLE: "song2", KEY_URL: "song2_url"},
        {KEY_TITLE: "song1", KEY_URL: "song1_url"},
        {KEY_TITLE: "song3", KEY_URL: "song3_url"},
    ]
