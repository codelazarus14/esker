import asyncio
import logging

import discord
from discord.ext import commands

import utils

logger = logging.getLogger('discord')


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
                      description='*Wanna listen to some tunes?*\n Given a link or search query, '
                                  'the bot will find an audio source on YouTube to be played immediately '
                                  'or added to the end of the audio queue.',
                      brief='Do you hear music?',
                      aliases=[],
                      pass_context=True
                      )
    async def play(self, context: discord.ext.commands.Context, *, query=None):
        if query is None:
            return await context.send(f"*{utils.emph('play')}* requires YouTube link or search query")

        user = context.author
        user_voice = user.voice
        # check if user in voice
        if user_voice is not None:
            vc = await utils.join_voice_channel(context, user_voice)
            # temp message to let the user know we're going to query - avoid delay in call to search_yt() below
            msg_emb = utils.make_embed(3, self, context)
            msg = await context.send(embed=msg_emb)
            # grab message id for later
            msg_id = msg.id

            # retrieve video: bunch of metadata + source: raw audio data
            video, source = utils.search_yt(query)
            # embed to display result of query + updating queue
            new_embed = utils.make_embed(4, self, context)
            if vc.is_playing():
                # only want to show queue "updating" when we're not about to play the new source
                msg: discord.Message = await context.channel.fetch_message(msg_id)
                new_embed.description = f"Added audio [{video['title']}]" \
                                        f"(https://youtube.com/watch?v={video['id']}) to queue"
            else:
                new_embed.description = f"Now playing: [{video['title']}]" \
                                        f"(https://youtube.com/watch?v={video['id']})"
            # should probably set this in utils.make_embed()..
            thumb_url = video['thumbnails'][1]['url']
            new_embed.set_thumbnail(url=thumb_url)
            # clear temp message and update user with result
            await msg.delete()
            await context.send(embed=new_embed)
            logger.log(logging.INFO, f"play: ~~~Added audio: id:{video['id']}, title:{video['title']}, "
                                     f"url=https://youtube.com/watch?v={video['id']}")
            self.audio_queue.append((video, source))

            # keep playing audio until queue exhausted
            if not vc.is_playing():
                utils.play_next(vc, context, self)
                # TODO: fix audio buffering - use asyncio.sleep() and tasks
        else:
            await context.send('User is not in a voice channel')

    @commands.command(name='play_next',
                      description='Same as play but adds to the front of the audio queue.',
                      brief='Quit cuttin\' in line!',
                      aliases=['playnext'],
                      pass_context=True)
    async def play_next(self, context: discord.ext.commands.Context, *, query=None):
        # if queue is empty - play normally
        if context.voice_client is None or not context.voice_client.is_playing():
            return await self.play(context=context, query=query)
        # most of this is copied from play() - we just need to change one piece - make a helper?
        user = context.author
        user_voice = user.voice
        if user_voice is not None:
            vc = await utils.join_voice_channel(context, user_voice)
            msg_emb = utils.make_embed(3, self, context)
            msg = await context.send(embed=msg_emb)
            msg_id = msg.id

            video, source = utils.search_yt(query)
            new_embed = utils.make_embed(4, self, context)
            if vc.is_playing():
                msg: discord.Message = await context.channel.fetch_message(msg_id)
                new_embed.description = f"Added audio [{video['title']}]" \
                                        f"(https://youtube.com/watch?v={video['id']}) to front of queue"
            else:
                new_embed.description = f"Now playing: [{video['title']}]" \
                                        f"(https://youtube.com/watch?v={video['id']})"
            thumb_url = video['thumbnails'][1]['url']
            new_embed.set_thumbnail(url=thumb_url)
            await msg.delete()
            await context.send(embed=new_embed)
            logger.log(logging.INFO, "play_next: ~~~Added audio: id:{video['id']}, title:{video['title']}, "
                                     f"url=https://youtube.com/watch?v={video['id']}")
            # only major difference from play = add to front of queue
            self.audio_queue.insert(0, (video, source))

            if not vc.is_playing():
                utils.play_next(vc, context, self)
                # TODO: fix audio buffering - use asyncio.sleep() and tasks
        else:
            await context.send('User is not in a voice channel')

    @commands.command(name='queue',
                      description='View the audio queue in order of most-soon-to-be-played.',
                      brief='View the audio queue',
                      aliases=['q'],
                      pass_context=True)
    async def queue(self, context: discord.ext.commands.Context):
        vc: discord.VoiceClient = context.voice_client
        if vc is not None:
            # Send embed if necessary, otherwise default chat message
            if vc.is_playing():
                return await context.send(embed=utils.make_embed(0, self, context))
        await context.send('No audio in queue')

    @commands.command(name='np',
                      description='See what audio is currently being played, if any.',
                      brief='See the current audio source',
                      aliases=['now_playing'],
                      pass_context=True
                      )
    async def now_playing(self, context: discord.ext.commands.Context):
        vc: discord.VoiceClient = context.voice_client
        if vc is not None:
            # Send embed if necessary, otherwise default chat message
            if vc.is_playing():
                return await context.send(embed=utils.make_embed(1, self, context))
        await context.send('Nothing playing')

    @commands.command(name='skip',
                      description='Skip the current audio being played and serves up the next one in line.'
                                  '\nWith more than two other users in voice, this command initiates a vote to skip.',
                      brief='Skip this trash',
                      aliases=[],
                      pass_context=True)
    async def skip(self, context: discord.ext.commands.Context):
        vc: discord.VoiceClient = context.voice_client
        if vc is None:
            return await context.send('Not in voice channel')
        if not vc.is_connected() or not vc.is_playing():
            return await context.send('Nothing to skip')

        threshold = 3  # threshold - 1-2 people can vote to skip individually, 3+ is a vote
        vote_timer = 15  # voting period in seconds

        if len(vc.channel.members) < threshold:
            e = utils.make_embed(5, self, context)
            # remove "Vote succeeded" title since we didn't vote
            e.title = ""
            # get next audio source if available
            next_audio = utils.skip_to_next(vc, self)
            if next_audio:
                e.add_field(name='Now playing:', value=next_audio)
            return await context.send(embed=e)
        # credit: https://stackoverflow.com/questions/69288961/how-to-make-queue-for-songs-and-skip-command-discord-py
        vote = utils.make_embed(2, self, context)  # create temporary message for vote
        vote_msg = await context.send(embed=vote)
        vote_id = vote_msg.id

        await vote_msg.add_reaction(u"\u2705")
        await vote_msg.add_reaction(u"\U0001F6AB")

        await asyncio.sleep(vote_timer)  # allow voting for vote_timer seconds

        # retrieve vote message and extract results
        vote_msg: discord.Message = await context.channel.fetch_message(vote_id)
        vote_reacts = [u"\u2705", u"\U0001F6AB"]  # emojis used to vote
        votes = {vote_reacts[0]: 0, vote_reacts[1]: 0}  # vote tally for each emoji
        reacted = []  # list of users who voted - only count them once!
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
        logger.log(logging.INFO, f'skip: >>>Vote {vote_id} results: {votes}')
        embed_update = discord.Embed()

        # check voting results
        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 \
                    or votes[u"\u2705"] / (votes[u"\u2705"] + votes[u"\U0001F6AB"]) > 0.5:
                can_skip = True
                embed_update = utils.make_embed(5, self, context)

        # voting is done - display result embeds and skip if vote passed
        if can_skip:
            next_audio = utils.skip_to_next(vc, self)
            # empty = False: no audio after current
            if next_audio:
                embed_update.add_field(name='Now playing:', value=next_audio)
        else:
            embed_update = utils.make_embed(6, self, context)

        await vote_msg.clear_reactions()
        await vote_msg.edit(embed=embed_update)

    @commands.command(name='clear',
                      description='Clears the entire audio queue except for the bot\'s current audio source, if any.',
                      brief='Clear the audio queue',
                      aliases=['clear_queue'],
                      pass_context=True
                      )
    async def clear(self, context):
        msg = 'Nothing to clear'
        if len(self.audio_queue) > 0:
            self.audio_queue.clear()
            msg = 'Cleared audio queue'
        await context.send(msg)

    @commands.command(name='join',
                      description='Moves the bot into the user\'s current voice channel.'
                                  '\nIf already in the same channel, this does nothing.',
                      brief='Make the bot join your voice channel',
                      aliases=['move'],
                      pass_context=True
                      )
    async def join(self, context):
        user = context.author
        if user.voice is not None:
            await utils.join_voice_channel(context, user.voice)
        else:
            await context.send('User is not in a voice channel')

    @commands.command(name='disconnect',
                      description='Makes the bot disconnect from any voice channel they\'re in.',
                      brief='Kick the bot outta voice',
                      aliases=['d'],
                      pass_context=True
                      )
    async def disconnect(self, context: discord.ext.commands.Context):
        msg = 'Not in voice channel'
        if context.voice_client is not None:
            # get bot voice channel to show name on disconnect
            curr_channel: discord.VoiceChannel = context.voice_client.channel
            # clear audio queue and disconnect - bot is no longer playing/storing audio
            if context.voice_client.is_playing():
                self.audio_queue.clear()
            msg = f'Disconnected from {utils.emph("#" + curr_channel.name)}'
            await context.voice_client.disconnect()
        await context.send(msg)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Shamelessly ripped from https://stackoverflow.com/questions/63658589/how-to-make-a-discord-bot-leave-the
        -voice-channel-after-being-inactive-for-x-min """
        timeout = 600

        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == timeout:
                    logger.log(logging.INFO, f"== Idle in voice for {timeout} seconds, disconnecting..")
                    await voice.disconnect()
                if not voice.is_connected():
                    break
