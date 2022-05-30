import asyncio
import os
import random

import discord
from discord.ext import commands

import utils

TIME_LOOP = 3 * 60
"""Number of seconds in the time loop"""
# TODO: fix monospaced chars not actually being.. monospaced
#   mostly the fault of the 3 largest supernova ones..
SYMBOL_BLANK = " "
SYMBOL_STARS = ["٭", "⭒", "⭑"]
SYMBOL_SUPERNOVA = ["✶", "✦", "✹", "✧"]  # other options: ✦
RESPONSE_THRESHOLDS = [0.1, 0.05]


class MyHelpCommand(commands.DefaultHelpCommand):
    """Overriding default help message as an embed"""
    def __init__(self, **options):
        super().__init__(**options)
        # on override, the help command's attrs are reset
        self.command_attrs['description'] = 'Shows this message'

    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        help_emb = utils.make_embed(6, self.cog, self.context)
        help_emb.description = f"\n\nType `{self.clean_prefix}help command` for more info on a command.\n You " \
                               f"can also type `{self.clean_prefix}help category` for more info on a category."
        await destination.send(embed=help_emb)

    async def send_cog_help(self, cog):
        destination = self.get_destination()
        help_emb = utils.make_embed(7, cog, self.context)
        help_emb.set_author(name=f"Showing help for category: {cog.qualified_name}",
                            icon_url=self.context.bot.user.avatar_url)
        help_emb.description = f"\n\nType `{self.clean_prefix}help command` for more info on a command."
        await destination.send(embed=help_emb)

    async def send_command_help(self, command):
        destination = self.get_destination()
        help_emb = utils.make_embed(8, self.cog, self.context)
        help_emb.set_author(name=f"Showing help for command: {command.name}",
                            icon_url=self.context.bot.user.avatar_url)
        desc = command.description
        help_emb.description = f"`{self.get_command_signature(command)}`\n\n{desc}"
        await destination.send(embed=help_emb)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.star_chart = {"is_looping": False, "counter": 0, "stars": ["Nobody here but us chickens"], "visible": []}
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
                     'Seems like we\'re coming to the end of the line now. I could use some time off.']
        }
        """List of Esker's responses corresponding to current loop progress"""
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    @commands.command(name='hello',
                      description='Say hi to an old friend.',
                      brief='Say hello',
                      aliases=['hi', 'greetings'],
                      pass_context=True
                      )
    async def hello(self, context):
        await context.send(embed=utils.make_embed(0, self, context))

    @commands.command(name='dialogue',
                      description='Relive your favorite bits of Mobius Digital Esker Dialogue™.',
                      brief='Chat with Esker',
                      aliases=['dialog'],
                      pass_context=True
                      )
    async def dialogue(self, context):
        """ TODO: figure out how to recreate dialogue system
             this is honestly such an entangled mess to work through - maybe replace with
             lucabot-style random line regurgitation """
        # dtree = DialogueTree(dialogue.NODES, 'start')
        # await dtree.evaluate(dtree.nodes[0])
        await context.send(embed=utils.make_embed(1, self, context))

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
                      description='Wanna listen to some tunes? If not, use `e.tunes stop`'
                                  ' and I\'ll turn off the player',
                      brief='Do you hear music?',
                      aliases=['music', 'tune'],
                      pass_context=True
                      )
    async def tunes(self, context: discord.ext.commands.Context, *, stop: str = None):
        # allows users to force disconnect whenever they want
        if stop is not None:
            if stop.lower() in ['stop', 'disconnect', 'd']:
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

            # voice client handling code from rythm experience
            source: discord.AudioSource = discord.FFmpegPCMAudio(to_play)
            if context.voice_client is None:
                await context.author.voice.channel.connect()
            else:
                await context.voice_client.move_to(context.author.voice.channel)
            vc: discord.VoiceClient = context.voice_client

            if not vc.is_playing():
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

    @commands.command(name='rock_assn',
                      description='Discover your true Hearthian name!',
                      brief='Assigned rock at slash command',
                      aliases=['rock', 'rock_assignment', 'ra'],
                      pass_context=True
                      )
    async def rock_assn(self, context):
        await context.send(embed=utils.make_embed(4, self, context))

    @commands.command(name='stars',
                      description='Look up at the night sky with Esker and welcome the end of the universe.',
                      brief='Stargazing with Esker',
                      aliases=['stargaze'],
                      pass_context=True
                      )
    async def stars(self, context, *, args=None):
        """TODO: By 1-2 mins left there should barely be any stars visible and once all the stars have vanished we
        have a countdown to the ATP activating/chat spam from Esker with custom visuals as the supernova detonates
        and then everything resets.

        | Additions: debug commands like above, random stars replaced with ඞ which are not recorded/popped from list
            (mogus witnesses the death of the universe)"""

        # allow admin to force reset the loop
        if args in ['start', 'reset'] and context.author.guild_permissions.administrator:
            self.star_chart['is_looping'] = False

        if not self.star_chart['is_looping']:
            # on first call, initiate time loop
            self.star_chart['is_looping'] = True
            self.star_chart['counter'] += 1
            print(f"Beginning loop {self.star_chart['counter']}: generating star chart data")
            star_freq = 15
            length = 720
            add_space = False
            star_str = [SYMBOL_BLANK] * length
            star_indices = []
            # randomly fill star string with stars each loop - not compatible lore-wise, but I like
            # having a new arrangement each time, maybe we're just looking at a different patch of sky
            # TODO: improve random star clustering so it doesn't look as streaky
            for i in range(length):  # 12 lines * 60 (monospaced char line length) = landscape orientation
                if i % 60 == 0:
                    star_str[i] = "\n"
                    add_space = False
                elif random.randint(1, 100) <= star_freq and not add_space:  # use star_freq to determine frequency
                    star_str[i] = random.choice(SYMBOL_STARS)
                    star_indices.append(i)
                    add_space = True  # force padding between stars on next iteration
                    i -= 1
                else:
                    # TODO: small chance to add ඞ
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

            rand_interval = random.randint(death_interval - 5, death_interval + 5)
            await asyncio.sleep(rand_interval)  # time to wait between supernovae
            supernova_index = self.star_chart['visible'].pop()
            asyncio.create_task(self.star_death(supernova_index, death_interval))
        print("No more stars left")

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
        while len(self.star_chart['visible']) > 0:
            # update interval - 3 seconds seems about enough
            await asyncio.sleep(3)
            # could throw an exception if message was deleted
            try:
                msg: discord.Message = await context.channel.fetch_message(msg_id)
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
                return

    def response_type(self):
        # determine Esker's response by progress through loop
        if len(self.star_chart['visible']) / len(self.star_chart['stars']) > RESPONSE_THRESHOLDS[0]:
            rtype = 'early'
        elif len(self.star_chart['visible']) / len(self.star_chart['stars']) > RESPONSE_THRESHOLDS[1]:
            rtype = 'mid'
        else:
            rtype = 'late'
        return rtype
