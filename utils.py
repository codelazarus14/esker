import json

import discord
import discord.ext.commands


class BadEmbedTypeError(ValueError):
    """Error when given bad embed format"""


async def join_voice_channel(client, context, user_voice):
    # get user VoiceChannel
    channel: discord.VoiceChannel = user_voice.channel
    # TODO: doesn't account for old bot instance left in voice - unreliable unless we force it
    #  to disconnect from everything when being shut down - override client.run()
    if len(client.voice_clients) > 0:
        # if client already exists
        voice_client = client.voice_clients[0]
        if voice_client.is_connected() and voice_client.channel is not channel:
            await context.send(f'Moving to channel `#{channel.name}`')
    else:
        # create new voice client and connect to current channel
        voice_client = await channel.connect()
        await context.send(f'Connecting to channel `#{channel.name}`')
    await voice_client.move_to(channel)
    return voice_client


def play_next(vc: discord.VoiceClient, context, audio_queue):
    if len(audio_queue) == 0:
        print('Reached end of audio queue')
        return
    else:
        curr_audio: discord.AudioSource = audio_queue[0]
        vc.play(curr_audio, after=lambda e: play_next(vc, context, audio_queue))
        print(f'Now playing {curr_audio}')
        del audio_queue[0]


def skip_to_next(vc: discord.VoiceClient, audio_queue):
    vc.pause()
    msg = ''
    # still another audio source in the queue? swap it in
    if len(audio_queue) > 0:
        vc.source = audio_queue.pop(0)
        vc.resume()
        msg = f'\nNow playing {vc.source}'
    else:
        vc.stop()
    return msg


def chat_styler(msg=str):
    # TODO: create generic chat-styler for non-embed messages
    return f'`{msg}`'


def make_embed(embed_type: int, aq: list[discord.AudioSource], bot: discord.ext.commands.Bot) -> discord.Embed:
    """Creates an embed for putting in chat given a format type
    that should match context from which make_embed() is called
    """
    type_to_file = {
        0: 'queue-embed'
    }
    if embed_type not in type_to_file:
        raise BadEmbedTypeError
    # find corresponding json file with dict
    with open(f'json/{type_to_file[embed_type]}.json', 'r') as embed_json:
        embed_dict = json.load(embed_json)
        # convert dict to embed
        embed = discord.Embed.from_dict(embed_dict)
        # update template with data based on conditions
        match embed_type:
            case 0:
                vc = bot.voice_clients[0]
                embed.add_field(name="**Currently playing: **", value=vc.source, inline=False)

                if len(aq) > 0:
                    queue_str = ''
                    for i in range(len(aq)):
                        queue_str += f'`{i+1}.` {aq[i]}\n'
                    embed.add_field(name="**Queue: **", value=queue_str)
        return embed
