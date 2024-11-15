from quart import Quart, request

from blueprints.twitch_forwarder import twitch_forwarder
from util.auth import require_token

app = Quart(__name__)
app.register_blueprint(twitch_forwarder)

@app.route("/")
async def hello():
    return f"hello world!"

@app.route("/private")
@require_token
async def hello2():
    app.logger.warning(request.authorization)
    return f"access granted"
