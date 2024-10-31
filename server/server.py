from quart import Quart

from blueprints.twitch_forwarder import twitch_forwarder

app = Quart(__name__)
app.register_blueprint(twitch_forwarder)

@app.route("/")
def hello():
    return f"hello world!"
