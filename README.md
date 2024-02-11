# 🎶 Discord music bot 🎶

A simple Discord music bot with basic functionality. Please note that this bot may have bugs and has not been extensively tested.

## Installation

### Docker Only

Run the following command to start the bot:

`docker run -d -e DISCORD_BOT_TOKEN=<discord bot token> tgerakitis/discord-music-bot`

### Docker Compose

1. Copy the example `docker-compose.yml` file and set your bot token:

    ```
    version: '3'
    services:
      discord-music-bot:
        image: tgerakitis/discord-music-bot
        restart: always
        environment:
            DISCORD_BOT_TOKEN: <discord bot token>
            # COMMAND_PREFIX: prefix of your choice, default is !
    ```

2. Run `docker compose up -d`.
3. Make sure your bot has all relevant server roles to read your text channels and is allowed to join your voice channels.
4. In chat, type `!play <song of your choice>`.

## Development

1. Clone this repository.
2. Copy the contents of [`.env-template`](.env-template) into a file called `.env` in the root and set your bot token.
3. Run `docker compose up --build` in the root directory to start the bot.
4. Use the provided debugger settings for VS Code in [`.vscode/launch.json`](.vscode/launch.json).

**Note**: For local development the default `COMMAND_PREFIX` is set to `!!`

## Requirements

-   Docker

## Usage

### In discord

-   Type `!play <search text>` to add a song to the queue.
-   Type `!stop` to stop and disconnect the bot.
-   Type `!q` to list the current song queue.
-   Type `!skip` to skip to the next song.

### Environment Variables

-   `DISCORD_BOT_TOKEN` - Required. Set your Discord bot token (see instructions below).
-   `COMMAND_PREFIX` - Optional. The prefix for bot commands. Default is `!`.

### Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and sign in to your account.
2. Click the "New Application" button and give your application a name, then click "Create."
4. Click the "Bot" tab on the left, name the bot and copy the API token (reset token if you can not see this options)
5. Keep the bot token secure as anyone with access to it can control your bot.
6. Still in the "Bot" tab, scroll down and enable the following "Privileged Gateway Intents":
    - `PRESENCE INTENT`
    - `MESSAGE CONTENT INTENT`
6. Save the changes if not saved automatically.
9. Go to Oauth2 > URL Generator and select the `bot` scope.
10. Select the following bot permissions:
    - `GENERAL PERMISSIONS`: `Read Messages/View Channels`
    - `TEXT PERMISSIONS`: `Send Messages`
    - `VOICE PERMISSIONS`: `Connect`
    - `VOICE PERMISSIONS`: `Speak`
11. Follow the generated invite link to add the bot to your Discord server.

Enjoy! 🤖
