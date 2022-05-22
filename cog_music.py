import discord
from discord.ext import commands

import utils

# TODO: add more information to audio queue (name, track length, author etc.) and update embed


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.audio_queue: list[discord.AudioSource] = []  # list of AudioSources added to in play()

    @commands.command(name='play',
                      description='Wanna listen to some tunes?',
                      brief='Do you hear music?',
                      aliases=[],
                      pass_context=True
                      )
    async def play(self, context):
        user = context.author
        user_voice = user.voice
        msg = 'User is not in a voice channel'
        # check if user in voice
        if user_voice is not None:
            vc: discord.VoiceClient = await utils.join_voice_channel(self.bot, context, user_voice)

            # TODO: temporary - replace with streamed audio from YouTube
            audio_source = discord.FFmpegPCMAudio('C:/Users/samed/PycharmProjects/esker/Ugly God FTBT.mp3')
            msg = f'Adding audio {audio_source} to queue'
            self.audio_queue.append(audio_source)

            # keep playing audio until queue exhausted
            if not vc.is_playing():
                utils.play_next(vc, context, self.audio_queue)
        await context.send(msg)

        # once audio finishes, bot goes quiet - wait for timeout or disconnect..

    @commands.command(name='queue',
                      description='View the pending audio queue',
                      brief='View audio queue',
                      aliases=['q'],
                      pass_context=True)
    async def queue(self, context: discord.ext.commands.Context):
        if len(self.bot.voice_clients) > 0:
            vc: discord.VoiceClient = self.bot.voice_clients[0]
            if vc.is_playing():
                await context.send(embed=utils.make_embed(0, self.audio_queue, vc))
                return
        await context.send('Nothing playing')

    @commands.command(name='np',
                      description='See what is currently being played',
                      brief='See current audio source',
                      aliases=['now_playing'],
                      pass_context=True
                      )
    async def now_playing(self, context):
        msg = 'Currently playing: '
        if len(self.bot.voice_clients) > 0:
            vc: discord.VoiceClient = self.bot.voice_clients[0]
            if vc.is_playing():
                msg += f'{vc.source}'
        await context.send(msg)

    @commands.command(name='skip',
                      description='Skip the current audio being played',
                      brief='Skip this trash',
                      aliases=[],
                      pass_context=True)
    async def skip(self, context):
        msg = 'Not in voice yet'
        if len(self.bot.voice_clients) > 0:
            vc: discord.VoiceClient = self.bot.voice_clients[0]
            if vc.is_connected() and vc.is_playing():
                # use pause = stopping the player = close it
                msg = 'Skipping current audio'
                msg += utils.skip_to_next(vc, self.audio_queue)
            else:
                msg = 'Nothing to skip'
        await context.send(msg)

    @commands.command(name='clear',
                      description='Clears the entire audio queue',
                      brief='Clears audio queue',
                      aliases=[],
                      pass_context=True
                      )
    async def clear(self, context):
        msg = 'Nothing to clear'
        if len(self.audio_queue) > 0:
            self.audio_queue.clear()
            msg = 'Cleared audio queue'
        await context.send(msg)

    @commands.command(name='join',
                      description='Moves the bot into the user\'s current voice channel',
                      brief='Make bot join voice',
                      aliases=['move'],
                      pass_context=True
                      )
    async def join(self, context):
        user = context.author
        if user.voice is not None:
            await utils.join_voice_channel(self.bot, context, user.voice)
        else:
            await context.send('User is not in a voice channel')

    @commands.command(name='disconnect',
                      description='Makes the bot disconnect from voice',
                      brief='Kick the bot outta voice',
                      aliases=['d'],
                      pass_context=True
                      )
    async def disconnect(self, context):
        msg = 'Not in voice yet'
        if len(self.bot.voice_clients) > 0:
            curr_channel: discord.VoiceChannel = self.bot.voice_clients[0].channel
            if self.bot.voice_clients[0].is_playing():
                curr_audio: discord.AudioSource = self.audio_queue[0]
                self.audio_queue.clear()
                self.audio_queue.append(curr_audio)
            msg = f'Disconnected from `#{curr_channel.name}`'
            await self.bot.voice_clients[0].disconnect()
        await context.send(msg)
