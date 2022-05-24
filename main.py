import asyncio

import discord.ext.commands
import os
from dotenv import load_dotenv

import cog_general
import cog_music

load_dotenv()

TOKEN = os.getenv('RYTHM_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['/', 'rr.', 'rr ']  # prefixes for bot slash commands

# TODO:
#  override default help, add embed support for play() and np() based on rythm's look
#  add playskip() to merge function of play and skip
#  get voice client from context instead of looking at voice_clients
#  https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=command#helpcommand
#  maybe localize message strings somewhere so i can refer to them (like a strings.xml?)
#  on idle/shutdown, bot leaves voice channels
#  remove prints or replace w logging

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)
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
# see https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#discord.ext.commands.Bot.run
# on how to override run() and clean up tasks (disconnect from voice?)
