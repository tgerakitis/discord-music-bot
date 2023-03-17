# Discord music bot
## Requirements
* Docker
* optional: docker-compose
## Usage
### Create a Discord bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) website and sign in with your Discord account.
2. Click on the "New Application" button to create a new application.
3. Give your application a name, and then click on the "Create" button.
4. Click on the "Bot" tab on the left-hand side of the screen, then click on the "Add Bot" button.
5. Confirm that you want to add a bot to your application by clicking on the "Yes, do it!" button.
6.  Copy the bot token by clicking on the "Copy" button **you will need it later**
7. Keep the bot token safe and secure, as anyone with access to it can control your bot.
8. **Important**: Don't forget to enable 
   * ```PRESENCE  INTENT``` & 
   * ```MESSAGE CONTENT INTENT``` 
   
   and save the changes
9. Go to Oauth2 &rarr; URL Generator and select ```bot``` scope
10. Select the following bot permissions 
   * ```GENERAL PERMISSIONS``` &rarr; ```Read Messages/View Channels```
   * ```TEXT PERMISSIONS```&rarr; ```Send Messages```
   * ```VOICE PERMISSIONS```&rarr; ```Connect```
   * ```VOICE PERMISSIONS```&rarr; ```Speak```
11. Follow the generated invite link at the bottom and connect the bot to your discord server
### Start the bot
1. Copy the example ```docker-compose.yml``` and set your bot token accordingly
```
version: '3'
services:
  discord-music-bot:
    image: tgerakitis/discord-music-bot
    restart: always
    environment:
        DISCORD_BOT_TOKEN: <discord bot token>
        #COMMAND_PREFIX: prefix of your choice, default is !
```
2.  run ```docker-compose up -d```
3.  Make sure your bot has all relevant server roles to read your text channels and is allowed to join your voice channels
4.  In chat text ```!play <song of your choice>```

# Development
Clone this repo and execute ```docker-compose up```
Debugger settings for Vscode are provided in the ```.vscode/launch.json```

Enjoy!