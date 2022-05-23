import discord
from discord.ext import commands

import utils


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.audio_queue: list[tuple] = []
        """List of audio sources to be updated by play(), skip() etc."""
        self.curr_audio: tuple = None, None
        """Current audio source being played"""

    @commands.command(name='play',
                      description='Wanna listen to some tunes?',
                      brief='Do you hear music?',
                      aliases=[],
                      pass_context=True
                      )
    async def play(self, context, *, query):
        user = context.author
        user_voice = user.voice
        msg = ''
        # check if user in voice
        if user_voice is not None:
            vc = await utils.join_voice_channel(self.bot, context, user_voice)

            video, source = utils.search_yt(query)
            if vc.is_playing():
                # Only want to show when we're visibly adding to queue,
                # append might be undone by play on first add
                msg = f"Adding audio `{video['title']}` to queue"
            print(f"~~~Added audio: id:{video['id']} + title:{video['title']}")
            self.audio_queue.append((video, source))

            # keep playing audio until queue exhausted
            if not vc.is_playing():
                await utils.play_next(vc, context, self)
        else:
            msg = 'User is not in a voice channel'
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
            # don't bother using embed if there's nothing playing
            if vc.is_playing():
                await context.send(embed=utils.make_embed(0, self))
                return
        await context.send('No audio in queue')

    @commands.command(name='np',
                      description='See what is currently being played',
                      brief='See current audio source',
                      aliases=['now_playing'],
                      pass_context=True
                      )
    async def now_playing(self, context):
        if len(self.bot.voice_clients) > 0:
            vc: discord.VoiceClient = self.bot.voice_clients[0]
            # don't bother using embed if there's nothing playing
            if vc.is_playing():
                await context.send(embed=utils.make_embed(1, self))
                return
        await context.send('Nothing playing')

    @commands.command(name='skip',
                      description='Skip the current audio being played',
                      brief='Skip this trash',
                      aliases=[],
                      pass_context=True)
    async def skip(self, context):
        msg = 'Not in voice channel'
        if len(self.bot.voice_clients) > 0:
            vc: discord.VoiceClient = self.bot.voice_clients[0]
            if vc.is_connected() and vc.is_playing():
                # use pause = stopping the player = close it
                msg = 'Skipping current audio'
                msg += utils.skip_to_next(vc, self)
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
        msg = 'Not in voice channel'
        if len(self.bot.voice_clients) > 0:
            curr_channel: discord.VoiceChannel = self.bot.voice_clients[0].channel
            if self.bot.voice_clients[0].is_playing():
                self.audio_queue.clear()
            msg = f'Disconnected from `#{curr_channel.name}`'
            await self.bot.voice_clients[0].disconnect()
        await context.send(msg)
