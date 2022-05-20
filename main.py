import discord.ext.commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv('RYTHM_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['/']  # prefixes for bot slash commands

# TODO: make Cogs for different slash command types: https://docs.pycord.dev/en/master/ext/commands/cogs.html

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


# Esker says hi!
@client.command(name='hello',
                description='Say hi to an old friend.',
                brief='Say hello',
                aliases=['hi', 'greetings'],
                pass_context=True
                )
async def hello(context):
    responses = [
        'Greetings, fellow traveler!',
        'Hi there!',
        'Hello!'
    ]
    await context.send(random.choice(responses))


def chat_styler(text):
    """used to style text for fancy chat output"""
    # TODO: try using rythm-style embed if i feel up for it
    return "**\n" + text + "**\n```css" \
                           "\n[----------------------------------------------" \
                           "-------------------------------------------------]```"


# keep_alive()
client.run(TOKEN)
