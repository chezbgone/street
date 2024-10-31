import asyncio
import logging

import discord
from discord.ext import commands

from cogs.twitch_forwarder import TwitchForwarder
from config import SECRETS

LOG = logging.getLogger(__name__)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='><>', intents=intents)

@bot.event
async def on_ready():
    LOG.info(f'Logged in as {bot.user}')
    await bot.add_cog(TwitchForwarder(bot))

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

async def main():
    await bot.start(SECRETS['DISCORD_TOKEN'])

if __name__ == '__main__':
    asyncio.run(main())
