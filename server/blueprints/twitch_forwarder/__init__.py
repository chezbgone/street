from threading import Thread

from quart import Blueprint, current_app
import redis.asyncio

from common.models import TwitchMessage
from .twitch_listener import TwitchChatListener
from config import CONFIG

twitch_forwarder = Blueprint('twitch_forwarder', __name__)

channel = CONFIG['twitch_channel']

@twitch_forwarder.before_app_serving
def before():
    LOG = current_app.logger
    r = redis.Redis(host='cache', port=6379)
    def chat_received(message: TwitchMessage):
        LOG.info(f'{message.display_name}: {message.content}')
        r.publish('twitch-chat', message.encode())
    def spawn_twitch_forwarder():
        TwitchChatListener(channel).listen(on_message=chat_received)
    Thread(target=spawn_twitch_forwarder).start()
    LOG.info(f'listening to twitch messages on {channel=}')
