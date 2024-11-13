import logging
from datetime import datetime, timedelta

from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context, Cog

from common.config import CONFIG
from common.database import currency_db, stream_chat_db
from common.util import pluralize

ACCRUAL_COOLDOWN = timedelta(minutes=15)
ACCRUAL_CURRENCY_AMOUNT = 10

LOG = logging.getLogger(__name__)

def _try_accrue_currency(user_id: int) -> bool:
    """
    Awards `ACCRUAL_CURRENCY_AMOUNT` currency to user with id `user_id` if
    enough time (`ACCRUAL_COOLDOWN`) has passed since their most recent accrual.
    
    Returns whether accrual was successful.
    """
    def _accrue_at_time(new_timestamp: datetime):
        currency_db.add_to_user(user_id, ACCRUAL_CURRENCY_AMOUNT)
        stream_chat_db.set_last_stream_message_time(user_id, new_timestamp)
        return True

    last_accrued = stream_chat_db.get_last_stream_message_time(user_id)
    now = datetime.now()
    if last_accrued is None:
        return _accrue_at_time(now)

    if now - last_accrued < ACCRUAL_COOLDOWN:
        return False

    # currency accrued very recently.u
    #    last_accrued    +1 cooldown      +2 cooldown
    #        |----------------|----------------|
    #                                now
    if now - last_accrued < 2 * ACCRUAL_COOLDOWN:
        return _accrue_at_time(last_accrued + ACCRUAL_COOLDOWN)
    
    return _accrue_at_time(now)

class ChatPoints(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id != CONFIG['discord_stream_chat']:
            return
        if message.author.bot:
            # this also ignores the twitch forwarding webhook
            return
        _try_accrue_currency(message.author.id)

    @commands.command()
    async def get_points(self, ctx: Context):
        points = currency_db.get_user_points(ctx.author.id)
        await ctx.send(f'you have {points} point{pluralize(points)}')
