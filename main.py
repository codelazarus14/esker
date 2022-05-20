import discord.ext.commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv('RYTHM_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['/']  # prefixes for bot slash commands

''' TODO: make Cogs for different slash command types: https://docs.pycord.dev/en/master/ext/commands/cogs.html
    add stop/disconnect and queueing system
    on shutdown, bot leaves voice channels
'''
client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if client.user.mentioned_in(message) and message.content == client.user.mention:
        await message.channel.send(f'My prefixes are `{BOT_PREFIX}`')
    await client.process_commands(message)


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


@client.command(name='play',
                description='Wanna listen to some tunes?',
                brief='Do you hear music?',
                aliases=[],
                pass_context=True
                )
async def play(context):
    user = context.author
    user_voice = user.voice
    # check if user in voice
    if user_voice is not None:
        # get user VoiceChannel
        channel = user_voice.channel
        # TODO: make this check if bot is not in any voice channel
        if len(client.voice_clients) == 0:
            ''' doesn't account for old bot instance left in voice - unreliable unless we force it
                to disconnect from everything when being shut down - override client.run() below vvv'''
            await context.send(f'Connecting to channel `#{channel.name}`')
            # create player with audio source
            voice_client = await channel.connect()
        else:
            # TODO: make this check if bot is already in a channel, only move if necessary
            await context.send(f'Moving to channel `#{channel.name}`')
            voice_client = client.voice_clients[0]
            await voice_client.move_to(channel)

        # TODO: temporary - replace with streamed audio from YouTube
        audio_source = discord.FFmpegPCMAudio('C:/Users/samed/PycharmProjects/esker/Ugly God FTBT.mp3')
        if not voice_client.is_playing():
            await context.send("Starting audio")
            voice_client.play(audio_source, after=lambda e: print('Done playing audio', e))
        else:
            await context.send("Already playing audio")
            # TODO: create queue of audio sources to work through

        # once audio finishes, bot goes quiet - wait for timeout or disconnect..
    else:
        await context.send('User is not in a voice channel')


def chat_styler(text):
    """used to style text for fancy chat output"""
    # TODO: try using rythm-style embed if i feel up for it
    return "**\n" + text + "**\n```css" \
                           "\n[----------------------------------------------" \
                           "-------------------------------------------------]```"


client.run(TOKEN)
# see https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#discord.ext.commands.Bot.run
# on how to override run() and clean up tasks (disconnect from voice?)
