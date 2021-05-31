import _thread
import asyncio
import importlib
import time
import threading

import requests
from discord_interactions import verify_key_decorator
from flask import Flask, request, jsonify, abort, send_from_directory, current_app, send_file

import statics.secrets as secrets
from bot import client
from globals import running_interactions, tokens
from statics import config

app = Flask("FlaskHACS", static_folder='web/public', static_url_path='', template_folder='web/templates')
app.secret_key = secrets.flask_secret_key


@app.route("/interaction/", methods=["POST"])
@verify_key_decorator(config.DISCORD_PUBLIC_KEY)
def interaction():
    req = request.json
    if req["type"] == 1:
        return {"type": 1}

    if "options" not in req["data"].keys():
        req["data"]["options"] = []

    location = [req["data"]["name"]]
    option_level = req["data"]["options"]

    if len(option_level) > 0:
        while "options" in option_level[0].keys():
            location.append(option_level[0]["name"])
            option_level = option_level[0]["options"]
    location = "interactions.commands." + ".".join(location)

    try:
        module = importlib.import_module(location)  # "slash-commands."+req["data"]["name"])
    except ModuleNotFoundError:
        return jsonify({"type": 4,
                        "data": {
                            "tts": False,
                            "content": "Huch! Das sollte nicht passieren, aber das Feature gibts irgendwie nicht...",
                            "embeds": [],
                            "allowed_mentions": []
                        }
                        })

    # res = module.run(req, client=client, options=option_level)

    name = req["guild_id"] + f"_{location}"

    if name in [thread.name for thread in threading.enumerate()]:
        r = requests.get(f"https://discord.com/api/v8/webhooks/{config.DISCORD_CLIENT_ID}/{running_interactions[req['guild_id']][location]['token']}/messages/@original")
        message_id = r.json()["id"]
        m_url = f"https://discord.com/channels/{req['guild_id']}/{req['channel_id']}/{message_id}"
        return jsonify({"type": 4,
                        "data": {
                            "tts": False,
                            "content": "Eine solche Interaktion läuft bereits! Bitte warte, bis diese abgeschlossen ist.\nZu finden unter: " + m_url,
                            "embeds": [],
                            "allowed_mentions": []
                        }
                        })

    res_url = f"https://discord.com/api/v8/webhooks/{config.DISCORD_CLIENT_ID}/{req['token']}/messages/@original"

    t = threading.Thread(name=name, target=module.run, args=[req], kwargs={"client": client, "options": option_level, "res_url": res_url})
    t.start()

    if req["guild_id"] not in running_interactions.keys():
        running_interactions[req["guild_id"]] = {}
    running_interactions[req["guild_id"]][location] = {"token": req["token"]}

    return jsonify(
        {
            "type": 5
        }
    )

@app.route("/pictures/<guild_id>/<dl_token>/")
def pictures(guild_id, dl_token):
    try:
        if tokens[int(guild_id)]["pictures"] != dl_token:
            abort(401)
    except KeyError:
        abort(401)
    return send_file(f"web/picture_downloads/{guild_id}.zip")


print("Der Bot startet...")

token = secrets.DISCORD_BOT_TOKEN

loop = asyncio.get_event_loop()
loop.create_task(client.start(token))

_thread.start_new_thread(loop.run_forever, tuple(), {})

# _thread.start_new_thread(client.run, token, {})

while not client.is_ready():
    time.sleep(1)

print("Der Webserver wird gestartet...")

if __name__ == "__main__":
    app.run(host=config.bind, port=config.web_port)
