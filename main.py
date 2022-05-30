# Esker's heart and soul
import asyncio
import logging
import os

import discord.ext.commands
from dotenv import load_dotenv

import cog_fun
import cog_general

load_dotenv()

TOKEN = os.getenv('ESKER_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['e.']  # prefixes for bot slash commands

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='log/esker-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)
client.add_cog(cog_general.General(client))
client.add_cog(cog_fun.Fun(client))


@client.event
async def on_ready():
    print(f'Logged in as {client.user}\n----------')


@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.content == client.user.mention:
        await message.channel.send(f"My prefixes are `{BOT_PREFIX}`")
    # important! default on_message() is being overridden - pass message onto commands
    await client.process_commands(message)


async def list_servers():
    await client.wait_until_ready()
    while True:
        print("Current servers:")
        for server in client.guilds:
            print(f">> {server.name}")
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
