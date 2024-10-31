from threading import Thread

from discord import AllowedMentions, SyncWebhook
from quart import Blueprint, current_app

from common.models import TwitchMessage
from .twitch_listener import TwitchChatListener
from config import CONFIG

twitch_forwarder = Blueprint('twitch_forwarder', __name__)

@twitch_forwarder.before_app_serving
def before():
    LOG = current_app.logger

    webhook_url = CONFIG['discord_stream_chat_webhook_url']
    webhook = SyncWebhook.from_url(webhook_url)
    def chat_received(message: TwitchMessage):
        webhook.send(
            message.content,
            username=message.display_name,
            allowed_mentions=AllowedMentions.none(),
            suppress_embeds=True,
        )

    channel = CONFIG['twitch_channel']
    def spawn_twitch_forwarder():
        TwitchChatListener(channel).listen(on_message=chat_received)
    Thread(target=spawn_twitch_forwarder).start()

    LOG.info(f'listening to twitch messages on {channel=}')
