import json
import random

import discord
from discord.ext import commands


class MyHelpCommand(commands.DefaultHelpCommand):
    """Overriding default help message as an embed"""
    async def send_bot_help(self, mapping):
        destination = self.get_destination()
        with open(f'json/help-embed.json', 'r') as embed_json:
            embed_dict = json.load(embed_json)
            # convert dict to embed
            help_emb = discord.Embed.from_dict(embed_dict)
            help_emb.set_author(name="Showing help", icon_url=self.context.bot.user.avatar_url)
            help_emb.description += f"\n\nType `{self.clean_prefix}help command` for more info on a command.\n You " \
                                    f"can also type `{self.clean_prefix}help category` for more info on a category."
            # extract commands from each cog
            for cog_name in self.context.bot.cogs:
                command_str = ""
                cmds = self.context.bot.get_cog(cog_name).get_commands()
                if len(cmds) > 0:
                    for i in range(len(cmds) - 1):
                        command_str += f"*{cmds[i]}*, "
                    command_str += f"*{cmds[len(cmds) - 1]}*"
                help_emb.add_field(name=cog_name + ":", value=command_str, inline=False)
            await destination.send(embed=help_emb)

    async def send_cog_help(self, cog):
        destination = self.get_destination()
        with open(f'json/help-embed.json', 'r') as embed_json:
            embed_dict = json.load(embed_json)
            # convert dict to embed
            help_emb = discord.Embed().from_dict(embed_dict)
            help_emb.set_author(name=f"Showing help for category: {cog.qualified_name}",
                                icon_url=self.context.bot.user.avatar_url)
            help_emb.description = f"\n\nType `{self.clean_prefix}help command` for more info on a command."
            # extract commands from cog
            cmd_names = ""
            cmd_briefs = ""
            cmds: list[discord.ext.commands.Command] = cog.get_commands()
            if len(cmds) > 0:
                for i in range(len(cmds) - 1):
                    cmd_names += f"*{cmds[i]}*\n"
                    cmd_briefs += f"{cmds[i].brief}\n"
                cmd_names += f"*{cmds[len(cmds) - 1]}*"
                cmd_briefs += f"{cmds[len(cmds) - 1].brief}"
            # name is already displayed above, just show commands
            help_emb.add_field(name="Commands:", value=cmd_names)
            # separate column (inline field) for briefs
            help_emb.add_field(name="_ _", value=cmd_briefs)
            await destination.send(embed=help_emb)

    async def send_command_help(self, command):
        destination = self.get_destination()
        with open(f'json/help-embed.json', 'r') as embed_json:
            embed_dict = json.load(embed_json)
            # convert dict to embed
            help_emb = discord.Embed().from_dict(embed_dict)
            help_emb.set_author(name=f"Showing help for command: {command.name}",
                                icon_url=self.context.bot.user.avatar_url)
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
        responses = [
            'Greetings, fellow traveler!',
            'Hi there!',
            'Hello!'
        ]
        await context.send(random.choice(responses))
