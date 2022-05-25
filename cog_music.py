import asyncio

import discord
from discord.ext import commands

import utils


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.audio_queue: list[tuple] = []
        """List of audio sources to be updated by play(), skip() etc."""
        self.curr_audio: tuple = None, None, None
        """Current audio source being played
        
        | audio[0] = video
        | audio[1] = raw source 
        | audio[2] = play() starting timestamp"""

    @commands.command(name='play',
                      description='Wanna listen to some tunes?',
                      brief='Do you hear music?',
                      aliases=[],
                      pass_context=True
                      )
    async def play(self, context: discord.ext.commands.Context, *, query=None):
        if query is None:
            return await context.send(f"{utils.emph('play')} requires YouTube link or search query")

        user = context.author
        user_voice = user.voice
        # check if user in voice
        if user_voice is not None:
            vc = await utils.join_voice_channel(self.bot, context, user_voice)
            msg_emb = discord.Embed(description='Searching', colour=discord.Colour.dark_green())
            msg = await context.send(embed=msg_emb)
            msg_id = msg.id

            video, source = utils.search_yt(query)
            if vc.is_playing():
                # Only want to show append "happening" when already playing, otherwise
                # indicate first pop after append as "now playing"
                msg: discord.Message = await context.channel.fetch_message(msg_id)
                new_embed = discord.Embed(description=f"Added audio {utils.emph(video['title'])} to queue")
            else:
                new_embed = discord.Embed(description=f"Now playing: {utils.emph(video['title'])}")
            new_embed.colour = discord.Colour.green()
            await msg.edit(embed=new_embed)
            print(f"~~~Added audio: id:{video['id']} + title:{video['title']}")
            self.audio_queue.append((video, source))

            # keep playing audio until queue exhausted
            if not vc.is_playing():
                utils.play_next(vc, context, self)
        else:
            await context.send('User is not in a voice channel')

        # once audio finishes, bot goes quiet - wait for timeout or disconnect..

    @commands.command(name='play_next',
                      description='If playing, the given audio plays. Otherwise it is added to the front of the queue',
                      brief='Add audio to the front of the queue',
                      aliases=['playnext'],
                      pass_context=True)
    async def play_next(self, context: discord.ext.commands.Context, *, query=None):
        # if queue is empty - play normally
        if context.voice_client is None or not context.voice_client.is_playing():
            return await self.play(context=context, query=query)
        user_voice = context.author.voice
        if user_voice is not None:
            vc = await utils.join_voice_channel(self.bot, context, user_voice)
            msg_emb = discord.Embed(description='Searching', colour=discord.Colour.dark_green())
            msg = await context.send(embed=msg_emb)
            msg_id = msg.id

            video, source = utils.search_yt(query)
            if vc.is_playing():
                msg: discord.Message = await context.channel.fetch_message(msg_id)
                new_embed = discord.Embed(description=f"Added audio {utils.emph(video['title'])} to front of queue")
            else:
                new_embed = discord.Embed(description=f"Now playing: {utils.emph(video['title'])}")
            new_embed.colour = discord.Colour.green()
            await msg.edit(embed=new_embed)
            print(f"~~~Added audio: id:{video['id']} + title:{video['title']}")
            # only major difference from play = add to front of queue
            self.audio_queue.insert(0, (video, source))

            # keep playing audio until queue exhausted
            if not vc.is_playing():
                utils.play_next(vc, context, self)
        else:
            await context.send('User is not in a voice channel')

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
                await context.send(embed=utils.make_embed(0, self, context))
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
                return await context.send(embed=utils.make_embed(1, self, context))
        await context.send('Nothing playing')

    @commands.command(name='skip',
                      description='Skip the current audio being played',
                      brief='Skip this trash',
                      aliases=[],
                      pass_context=True)
    async def skip(self, context: discord.ext.commands.Context):
        if len(self.bot.voice_clients) == 0:
            return await context.send('Not in voice channel')
        vc: discord.VoiceClient = self.bot.voice_clients[0]
        if not vc.is_connected() or not vc.is_playing():
            return await context.send('Nothing to skip')

        # threshold - 1-2 people can vote to skip individually, 3+ is a vote
        if len(vc.channel.members) < 3:
            e = discord.Embed(description='*Skipping current audio*',
                              colour=discord.Colour.green())
            next_audio = utils.skip_to_next(vc, self)
            if next_audio:
                e.add_field(name='Now playing:', value=next_audio)
            return await context.send(embed=e)
        # https://stackoverflow.com/questions/69288961/how-to-make-queue-for-songs-and-skip-command-discord-py
        vote = utils.make_embed(2, self, context)  # create temporary message for vote
        vote_msg = await context.send(embed=vote)
        vote_id = vote_msg.id

        await vote_msg.add_reaction(u"\u2705")
        await vote_msg.add_reaction(u"\U0001F6AB")

        await asyncio.sleep(15)  # 15 seconds to vote

        vote_msg: discord.Message = await context.channel.fetch_message(vote_id)
        votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        vote_reacts = [u"\u2705", u"\U0001F6AB"]
        reacted = []
        for react in vote_msg.reactions:
            if react.emoji in vote_reacts:
                async for user in react.users():
                    # find unique user reactions and add to votes
                    # have to turn a User into a Member to get voice status
                    member: discord.Member = await context.guild.fetch_member(user.id)
                    if member.voice.channel.id == vc.channel.id and user.id not in reacted and not user.bot:
                        votes[react.emoji] += 1
                        reacted.append(user.id)

        can_skip = False
        print(f'Vote {vote_id} results: {votes}')
        embed_update = discord.Embed()

        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 \
                    or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.5:
                can_skip = True
                embed_update = discord.Embed(title='Vote to Skip successful',
                                             description='*Skipping current audio*',
                                             colour=discord.Colour.green())
        if not can_skip:
            embed_update = discord.Embed(title='Vote to Skip failed',
                                         description='*At least 50% of members\' votes needed to skip*',
                                         colour=discord.Colour.red())
        embed_update.set_footer(text='')

        await vote_msg.clear_reactions()
        await vote_msg.edit(embed=embed_update)

        if can_skip:
            await context.send(utils.skip_to_next(vc, self))

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
            msg = f'Disconnected from {utils.emph("#" + curr_channel.name)}'
            await self.bot.voice_clients[0].disconnect()
        await context.send(msg)
