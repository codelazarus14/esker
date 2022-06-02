import asyncio
import os
import random

import discord
from discord.ext import commands

import utils

TIME_LOOP = 1 * 60
"""Number of seconds in the time loop"""
# TODO: fix monospaced chars not actually being.. monospaced
#   mostly the fault of the 3 largest supernova ones..
SYMBOL_BLANK = " "
SYMBOL_STARS = ["٭", "⭒", "⭑"]
SYMBOL_SUPERNOVA = ["✶", "✦", "✹", "✧"]
SYMBOL_END = ['■']
RESPONSE_THRESHOLDS = [0.1, 0.05]


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.curr_audio = 'Nothing playing'
        self.star_chart = {"is_looping": False, "counter": 9318054,
                           "stars": ["Nobody here but us chickens"], "visible": []}
        """dict of current visible stars in the sky that updates over the course of a loop\n
        "counter" = loop #, "stars" = char list - mutable, "visible" = list of visible star indices"""
        self.gaze_responses = {
            "early": ['Take a look!',
                      'A sight for four eyes...\n'
                      'By the look you\'re giving me, I\'d guess you\'re not a big fan of puns.',
                      'Chert\'s the one with all the juicy details about these things.'
                      ' I just think they\'re nice to look at.'],
            "mid": ['Is it just me, or do the stars look different today?',
                    'Lotta supernovae today. I might just be getting older but it feels like time '
                    'is moving a little too fast.',
                    'No shortage of interesting things going on. Chert must be getting quite a kick out of '
                    'all this on Ember Twin.'],
            "late": ['It\'s getting awfully quiet out there, don\'t you think?',
                     'Only a few of them left now, I wonder what comes next..',
                     'Seems like we\'re coming to the end of the line now. I could use some time off.'],
            'end': ['Oh well. Bit of an awkward way to go, but at least you\'re still here with me.']
        }
        """List of Esker's responses corresponding to current loop progress"""

    @commands.command(name='mallow',
                      description='Toast a marshmallow to your liking, or even burn it to a crisp.',
                      brief='Toast a marshmallow',
                      aliases=['marshmallow'],
                      pass_context=True
                      )
    async def mallow(self, context):
        """TODO: marshmallow minigame w pixel art or maybe just numbers for now"""
        await context.send(embed=utils.make_embed(2, self, context))

    @commands.command(name='tunes',
                      description='*Wanna listen to some tunes?*\n\nIf user is not in voice, Esker will reply with '
                                  'a link to an OST track on YouTube.\n\nIn voice, Esker will join and give you a '
                                  'random track. If you have second thoughts, use `e.tunes stop` and '
                                  'Esker will turn off the player',
                      brief='Do you hear music?',
                      aliases=['music', 'tune'],
                      pass_context=True
                      )
    async def tunes(self, context: discord.ext.commands.Context, *, arg: str = None):
        # allows users to force disconnect whenever they want
        if arg is not None:
            if arg.lower() in ['stop', 'disconnect', 'd']:
                if context.voice_client is not None and context.voice_client.is_playing():
                    await context.voice_client.disconnect()
                    await context.send(embed=discord.Embed(color=discord.Color.orange())
                                       .add_field(name="Okay I hear ya!", value="_ _"))
                    return
            else:
                await context.send(embed=discord.Embed(colour=discord.Color.orange())
                                   .add_field(name="Sorry, didn't catch that one? Did you mean `e.tunes stop`?",
                                              value="_ _"))
                return
        elif context.author.voice is not None:
            # grab file locally - no downloading bc I bought the soundtrack
            fp = 'ost/Outer Wilds - Original Soundtrack/OST/'
            files = os.listdir(os.getcwd() + "/" + fp)
            # 1-28 OST tracks to choose from
            rand_track = random.randint(1, 28)
            to_play: str = ""
            for f in files:
                title = f.split(' - ')
                # match track # in filename
                if title[0] == f'{rand_track:02d}':
                    to_play = fp + f
                    self.curr_audio = f

            # voice client handling code from rythm experience
            # TODO: fix stuttering/audio quality issues like on rythm
            source: discord.AudioSource = discord.FFmpegPCMAudio(to_play)
            if context.voice_client is None:
                await context.author.voice.channel.connect()
            else:
                await context.voice_client.move_to(context.author.voice.channel)
            vc: discord.VoiceClient = context.voice_client

            if vc.is_playing():
                vc.stop()
            vc.play(source)

            await context.send(embed=utils.make_embed(3, self, context))
        else:
            # if not in voice (text response)
            # list of YouTube video ids in order (1-28)
            ost_ids = ['SPa8bPqQfmo', 'Xpkc-NU1KA0', 'RmouAm4pXLE', 'W9p-yVwF71o', 'lSo4f1hBI0w', 'bcEoHjGdbbY',
                       'vfCxLVQaSis', 'HkslC6TrCIM', 'b8cggVGj--I', 't5vG4Be1Ci8', 'zB5lEhUxwDU', '7Y3xbA4gsis',
                       '0ddvyyyCCD4', 'yHNf6vQ0HFs', '7Kem5iuzW54', 'KQrcRTA6_5M', '6zlSUvWU6z8', 'VtQ2gOoIUiU',
                       'MdWU7Qsc0kY', 'z34enKCqRGk', 'tlmUSX5Jsmc', 'XOrygf_iLhw', 'VcmPOvy4hHA', 'DxG574HUn3c',
                       '5MIYydxcJkU', '9N-5fCFEcs0', 'u_SEqF9bygQ', 'Ht4HxSpUN60']
            await context.send(f'https://youtube.com/watch?v={random.choice(ost_ids)}')

    @commands.command(name='stars',
                      description='Look up at the night sky and welcome the end together.',
                      brief='Stargazing with Esker',
                      aliases=['stargaze'],
                      pass_context=True
                      )
    async def stars(self, context, *, admin_override=None):
        # allow admin to force reset - skips to next loop
        if admin_override in ['start', 'reset'] and context.author.guild_permissions.administrator:
            # TODO: make this not break the supernova ending
            self.star_chart['is_looping'] = False

        if not self.star_chart['is_looping']:
            # on first call, initiate time loop
            self.star_chart['is_looping'] = True
            self.star_chart['counter'] += 1
            print(f"Beginning loop {self.star_chart['counter']:,}: generating star chart data")
            star_freq = 15
            length = 720
            add_space = False
            star_str = [SYMBOL_BLANK] * length
            star_indices = []
            # randomly fill star string with stars each loop - not compatible lore-wise, but I like
            # having a diff sky each time? maybe we're just looking at a different patch of it
            for i in range(length):  # 12 lines * 60 (monospaced char line length) = landscape orientation
                if i % 60 == 0:
                    star_str[i] = "\n"
                    add_space = False
                elif random.randint(1, 100) <= star_freq and not add_space:  # use star_freq to determine frequency
                    if random.randint(1, 500) <= 1:  # roll another die to see if we get mogus
                        star_str[i] = 'ඞ'
                    else:
                        star_str[i] = random.choice(SYMBOL_STARS)
                        star_indices.append(i)
                    add_space = True  # force padding between stars on next iteration
                    i -= 1
                else:
                    add_space = False
            # shuffle indices for random ordering
            random.shuffle(star_indices)
            self.star_chart['stars'] = star_str
            self.star_chart['visible'] = star_indices
            print(f"Starting indices: {self.star_chart['visible']}")

            # time begins to pass...
            death_interval = TIME_LOOP / len(self.star_chart['visible'])  # loop length/num of stars
            asyncio.create_task(self.universe_death(int(death_interval)))

        embed = utils.make_embed(5, self, context)
        rtype = self.response_type()
        embed.add_field(name=random.choice(self.gaze_responses[rtype]), value="_ _", inline=False)

        # keep updating message embed - convenience feature for testing, might not keep in final
        # instead, could replace with a method that makes esker reply about their concern
        # and prompt someone to call e.stars again
        msg: discord.Message = await context.send(embed=embed)
        msg_id = msg.id
        asyncio.create_task(self.update_msg(context, msg_id))

    async def universe_death(self, death_interval):
        while len(self.star_chart['visible']) > 0:
            print(len(self.star_chart['visible']))
            print(len(self.star_chart['visible']) / len(self.star_chart['stars']))

            rand_interval = random.randint(death_interval - 3, death_interval + 3)
            await asyncio.sleep(rand_interval)  # time to wait between supernovae
            supernova_index = self.star_chart['visible'].pop()
            asyncio.create_task(self.star_death(supernova_index, death_interval))
        # no more stars left
        self.star_chart['is_looping'] = False

    async def star_death(self, index, duration):
        self.star_chart['stars'][index] = SYMBOL_SUPERNOVA[0]  # other options ✦
        print(f"Uh oh.. {index}")
        await asyncio.sleep(duration / 2)
        self.star_chart['stars'][index] = SYMBOL_SUPERNOVA[1]
        print(f"..Here it comes.. {index}")
        await asyncio.sleep(duration / 3)
        self.star_chart['stars'][index] = SYMBOL_SUPERNOVA[2]
        print(f"Star at index {index} just went supernova!")
        await asyncio.sleep(duration / 2)
        self.star_chart['stars'][index] = SYMBOL_SUPERNOVA[3]
        print(f"Star at index {index} is cooling down..")
        await asyncio.sleep(duration)
        self.star_chart['stars'][index] = SYMBOL_BLANK
        print(f"Star at index {index} has faded away..")

    async def update_msg(self, context, msg_id):
        """Async function to keep bot updating previous e.stars embeds"""
        while self.star_chart['is_looping']:
            # update interval - 1320 / (1320/4=330) = 4 seconds
            await asyncio.sleep(TIME_LOOP / (TIME_LOOP / 4))
            # could throw an exception if message was deleted
            try:
                msg: discord.Message = await context.channel.fetch_message(msg_id)
                if msg.embeds[0].footer.text == f'{self.star_chart["counter"]:,}':
                    # want to keep response same for the embed, only update when necessary
                    prev_response: str = msg.embeds[0].fields[1].name
                    # if Esker's response is from a previous mood/stage of universe death, update
                    if prev_response not in self.gaze_responses[self.response_type()]:
                        prev_response = random.choice(self.gaze_responses[self.response_type()])
                        print(f"new response: {prev_response}")

                    emb = utils.make_embed(5, self, context)
                    emb.add_field(name=prev_response, value="_ _", inline=False)
                    await msg.edit(embed=emb)
            except discord.NotFound:
                print(f"No message found matching {msg_id}")
                return
        # we're at the end - trigger the loop finale
        await self.the_end(context, msg_id)

    def response_type(self):
        # determine Esker's response by progress through loop
        if len(self.star_chart['visible']) / len(self.star_chart['stars']) > RESPONSE_THRESHOLDS[0]:
            rtype = 'early'
        elif len(self.star_chart['visible']) / len(self.star_chart['stars']) > RESPONSE_THRESHOLDS[1]:
            rtype = 'mid'
        else:
            rtype = 'late'
        return rtype

    async def the_end(self, context, msg_id):
        try:
            msg: discord.Message = await context.channel.fetch_message(msg_id)
        except discord.NotFound:
            print(f"No message found matching {msg_id} to end the universe")
            return
        # Esker's final words
        emb = utils.make_embed(5, self, context)
        resp = random.choice(self.gaze_responses['end'])
        print(f"last words: {resp}")
        emb.add_field(name=resp, value="_ _", inline=False)
        await msg.edit(embed=emb)
        await asyncio.sleep(3)
        # slowly (asyncio.sleep) replace all the strings with exploding supernova
        total_stars = range(len(self.star_chart['stars']))
        for i in reversed(total_stars):
            if i % 60 != 0:
                # looks like a smooth curve if you squint at it
                if 28 < i % 60 < 32:
                    self.star_chart['stars'][i] = SYMBOL_END[0]
                elif 16 < i % 60 < 44 and i + 60 < len(total_stars):
                    self.star_chart['stars'][i+60] = SYMBOL_END[0]
                elif 8 < i % 60 < 52 and i + 120 < len(total_stars):
                    self.star_chart['stars'][i+120] = SYMBOL_END[0]
                elif 2 < i % 60 < 58 and i + 180 < len(total_stars):
                    self.star_chart['stars'][i+180] = SYMBOL_END[0]
                elif i + 240 < len(total_stars):
                    self.star_chart['stars'][i+240] = SYMBOL_END[0]
            else:
                # after finishing a line, update embed to show progression vertically
                emb = utils.make_embed(5, self, context)
                emb.add_field(name=resp, value="_ _", inline=False)
                await msg.edit(embed=emb)
                await asyncio.sleep(3)
        # after sun reaches top of embed text, fill in the remaining
        for i in reversed(range(len(self.star_chart['stars']) // 3)):
            if i % 60 != 0:
                if 16 < i % 60 < 44 and i - 180 >= 0:
                    self.star_chart['stars'][i-180] = SYMBOL_END[0]
                elif 8 < i % 60 < 52 and i - 120 >= 0:
                    self.star_chart['stars'][i-120] = SYMBOL_END[0]
                elif 2 < i % 60 < 58 and i - 60 >= 0:
                    self.star_chart['stars'][i-60] = SYMBOL_END[0]
                else:
                    self.star_chart['stars'][i] = SYMBOL_END[0]
            else:
                emb = utils.make_embed(5, self, context)
                emb.add_field(name=resp, value="_ _", inline=False)
                await msg.edit(embed=emb)
                await asyncio.sleep(3)

        # clear esker's last message
        emb = utils.make_embed(5, self, context)
        emb.set_footer(text='_ _', icon_url="_ _")
        await msg.edit(embed=utils.make_embed(5, self, context))
        print(f"Loop {self.star_chart['counter']:,} has ended")
