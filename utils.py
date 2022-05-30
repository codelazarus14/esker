import random

import discord.ext

import json


class BadEmbedTypeError(ValueError):
    """Error on bad embed/format type given to make_embed()"""


def say_hi():
    """Esker says hi!"""
    responses = [
        'Greetings, hatchling!',
        'Hi there!',
        'Hello!',
        'Nice lunar weather we\'re having...',
        'Welcome to the Lunar Outpost! I don\'t get visitors very often...'
    ]
    return random.choice(responses)


def say_dialogue():
    """Returns a random piece of Esker's Official Dialogue"""
    # TODO: replace with Esker's dialogue from Outer Wilds
    responses = [
        'I can\'t even remember my lines..'
    ]
    return random.choice(responses)


def choose_rock(user_hash):
    # list of rocks from https://en.wikipedia.org/wiki/List_of_rock_types
    rocks = ["Arkose", "Basalt", "Breccia", "Gypsum", "Caliche", "Coquina", "Flint", "Ijolite"
                                                                                     "Mariposite", "Skarn",
             "Pyrite", "Schist", "Scoria", "Shale", "Tufa"]
    return rocks[user_hash % len(rocks)]


def stargazing(star_chart):
    return f"```{''.join(star_chart['stars'])}```"


def make_embed(embed_type: int, cog: discord.ext.commands.Cog, context: discord.ext.commands.Context) -> discord.Embed:
    """Creates an embed for putting in chat given a format indicator
    that should match the context from which make_embed() is called

    | See type_to_file in this method but really this is just my own utility method"""

    # shorthand for writing out multiple command types pointing to same json
    type_to_file = dict.fromkeys([0, 1, 2, 3, 4, 5], 'default-embed')
    type_to_file.update(dict.fromkeys([6, 7, 8], 'help-embed'))

    if embed_type not in type_to_file:
        raise BadEmbedTypeError
    # find corresponding json file with dict
    with open(f'json/{type_to_file[embed_type]}.json', 'r') as embed_json:
        embed_dict = json.load(embed_json)
        # convert dict to embed
        embed = discord.Embed.from_dict(embed_dict)
        # update each template with data from context
        match embed_type:
            case 0:
                embed.add_field(name="_ _", value=f"**{say_hi()}**")
            case 1:
                embed.add_field(name="_ _", value=f"**{say_dialogue()}**")
            case 2:
                embed.add_field(name="_ _", value=f"**NO MALLOWS FOR YOU!**")
            case 3:
                if context.author.voice is None:
                    embed.add_field(name="Here you go!", value="_ _", inline=False)
                else:
                    embed.add_field(name="Found one! The labels on these cassettes have peeled off"
                                         " but it's all great stuff anyway.", value="_ _")
            case 4:
                # generate rock name from user id
                user_hash = abs(hash(context.author.id))
                embed.add_field(name="_ _",
                                value=f"**I reckon you'd make a fine {choose_rock(user_hash)}, hatchling!**")
            case 5:
                embed.add_field(name="_ _", value=stargazing(cog.star_chart), inline=False)
                # best nomai mask high contrast image i could find on google
                embed.set_footer(text=f"{cog.star_chart['counter']:,}",
                                 icon_url='https://ih1.redbubble.net/image.881198846.0086/flat,750x1000,075,f.jpg')
            case 6:
                # bot help: extract commands from each cog
                for cog_name in context.bot.cogs:
                    command_str = ""
                    cmds = context.bot.get_cog(cog_name).get_commands()
                    if len(cmds) > 0:
                        for i in range(len(cmds) - 1):
                            command_str += f"*{cmds[i]}*, "
                        command_str += f"*{cmds[len(cmds) - 1]}*"
                    embed.add_field(name=cog_name + ":", value=command_str, inline=False)
            case 7:
                # category help: extract commands from cog
                cmd_names = ""
                cmd_briefs = ""
                cmds: list[discord.ext.commands.Command] = cog.get_commands()
                if len(cmds) > 0:
                    for i in range(len(cmds) - 1):
                        cmd_names += f"*{cmds[i]}*\n"
                        cmd_briefs += f"{cmds[i].brief}\n"
                    cmd_names += f"*{cmds[len(cmds) - 1]}*"
                    # help's description is blank after overwrite
                    if cmds[len(cmds) - 1].qualified_name == 'help':
                        cmd_briefs += 'Shows this message'
                    else:
                        cmd_briefs += f"{cmds[len(cmds) - 1].brief}\n"
                # name is already displayed above, just show commands
                embed.add_field(name="Commands:", value=cmd_names)
                # separate column (inline field) for briefs
                embed.add_field(name="_ _", value=cmd_briefs)
        return embed
