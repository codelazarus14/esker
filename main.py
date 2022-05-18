# Esker's heart and soul
import discord.ext.commands
import os
from dotenv import load_dotenv
import random

# from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = "~"  # prefix for bot slash commands

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


# Esker says hi!
@client.command(name='hello',
                description='Ask how our old friend is doing.',
                brief='Say hello',
                aliases=['hi', 'greetings'],
                pass_context=True
                )
async def hello(context):
    possible_responses = [
        'Greetings, hatchling!',
        'Hi there!',
        'Hello!',
        'What brings you to the Lunar Outpost on this fine day?'
    ]
    await context.send(random.choice(possible_responses))

# keep_alive()
client.run(TOKEN)
