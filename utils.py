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
    responses = {
        "greetings": [
            "Oh, hey, it’s you! Ground control didn’t tell me you were launching. Long time no see!\n"
            "Actually, I guess it’s been a long time since I’ve seen anyone.",
            "Hi again. Can’t get enough of the moon? ...I’m kidding.",
            "Don’t go! Uh, I mean, anything else you wanted to ask?", ],
        "travelers": ["The Lunar Outpost saw more traffic back when our ships were less sophisticated "
                      "and needed more frequent repairs. Nowadays, it’s mostly used to keep a set of eyes on things."
                      "\nSometimes Chert comes by to say hi, but Gabbro is Gabbro, and you know how Riebeck feels "
                      "about “unnecessary spaceflight."],
        "whistling": ["Probably. Or actually, definitely. The other travelers carry instruments, "
                      "so they don’t bother whistling.\nYou can pick up their music with a signalscope, you know. "
                      "Best spot for that is the north pole. Great reception."
                      "\nThe north pole is marked in red on your mini map, but the Attlerock is a pretty small moon,"
                      " really. Just go north. You can’t miss it."],
        "lonely": ["A little. I’m in touch with ground control — Hornfels and Gossan, mostly "
                   "— and they radio up to chat now and then."],
        "what": ["Ha ha, very funny. ...Oh, stars above, you’re serious, aren’t you? That’s just depressing."
                 "\nSigh… Welcome to the Lunar Outpost, which apparently the space program doesn’t bother to "
                 "teach anyone anymore."
                 "\nWhen we first started Outer Wilds, travelers used to bring their ships here all the time for "
                 "repairs. Our spacefaring technology has improved loads since then, but the older ships tended to,"
                 " uh, fall apart a lot. Like, more than they do now."
                 "\nUsing the outpost cut down on the number of launches and landings taking place in the village"
                 " and also the number of fires. Nowadays, though, it’s mostly just me up here raising saplings"
                 " from Timber Hearth and keeping an eye on things."],
        "marl": ["Heh, Marl is probably the only one who remembers I’m up here. I should go see the big lug soon."
                 "\nDon’t tell them about this, but sometimes I throw my Little Scout down to make sure Marl isn’t "
                 "doing anything stupid. I worry that big tree in the village wouldn’t stand a chance otherwise."]
    }
    return random.choice(responses['greetings'])


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
                cog: cog_fun.Fun
                args = context.message.content.split()
                # asking for leaderboard
                # effective way to pull args out of message
                if len(args) > 1:
                    if args[1].lower() in ['leaderboard', 'l']:
                        embed.title = "Mallow Game Leaderboard"
                        if len(cog.mallow_leaderboard) > 0:
                            lead_str = ""
                            lead_str2 = ""
                            for user in cog.mallow_leaderboard:
                                lead_str += f"`{user}`\n"
                                lead_str2 += f"`{cog.mallow_leaderboard.get(user)}`\n"
                            embed.add_field(name="User:", value=lead_str)
                            embed.add_field(name="Score:", value=lead_str2)
                        else:
                            embed.add_field(name="_ _", value="No entries yet! Toast some mallows first.")
                    else:
                        embed.add_field(name=f"Were you looking for the scores, hatchling?"
                                             f"\nTry `{args[0]} leaderboard`", value="_ _")
                # otherwise
                else:
                    rnum = random.randint(1, 5)
                    # mapping of randint to score: {1,5} = 1 point, {2,4} = 2 points, {3} = 3 points
                    res_dict = {1: 1, 2: 2, 3: 3, 4: 2, 5: 1}
                    res = res_dict[rnum]

                    # response: underdone
                    if rnum < 3:
                        embed.add_field(name="Could've left it in a bit longer... oh well.",
                                        value=f"Underdone: +{res} points")
                    # perfect toast
                    elif rnum == 3:
                        embed.add_field(name="Great job hatchling! Smooth brown outside, nice goopy inside. "
                                             "\nJust the way I like 'em.",
                                        value=f"Perfectly toasted: +{res} points")
                    # overdone
                    elif rnum < 5:
                        embed.add_field(name="Hmm. A little crisp for my liking but good enough.",
                                        value=f"Overdone: +{res} points")
                    # incinerated
                    elif rnum == 5:
                        embed.add_field(name="Oh dear. I think that's more than enough, \nyou can pull it "
                                             "out of the fire now.\nEating that lump of coal is bad for you, y'know.",
                                        value=f"Incinerated: +{res} points")

                    # add new mallow points to leaderboard
                    if context.author in cog.mallow_leaderboard.keys():
                        res += cog.mallow_leaderboard.get(context.author)

                    cog.mallow_leaderboard.update({context.author: res})
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
                embed.add_field(name=f"I reckon you'd make a fine {choose_rock(user_hash)}, hatchling!",
                                value="_ _")
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
                    resp = [f"\"*{q['query'][0]}*\", eh?",
                            f"\"*{q['query'][0]}*\", hmm. Gotta have something lying around here...",
                            f"I think I saw something on that while going through the archives the other day,"
                            f" hang on a sec..."]
                    # ['query'][0] is first item in tuple - raw text, [1] is the url encoding
                    embed.title = random.choice(resp)
                    if q['url']:
                        embed.description = f"Hope this is what you were looking for:"
                        embed.add_field(name=f"{q['title']}:", value=f"`{q['description']}`", inline=False)
                        embed.add_field(name=f"{q['url']}", value="_ _", inline=False)
                        embed.set_image(url=q['image'])
                        embed.set_footer(text=f"{q['name']} | {time.asctime()}", icon_url=f"{q['icon']}")
                    else:
                        # search query failed on the wiki
                        embed.description = f"Huh. I don't think I have any information on that right now.."
                else:
                    embed.add_field(name="Er, you gonna ask me what you wanted to know about?", value="_ _")
        return embed
