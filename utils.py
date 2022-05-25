import math
import time

import requests

import json

import discord
import discord.ext.commands
from youtube_dl import YoutubeDL


class BadEmbedTypeError(ValueError):
    """Error when given bad embed format"""


ffmpeg_opts: dict[str, str] = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}  # required to keep bot connected against YouTube's wishes


async def join_voice_channel(context: discord.ext.commands.Context, user_voice):
    # get user VoiceChannel
    channel: discord.VoiceChannel = user_voice.channel
    # TODO: doesn't account for old bot instance left in voice - unreliable unless we force it
    #  to disconnect from everything when being shut down - override client.run()
    voice_client = context.voice_client
    if voice_client is not None:
        # if client already exists
        if voice_client.is_connected() and voice_client.channel is not channel:
            await context.send(f'Moving to channel {emph("#" + channel.name)}')
    else:
        # create new voice client and connect to current channel
        voice_client = await channel.connect()
        await context.send(f'Connecting to channel {emph("#" + channel.name)}')
    await voice_client.move_to(channel)
    return voice_client


def play_next(vc: discord.VoiceClient, context, music_cog):
    if len(music_cog.audio_queue) == 0:
        print('Reached end of audio queue')
        return
    else:
        music_cog.curr_audio = music_cog.audio_queue.pop(0)
        music_cog.curr_audio += (time.time(),)
        # curr_audio[2] = play() starting timestamp
        vc.play(discord.FFmpegPCMAudio(music_cog.curr_audio[1], **ffmpeg_opts),
                after=lambda e: play_next(vc, context, music_cog))


def skip_to_next(vc: discord.VoiceClient, music_cog):
    # use pause = stopping the player = close it
    vc.pause()
    msg = ''
    # still another audio source in the queue? swap it in
    if len(music_cog.audio_queue) > 0:
        music_cog.curr_audio = music_cog.audio_queue.pop(0)
        music_cog.curr_audio += (time.time(),)
        vc.source = discord.FFmpegPCMAudio(music_cog.curr_audio[1], **ffmpeg_opts)
        vc.resume()
        msg = f"{music_cog.curr_audio[0]['title']}"
    else:
        vc.stop()
    return msg


def search_yt(query):
    """get video from links or YouTube search

    | credit to https://stackoverflow.com/questions/63647546/how-would-i-stream-audio-from-pytube-to-ffmpeg-and
    -discord-py-without-downloadin """
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try:
            # use query as link
            requests.get(query)
        except:
            # use query as search phrase
            info = ydl.extract_info(f'ytsearch:{query}', download=False)['entries'][0]
        else:
            info = ydl.extract_info(query, download=False)
    return info, info['formats'][0]['url']


def emph(msg: str):
    return f'`{msg}`'


def audio_progress(start: float, duration: float) -> str:
    """Creates a visual representation of progress through an audio source"""
    symbols = ["⚪", "=", "-"]
    progress = time.time() - start  # subtract current time from when bot started playing
    percentage = progress / duration
    timeline_size = 40
    msg = "**`|"
    print(f"progress: {progress}s, duration:{duration} percent: {percentage * 100}")
    for i in range(timeline_size):
        scaled_percentage = timeline_size * percentage
        if i < scaled_percentage:
            if i == math.floor(scaled_percentage):
                msg += symbols[0]
            else:
                msg += symbols[1]
        else:
            msg += symbols[2]
    msg += f"|`**\n`"
    prog_msg = ""
    dur_msg = " / "
    if duration / 3600 >= 1:  # support for 1+ hr sources
        prog_msg += f"{int(progress // 3600):02d}:"
        dur_msg += f"{int(duration // 3600):02d}:"
    prog_msg += f"{int((progress // 60) % 60):02d}:{int(progress % 60):02d}"
    dur_msg += f"{int((duration // 60) % 60):02d}:{int(duration % 60):02d}`"
    return msg + prog_msg + dur_msg


def make_embed(embed_type: int, music_cog, context: discord.ext.commands.Context) -> discord.Embed:
    """Creates an embed for putting in chat given a format indicator
    that should match the context from which make_embed() is called

    | See type_to_file in this method but really this is just my own utility method"""
    curr_audio = music_cog.curr_audio
    aq = music_cog.audio_queue
    type_to_file = {
        0: 'queue-embed',
        1: 'queue-embed',
        2: 'vote-embed',
        3: 'searching-embed',
        4: 'query-success-embed',
        5: 'skip-success-embed',
        6: 'skip-fail-embed'
    }
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
                # queue = show current track and queue
                embed.add_field(name="**Currently playing: **", value=curr_audio[0]['title'], inline=False)
                embed.add_field(name="Progress", value=audio_progress(curr_audio[2], curr_audio[0]['duration']),
                                inline=False)

                if len(aq) > 0:
                    queue_str = ''
                    for i in range(len(aq)):
                        queue_str += f"`{i + 1}.` {(aq[i][0]['title'])}\n"
                    embed.add_field(name="**Queue: **", value=queue_str)
            case 1:
                # np = just show current track
                embed.add_field(name="**Currently playing: **", value=curr_audio[0]['title'], inline=False)
                embed.add_field(name="Progress", value=audio_progress(curr_audio[2], curr_audio[0]['duration']),
                                inline=False)
            case 2 | 3 | 4:
                # Vote, searching, query success should indicate author
                embed.set_author(name=context.author.name, icon_url=context.author.avatar_url)
        return embed
