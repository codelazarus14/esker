# Esker's heart and soul
import discord.ext.commands
import os
from dotenv import load_dotenv
import random

# from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['~', 'e.']  # prefixes for bot slash commands

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


@client.command(name='dialogue',
                description='Relive your favorite bits of Mobius Digital Esker Dialogue™.',
                brief='Chat with Esker',
                aliases=['dialog'],
                pass_context=True
                )
async def dialogue(context):
    # figure out how to recreate dialogue system
    await context.send("INVALID DIALOGUE OPTION! \*whistles angrily\*")


@client.command(name='mallow',
                description='Toast a marshmallow to your liking, or even to a crisp.',
                brief='Toast a marshmallow',
                aliases=['marshmallow'],
                pass_context=True
                )
async def mallow(context):
    # marshmallow minigame w pixel art or maybe just numbers for now
    await context.send("NO MALLOWS FOR YOU!")


@client.command(name='tunes',
                description='Wanna listen to some tunes?',
                brief='Do you hear music?',
                aliases=['music', 'tune'],
                pass_context=True
                )
async def tunes(context):
    # Reply with a random OST link if in text chat
    # in voice, put YouTube playlist of OST on shuffle
    await context.send("Damn phonograph is busted... again.")


@client.command(name='rock_assignment',
                description='Discover your true Hearthian name!',
                brief='Assigned rock at slash command',
                aliases=['rock', 'rock_assn', 'ra'],
                pass_context=True
                )
async def rock_assn(context):
    # Hash their username? and then use algorithm to decide
    # what their rock is from a list of possibilities

    # Lists are indexed in python - just dynamic arrays really
    rocks = ["Granite"]
    rock_index = 0  # generate from hash function
    await context.send("I reckon you'd make a fine " + rocks[rock_index] + ", hatchling!")


# keep_alive()
client.run(TOKEN)
