# Esker's heart and soul
import discord.ext.commands
import os
from dotenv import load_dotenv
import random

# from keep_alive import keep_alive
# from dialogue import DialogueTree

load_dotenv()

TOKEN = os.getenv('RYTHM_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['~', 'e.']  # prefixes for bot slash commands

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
        'Greetings, hatchling!',
        'Hi there!',
        'Hello!',
        'Nice lunar weather we\'re having...',
        'Welcome to the Lunar Outpost! I don\'t get visitors very often...'
    ]
    await context.send(random.choice(responses))


def chat_styler(text):
    """used to style text for fancy chat output"""
    # TODO: center bold paragraph above the orange line for immersive purposes
    return "**\n" + text + "**\n```css" \
                           "\n[----------------------------------------------" \
                           "-------------------------------------------------]```"


# keep_alive()
client.run(TOKEN)
