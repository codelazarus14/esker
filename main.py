# Esker's heart and soul
import asyncio
import logging

import discord.ext.commands
import os
from dotenv import load_dotenv

import cog_general
import utils

load_dotenv()

TOKEN = os.getenv('ESKER_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['e.']  # prefixes for bot slash commands

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='log/esker-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# TODO:
#   add e.define = search outer wilds fan wiki for title of article + respond w intro paragraph
#   copy useful code from rythm = playing audio, creating embeds

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)
client.add_cog(cog_general.General(client))


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.content == client.user.mention:
        await message.channel.send(f"My prefixes are `{BOT_PREFIX}`")
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
