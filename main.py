# Esker's heart and soul
import asyncio

import discord.ext.commands
import os
from dotenv import load_dotenv
import random

# from keep_alive import keep_alive
# from dialogue import DialogueTree

load_dotenv()

TOKEN = os.getenv('ESKER_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['~', 'e.']  # prefixes for bot slash commands

# TODO: make Cogs + files for different slash command types: https://docs.pycord.dev/en/master/ext/commands/cogs.html
#   add e.define = search outer wilds fan wiki for title of article + respond w intro paragraph
#   add e.stars/constellation = like the tumblr post but uses asyncio over 22 mins to slowly remove them, also mogus
#   override help/make pretty with embedded thing like sheep/rythm or don't idk

client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.content == client.user.mention:
        await message.channel.send(chat_styler("My prefixes are `{}`".format(BOT_PREFIX)))
    # important! default on_message() is being overridden - pass message onto commands
    await client.process_commands(message)


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
    await context.send(chat_styler(random.choice(responses)))


@client.command(name='dialogue',
                description='Relive your favorite bits of Mobius Digital Esker Dialogue™.',
                brief='Chat with Esker',
                aliases=['dialog'],
                pass_context=True
                )
async def dialogue(context):
    """ TODO: figure out how to recreate dialogue system
         this is honestly such an entangled mess to work through - maybe replace with
         lucabot-style random line regurgitation """
    # dtree = DialogueTree(dialogue.NODES, 'start')
    # await dtree.evaluate(dtree.nodes[0])
    await context.send("sorry pal i gotta develop a dialogue system first")


@client.command(name='mallow',
                description='Toast a marshmallow to your liking, or even burn it to a crisp.',
                brief='Toast a marshmallow',
                aliases=['marshmallow'],
                pass_context=True
                )
async def mallow(context):
    # marshmallow minigame w pixel art or maybe just numbers for now
    await context.send(chat_styler("NO MALLOWS FOR YOU!"))


@client.command(name='tunes',
                description='Wanna listen to some tunes?',
                brief='Do you hear music?',
                aliases=['music', 'tune'],
                pass_context=True
                )
async def tunes(context):
    # Reply with a random OST link if in text chat
    # in voice, put YouTube playlist of OST on shuffle
    await context.send(chat_styler("Looks like the tape player is broken... again. Maybe I can ask Hornfels about it "
                                   "the next time they check up on me. They oughta be able to get Slate's engineering "
                                   "genius on board."))


@client.command(name='rock_assn',
                description='Discover your true Hearthian name!',
                brief='Assigned rock at slash command',
                aliases=['rock', 'rock_assignment', 'ra'],
                pass_context=True
                )
async def rock_assn(context):
    # list of rocks from https://en.wikipedia.org/wiki/List_of_rock_types
    rocks = ["Arkose", "Basalt", "Breccia", "Gypsum", "Caliche", "Coquina", "Flint", "Ijolite"
             "Mariposite", "Skarn", "Pyrite", "Schist", "Scoria", "Shale", "Tufa"]
    # generate rock name from user id
    rock_index = abs(hash(context.author.id)) % len(rocks)
    await context.send(chat_styler("I reckon you'd make a fine " + rocks[rock_index] + ", hatchling!"))


def chat_styler(text):
    """used to style text for fancy chat output"""
    # TODO: redesign chat styler to be mobile-friendly.. maybe remove orange line
    return "**\n" + text + "**\n```css" \
                           "\n[----------------------------------------------" \
                           "-------------------------------------------------]```"


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.guilds:
            print(server.name)
        await asyncio.sleep(600)


# keep_alive()
client.run(TOKEN)
