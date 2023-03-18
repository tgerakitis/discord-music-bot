# 🎶 Discord music bot 🎶

A simple Discord music bot with basic functionality. Please note that this bot may have bugs and has not been extensively tested.

## Development

1. Clone this repository.
2. Run `docker-compose up` in the root directory to start the bot.
3. Use the provided debugger settings for VS Code in [`.vscode/launch.json`](.vscode/launch.json).

## Requirements

* Docker

## Usage
### In discord
* Type `!play <search text>` to add a song to the queue.
* Type `!stop` to stop and disconnect the bot.
* Type `!q` to list the current song queue.
* Type `!skip` to skip to the next song.

### Environment Variables

* `DISCORD_BOT_TOKEN` - Required. Set your Discord bot token (see instructions below).
* `COMMAND_PREFIX` - Optional. The prefix for bot commands. Default is `!`.

### Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and sign in to your account.
2. Click the "New Application" button and give your application a name, then click "Create."
3. Click the "Bot" tab on the left, then click "Add Bot."
4. Click "Yes, do it!" to confirm adding a bot to your application.
5. Copy the bot token by clicking "Copy" (you will need this later).
6. Keep the bot token secure as anyone with access to it can control your bot.
7. Enable the following:
   * `PRESENCE INTENT`
   * `MESSAGE CONTENT INTENT`
8. Save the changes.
9. Go to Oauth2 > URL Generator and select the `bot` scope.
10. Select the following bot permissions:
    * `GENERAL PERMISSIONS`: `Read Messages/View Channels`
    * `TEXT PERMISSIONS`: `Send Messages`
    * `VOICE PERMISSIONS`: `Connect`
    * `VOICE PERMISSIONS`: `Speak`
11. Follow the generated invite link to add the bot to your Discord server.

### Start the Bot

#### Docker Only

Run the following command to start the bot:

```docker run -d -e DISCORD_BOT_TOKEN=<discord bot token> tgerakitis/discord-music-bot```

#### Docker Compose

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

2. Run `docker-compose up -d`.
3. Make sure your bot has all relevant server roles to read your text channels and is allowed to join your voice channels.
4. In chat, type `!play <song of your choice>`.

Enjoy! 🤖
