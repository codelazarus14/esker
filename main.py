# import asyncio

import discord.ext.commands
import os
from dotenv import load_dotenv
import random

load_dotenv()

TOKEN = os.getenv('RYTHM_BOT_SECRET')  # secret token for bot to run
BOT_PREFIX = ['/', 'rr.', 'rr ']  # prefixes for bot slash commands

''' TODO: make Cogs for different slash command types (music vs. general):
        https://docs.pycord.dev/en/master/ext/commands/cogs.html
    build messages over the course and send one await context.send() at the end?
    on shutdown, bot leaves voice channels
'''
client = discord.ext.commands.Bot(command_prefix=BOT_PREFIX)
audio_queue: list[discord.AudioSource] = []  # list of AudioSources to be created in play()


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
    msg = 'User is not in a voice channel'
    # check if user in voice
    if user_voice is not None:
        vc: discord.VoiceClient = await join_voice_channel(context, user_voice)

        # TODO: temporary - replace with streamed audio from YouTube
        audio_source = discord.FFmpegPCMAudio('C:/Users/samed/PycharmProjects/esker/Ugly God FTBT.mp3')
        msg = f'Adding audio {audio_source} to queue'
        audio_queue.append(audio_source)

        # keep playing audio until queue exhausted
        if not vc.is_playing():
            # TODO: use play_next() merged from get_next w recursive call from after= to get .play looping
            vc.play(audio_queue[0], after=lambda e: get_next_source(vc, context))
    await context.send(msg)

    # once audio finishes, bot goes quiet - wait for timeout or disconnect..


@client.command(name='queue',
                description='View the pending audio queue',
                brief='View audio queue',
                aliases=['q'],
                pass_context=True)
async def queue(context):
    # TODO: break into enumerated lines, also might depend on whether
    # the queue becomes a mapping of audio sources to name, length etc.
    await context.send(f'Queue: {audio_queue}')


@client.command(name='skip',
                description='Skip the current audio being played',
                brief='Skip this trash',
                aliases=[],
                pass_context=True)
async def skip(context):
    if len(client.voice_clients) > 0:
        vc: discord.VoiceClient = client.voice_clients[0]
        if vc.is_connected() and vc.is_playing():
            # use pause = stopping the player = close it
            await context.send('Skipping current audio')
            get_next_source(vc, context)
        else:
            await context.send('Nothing to skip')
    else:
        await context.send('Not in voice yet')


@client.command(name='join',
                description='Moves the bot into the user\'s current voice channel',
                brief='Make bot join voice',
                aliases=['move'],
                pass_context=True
                )
async def join(context):
    user = context.author
    if user.voice is not None:
        await join_voice_channel(context, user.voice)


@client.command(name='disconnect',
                description='Makes the bot disconnect from voice',
                brief='Kick the bot outta voice',
                aliases=['d'],
                pass_context=True
                )
async def disconnect(context):
    curr_channel: discord.VoiceChannel = client.voice_clients[0].channel
    global audio_queue
    if client.voice_clients[0].is_playing():
        curr_audio: discord.AudioSource = audio_queue[0]
        audio_queue.clear()
        audio_queue.append(curr_audio)
    await context.send(f'Disconnected from `#{curr_channel.name}`')
    await client.voice_clients[0].disconnect()


@client.command(name='clear',
                description='Clears the entire audio queue',
                brief='Clears audio queue',
                aliases=[],
                pass_context=True
                )
async def clear(context):
    global audio_queue
    audio_queue.clear()
    await context.send('Cleared audio queue')


def get_next_source(vc: discord.VoiceClient, context):
    vc.pause()
    if len(audio_queue) > 0:
        del audio_queue[0]
        # still another audio source in the queue? swap it in
        if len(audio_queue) > 0:
            vc.source = audio_queue[0]
            vc.resume()
            # TODO: how to announce next track without awaiting context.send()?
            # await context.send(f'Now playing {vc.source}')
            print(f'Now playing {vc.source}')


async def join_voice_channel(context, user_voice):
    # get user VoiceChannel
    channel: discord.VoiceChannel = user_voice.channel
    ''' TODO:
        doesn't account for old bot instance left in voice - unreliable unless we force it
        to disconnect from everything when being shut down - override client.run() below'''
    if len(client.voice_clients) > 0:
        # if client already exists
        voice_client = client.voice_clients[0]
        if voice_client.is_connected() and voice_client.channel is not channel:
            await context.send(f'Moving to channel `#{channel.name}`')
    else:
        # create new voice client and connect to current channel
        voice_client = await channel.connect()
        await context.send(f'Connecting to channel `#{channel.name}`')
    await voice_client.move_to(channel)
    return voice_client


def chat_styler(text):
    """used to style text for fancy chat output"""
    # TODO: try using rythm-style embed if i feel up for it
    return "**\n" + text + "**\n"


# async def list_servers():
#     await client.wait_until_ready()
#     while not client.is_closed:
#         print("Current servers:")
#         for server in client.guilds:
#             print(server.name)
#         await asyncio.sleep(600)
#
# client.loop.create_task(list_servers())
client.run(TOKEN)
# see https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=bot#discord.ext.commands.Bot.run
# on how to override run() and clean up tasks (disconnect from voice?)
