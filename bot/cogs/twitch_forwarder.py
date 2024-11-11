from typing import Any, Literal, TypeAlias, TypedDict, Union
import logging

from discord.abc import Messageable
from discord.ext import commands
import redis.asyncio as redis
from common.models import TwitchMessage

from common.config import CONFIG

LOG = logging.getLogger(__name__)

STREAM_CHANNEL = CONFIG['discord_stream_chat']

RedisMessageType: TypeAlias = Union[
    Literal['subscribe'],
    Literal['unsubscribe'],
    Literal['psubscribe'],
    Literal['punsubscribe'],
    Literal['message'],
    Literal['pmessage'],
]

class RedisMessage(TypedDict):
    type: RedisMessageType
    pattern: str | None
    channel: bytes
    data: Any

def message_forwarder(channel: Messageable):
    async def f(redis_message: RedisMessage):
        twitch_message_bytes: bytes = redis_message['data']
        message = TwitchMessage.decode(twitch_message_bytes.decode())
        await channel.send(f'{message.display_name}: {message.content}')
    return f

class TwitchForwarder(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        channel = self.bot.get_partial_messageable(STREAM_CHANNEL)
        r = redis.Redis(host='cache', port=6379)
        pubsub = r.pubsub()
        await pubsub.subscribe(**{'twitch-chat': message_forwarder(channel)})
        await pubsub.run()

