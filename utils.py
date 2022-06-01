import random
import time

import discord.ext

import cog_fun
import cog_general
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
    type_to_file = dict.fromkeys([0, 1, 2, 3, 4, 5, 9], 'default-embed')
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
                embed.add_field(name=say_hi(), value="_ _")
            case 1:
                embed.add_field(name=say_dialogue(), value="_ _")
            case 2:
                embed.add_field(name="NO MALLOWS FOR YOU!", value=f"_ _")
            case 3:
                # extract track name from filename
                cog: cog_fun.Fun
                name: str = f'Track {cog.curr_audio.split(".mp3")[0]}'
                responses = [f"Let's see here... found one! \n\nThis one's labeled `{name}`",
                             f"It's a bit smudged, but I've never been able to read Slate's handwriting either way.\n\n"
                             f"I think this one says... `{name}`",
                             f"Get ready for `{name}`!"]
                embed.add_field(name=random.choice(responses), value="_ _")
            case 4:
                # generate rock name from user id
                user_hash = abs(hash(context.author.id))
                embed.add_field(name="_ _",
                                value=f"**I reckon you'd make a fine {choose_rock(user_hash)}, hatchling!**")
            case 5:
                cog: cog_fun.Fun
                embed.add_field(name="_ _", value=stargazing(cog.star_chart), inline=False)
                # best nomai mask high contrast image I could find on Google
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
            case 9:
                cog: cog_general.General
                q = cog.query
                if q is not None:
                    # ['query'][0] is first item in tuple - raw text, [1] is the url encoding
                    embed.title = f"\"*{q['query'][0]}*\", eh?"
                    if q['url']:
                        embed.description = f"After some digging around, I found this:"
                        embed.add_field(name=f"{q['title']}:", value=f"{q['description']}...", inline=False)
                        embed.add_field(name=f"{q['url']}", value="_ _", inline=False)
                        embed.set_image(url=q['image'])
                        embed.set_footer(text=f"{q['name']} | Accessed {time.asctime()}", icon_url=f"{q['icon']}")
                    else:
                        # search query failed on the wiki
                        embed.description = f"Huh. I don't think I have any information on that right now.."
                else:
                    embed.add_field(name="Er, you gonna ask me what you wanted to know about?", value="_ _")
        return embed
