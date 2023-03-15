from discord.ext import commands
from bs4 import BeautifulSoup
import os
import requests
import youtube_dl
import subprocess

AUDIO_FILENAME = "audio.mp3"
HTML_PARSER = "html.parser"

bot = commands.Bot(command_prefix="!")


@bot.command()
async def music(ctx, *, query):
    await ctx.send(f"Searching for {query}...")

    # Search on YouTube
    youtube_results = search_youtube(query)
    if youtube_results:
        await ctx.send("Found on YouTube!")
        best_quality = get_best_quality(youtube_results)
        download_video(best_quality)
        play_audio()
        return

    # Search on Bandcamp
    bandcamp_results = search_bandcamp(query)
    if bandcamp_results:
        await ctx.send("Found on Bandcamp!")
        download_bandcamp(bandcamp_results)
        play_audio()
        return

    # Search on SoundCloud
    soundcloud_results = search_soundcloud(query)
    if soundcloud_results:
        await ctx.send("Found on SoundCloud!")
        best_quality = get_best_quality(soundcloud_results)
        download_audio(best_quality)
        play_audio()


def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, HTML_PARSER)
    videos = soup.find_all("a", class_="yt-uix-tile-link")
    return [f"https://www.youtube.com{video['href']}" for video in videos]


def search_bandcamp(query):
    url = f"https://bandcamp.com/search?q={query}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, HTML_PARSER)
    albums = soup.find_all("li", class_="searchresult")
    if not albums:
        return None
    album_url = albums[0].find("a")["href"]
    return f"https://bandcamp.com{album_url}"


def search_soundcloud(query):
    url = f"https://soundcloud.com/search?q={query}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, HTML_PARSER)
    tracks = soup.find_all("h2", class_="trackItem__heading")
    return [f"https://soundcloud.com{track.find('a')['href']}" for track in tracks]


def get_best_quality(urls):
    ydl = youtube_dl.YoutubeDL({"quiet": True})
    for url in urls:
        with ydl:
            info = ydl.extract_info(url, download=False)
        formats = info["formats"]
        best = max(formats, key=lambda f: f.get("filesize", 0))
        if best["format_id"].startswith("audio"):
            return best["url"]
    return None


def download_video(url):
    subprocess.call(
        [
            "youtube-dl",
            "-f",
            "bestaudio",
            "--audio-format",
            "mp3",
            "-o",
            AUDIO_FILENAME,
            url,
        ]
    )


def download_bandcamp(url):
    subprocess.call(
        ["youtube-dl", "-x", "--audio-format", "mp3", "-o", AUDIO_FILENAME, url]
    )


def download_audio(url):
    subprocess.call(["wget", "-O", AUDIO_FILENAME, url])


def play_audio():
    subprocess.call(["ffplay", "-nodisp", "-autoexit", "-i", AUDIO_FILENAME])


bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
