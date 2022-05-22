import discord


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


def make_embed() -> discord.Embed:
    """used to style text for fancy chat output given a properly-formatted
    dict of content - possibly created by helper?"""
    test_dict = {
        'author': {
            'name': 'bot-name',
            'icon_url': 'https://penis.com'
        },
        'fields': [{
            'name': 'Title',
            'value': 'Body here'
        }]
    }

    e = discord.Embed.from_dict(test_dict)
    # match msg_type:
    #     case 1:
    #         for x in fields_test:
    #             e.add_field(x['title'], x['body'])
    #     case _:
    #         print("Invalid embed type given")
    #         raise EmbedTypeError
    return e

    # return "**\n" + text + "**\n"
