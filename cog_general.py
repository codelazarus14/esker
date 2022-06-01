import html
import re
import urllib.parse

import aiohttp
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
        self.query = None

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

    @commands.command(name='define',
                      description='Peruse the Outer Wilds Wiki from the comfort of your own Discord client.'
                                  '\n\n*In-universe:* Give Esker an article title or search query and they\'ll '
                                  'hunt around the Ventures archives to find what you\'re looking for.',
                      brief='Ask about the lore',
                      aliases=['def', 'wiki'],
                      pass_context=True)
    async def define(self, context, *, query=None):
        if query is not None:
            # convert their input to field and then generate embed
            search = 'https://outerwilds.fandom.com/wiki/Special:Search'
            # store their text input and params for url
            self.query = {'query': [query, [('query', urllib.parse.quote(query)),
                                            ('scope', 'internal'),
                                            ('navigationSearch', 1)]]}
            async with aiohttp.ClientSession() as session:
                async with session.get(search, params=self.query['query'][1]) as resp:
                    # made it to the page unharmed
                    if resp.status == 200:
                        body = await resp.text()
                        search_regex = '<h1 class="unified-search__result__header">\s*<a href="(.+?)"'
                        # get first matching string - first search result in layout
                        result_url = re.search(search_regex, body)
                        if result_url:
                            # proceed forth with search result
                            print(result_url.group(1))
                            async with session.get(result_url.group(1)) as resp2:
                                body2 = await resp2.text()
                                print(body2)
                                # TODO: maybe just use first paragraph instead of whole description?
                                extract_regex = ['<meta property="og:site_name" content="(.+?)"/>',
                                                 '<meta property="og:title" content="(.+?)"/>',
                                                 '<meta property="og:description" content="(.+?)"/>',
                                                 '<meta property="og:image" content="(.+?)"/>',
                                                 '<a accesskey="z" href="//outerwilds.fandom.com" '
                                                 'class="fandom-community-header__image">\s*<img\s*src="(.+?)"']
                                extracted = {'name': re.search(extract_regex[0], body2).group(1),
                                             'title': re.search(extract_regex[1], body2).group(1),
                                             'description': re.search(extract_regex[2], body2).group(1),
                                             'image': re.search(extract_regex[3], body2).group(1),
                                             'icon': re.search(extract_regex[4], body2).group(1),
                                             'url': result_url.group(1)}
                                # convert escape chars like apostrophes etc.
                                for k in extracted:
                                    val = extracted[k]
                                    extracted[k] = html.unescape(val)

                                print(extracted)
                                self.query.update(extracted)
                        else:
                            # make Esker display search failure on embed
                            self.query['url'] = None

        await context.send(embed=utils.make_embed(9, self, context))
        # delete data to avoid affecting future queries
        self.query = None

    @commands.command(name='rock_assn',
                      description='Discover your true Hearthian name!',
                      brief='Assigned rock at slash command',
                      aliases=['rock', 'rock_assignment', 'ra'],
                      pass_context=True
                      )
    async def rock_assn(self, context):
        await context.send(embed=utils.make_embed(4, self, context))
