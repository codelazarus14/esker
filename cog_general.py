import random

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
        """Esker says hi!"""
        responses = [
            'Greetings, hatchling!',
            'Hi there!',
            'Hello!',
            'Nice lunar weather we\'re having...',
            'Welcome to the Lunar Outpost! I don\'t get visitors very often...'
        ]
        await context.send(utils.chat_styler(random.choice(responses)))

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
        await context.send("sorry pal i gotta develop a dialogue system first")

    @commands.command(name='mallow',
                      description='Toast a marshmallow to your liking, or even burn it to a crisp.',
                      brief='Toast a marshmallow',
                      aliases=['marshmallow'],
                      pass_context=True
                      )
    async def mallow(self, context):
        """TODO: marshmallow minigame w pixel art or maybe just numbers for now"""
        await context.send(utils.chat_styler("NO MALLOWS FOR YOU!"))

    @commands.command(name='tunes',
                      description='Wanna listen to some tunes?',
                      brief='Do you hear music?',
                      aliases=['music', 'tune'],
                      pass_context=True
                      )
    async def tunes(self, context):
        """TODO: Reply with a random OST link if in text chat

        | in voice, put YouTube playlist of OST on shuffle"""
        await context.send(
            utils.chat_styler("Looks like the tape player is broken... again. Maybe I can ask Hornfels about it "
                              "the next time they check up on me. They oughta be able to get Slate's engineering "
                              "genius on board."))

    @commands.command(name='rock_assn',
                      description='Discover your true Hearthian name!',
                      brief='Assigned rock at slash command',
                      aliases=['rock', 'rock_assignment', 'ra'],
                      pass_context=True
                      )
    async def rock_assn(self, context):
        # list of rocks from https://en.wikipedia.org/wiki/List_of_rock_types
        rocks = ["Arkose", "Basalt", "Breccia", "Gypsum", "Caliche", "Coquina", "Flint", "Ijolite"
                                                                                         "Mariposite", "Skarn",
                 "Pyrite", "Schist", "Scoria", "Shale", "Tufa"]
        # generate rock name from user id
        rock_index = abs(hash(context.author.id)) % len(rocks)
        await context.send(utils.chat_styler("I reckon you'd make a fine " + rocks[rock_index] + ", hatchling!"))
