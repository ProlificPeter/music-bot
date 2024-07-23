# Music-Bot
## Lobot
Simple discord bot to add spotify songs to a playlist whenever a spotify link is posted in the chat, enhanced to also provide functionality to bridge the Spotify/Apple Music gap.

Edit your .env file with you discord tokens and keys. Run with python3.12 main.py. You may need to install dependencies. (Requires >= Python 3.10)

You will need to create a bot/application in discord, give it the following permissions:
- "bot"
- "application.commands"
- "Send messages"
- "Read messages/View Channels"
- "Embed Links"

Spotify Authorization requires OAuth approval from the browser. If this needs to run on a headless server, you can run locally and copy cache file to your serveer.

Copy the invitation URL and invite the bot to your server.
Currently runs in a screen session headless.

This is a fork of [discord_spotify project from rundro](https://github.com/rundro/discord_spotify)
