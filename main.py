# Esker's heart and soul
import asyncio

import discord.ext.commands
import os
from dotenv import load_dotenv

import cog_general
import utils

load_dotenv()

TOKEN = os.getenv('ESKER_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['e.']  # prefixes for bot slash commands

# TODO: make Cogs + files for different slash command types: https://docs.pycord.dev/en/master/ext/commands/cogs.html
#   add e.define = search outer wilds fan wiki for title of article + respond w intro paragraph
#   add e.stars/constellation = like the tumblr post but uses asyncio over 22 mins to slowly remove them, also mogus
#   copy useful code from rythm = playing audio, creating embeds

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)
client.add_cog(cog_general.General(client))


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.content == client.user.mention:
        await message.channel.send(utils.chat_styler("My prefixes are `{}`".format(BOT_PREFIX)))
    # important! default on_message() is being overridden - pass message onto commands
    await client.process_commands(message)


# TODO: fix or delete
async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.guilds:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
