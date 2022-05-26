import asyncio
import logging

import discord.ext.commands
import os
from dotenv import load_dotenv

import cog_general
import cog_music

load_dotenv()

TOKEN = os.getenv('RYTHM_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['!', 'rr.', 'rr ']  # prefixes for bot slash commands

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# TODO:
#  maybe localize message strings somewhere so i can refer to them (like a strings.xml?)

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX, help_command=None)
# load commands by category
client.add_cog(cog_music.Music(client))
client.add_cog(cog_general.General(client))


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.content == client.user.mention:
        await message.channel.send(f'My prefixes are `{BOT_PREFIX}`')
    # necessary - after overriding on_message() we leave rest to commands
    await client.process_commands(message)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.guilds:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(TOKEN)
