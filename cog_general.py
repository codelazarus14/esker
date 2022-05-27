from discord.ext import commands

import utils


class General(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
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
