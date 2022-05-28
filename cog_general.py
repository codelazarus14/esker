import asyncio
import random

import discord
from discord.ext import commands

import utils

TIME_LOOP = 22 * 60
"""Number of seconds in the time loop"""
# TODO: fix monospaced chars not actually being.. monospaced
#   mostly the fault of the 3 largest supernova ones..
SYMBOL_BLANK = " "
SYMBOL_STARS = ["٭", "⭒", "⭑"]
SYMBOL_SUPERNOVA = ["✶", "✦", "✹", "✧"]  # other options: ✦


class MyHelpCommand(commands.DefaultHelpCommand):
    """Overriding default help message as an embed"""
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
        # TODO: fix help command description
        # help's description is blank after override
        if command.name == 'help':
            desc = 'Shows this message'
        else:
            desc = command.description
        help_emb.description = f"`{self.get_command_signature(command)}`\n\n{desc}"
        await destination.send(embed=help_emb)


class General(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.star_chart = {"is_looping": False, "counter": 0, "stars": ["Nobody here but us chickens"], "visible": []}
        """dict of current visible stars in the sky that updates over the course of a loop\n
        "counter" = loop #, "stars" = char list - mutable, "visible" = list of visible star indices"""
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
                      description='Wanna listen to some tunes?',
                      brief='Do you hear music?',
                      aliases=['music', 'tune'],
                      pass_context=True
                      )
    async def tunes(self, context):
        """TODO: Reply with a random OST link if in text chat

        | in voice, put YouTube playlist of OST on shuffle"""
        await context.send(embed=utils.make_embed(3, self, context))

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
    async def stars(self, context):
        """TODO:

        | On the first call to stars or after using a debug parameter (e.stars reset/loop_start), the string is randomly
          generated again to have N number of stars in it randomly scattered throughout, or using a % chance, or using
          a list of star patterns/clusters? last one sounds too advanced idk.

        | Over the course of 22 mins, at even intervals (dependent on # of stars total) we slowly pop the front of that
          index list and replace the corresponding char in the stars string with a blank space, so that they blink out
          one by one (if we implement supernovas - want to first replace w a * or something and then remove it). By 1-2
          mins left there should barely be any stars visible and once all the stars have vanished we have a countdown
          to the ATP activating/chat spam from Esker with custom visuals as the supernova detonates and then everything
          resets.

        | The first call to e.stars will activate the time loop, then subsequent calls without params just show the
          current state of the visible sky captioned with a comment from Esker. As the loop progresses, at major
          intervals they start to change their tone a bit (50%, 75%, 90%) as they take notice of the dying universe.

        | Additions: debug commands like above, random stars replaced with ඞ which are not recorded/popped from list
            (mogus witnesses the death of the universe)"""
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

        # keep updating message embed - convenience feature for testing, might not keep in final
        # instead, could replace with a method that makes esker reply about their concern
        # and prompt someone to call e.stars again
        msg: discord.Message = await context.send(embed=utils.make_embed(5, self, context))
        msg_id = msg.id
        asyncio.create_task(self.update_msg(context, msg_id))

    async def universe_death(self, death_interval):
        while len(self.star_chart['visible']) > 0:
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
            await asyncio.sleep(3)
            # could throw an exception if message was deleted
            try:
                msg: discord.Message = await context.channel.fetch_message(msg_id)
                await msg.edit(embed=utils.make_embed(5, self, context))
            except discord.NotFound:
                return
