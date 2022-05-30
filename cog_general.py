from discord.ext import commands

import utils


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

    @commands.command()
    async def define(self, context):
        await context.send(embed=utils.make_embed(9, self, context))

    @commands.command(name='rock_assn',
                      description='Discover your true Hearthian name!',
                      brief='Assigned rock at slash command',
                      aliases=['rock', 'rock_assignment', 'ra'],
                      pass_context=True
                      )
    async def rock_assn(self, context):
        await context.send(embed=utils.make_embed(4, self, context))
