import random
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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
