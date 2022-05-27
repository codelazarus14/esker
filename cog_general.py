from discord.ext import commands

import utils


class General(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.star_chart = {"loop": 0, "stars": "Nobody here but us chickens"}
        """dict of current visible stars in the sky that updates over the course of a loop"""
        # TODO: implement help command like before
        # self._original_help_command = bot.help_command
        # bot.help_command = MyHelpCommand()
        # bot.help_command.cog = self

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
        """TODO: use self.star_chart to maintain a dictionary of the current loop,
            a string representing the visible stars and a list of visible star indices from that string

        | On the first call to stars or after using a debug parameter (e.stars reset/loop_start), the string is randomly
          generated again to have N number of stars in it randomly scattered throughout, or using a % chance, or using
          a list of star patterns/clusters? last one sounds too advanced idk.

        | While generating this string, whenever the string is about to have a new star added its index is saved to
          the list of visible star indices. We then shuffle this list once after finishing the string and now have a
          random ordering of visible stars in the sky.

        | Over the course of 22 mins, at even intervals (dependent on # of stars total) we slowly pop the front of that
          index list and replace the corresponding char in the stars string with a blank space, so that they blink out
          one by one (if we implement supernovas - want to first replace w a * or something and then remove it). By 1-2
          mins left there should barely be any stars visible and once all the stars have vanished we have a countdown
          to the ATP activating/chat spam from Esker with custom visuals as the supernova detonates and then everything
          resets.

        | The first call to e.stars will activate the time loop, then subsequent calls without params just show the
          current state of the visible sky captioned with a comment from Esker. As the loop progresses, at major
          intervals they start to change their tone a bit (50%, 75%, 90%) as they take notice of the dying universe.

        | Additions: debug commands like above, using fields to store the timing of events for testing, random stars
        replaced with ඞ which are not recorded/popped from list (mogus witnesses the death of the universe)"""
        await context.send(embed=utils.make_embed(5, self, context))
