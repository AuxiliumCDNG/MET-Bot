import importlib
import threading

import requests
from discord_interactions import verify_key_decorator
from flask import Blueprint, abort, send_file, request, jsonify

from globals import tokens, running_interactions, client, db
from statics import config

views = Blueprint("misc", __name__)

@views.route("/pictures/<guild_id>/<dl_token>/")
def pictures(guild_id, dl_token):
    try:
        if tokens[int(guild_id)]["pictures"] != dl_token:
            abort(401)
    except KeyError:
        abort(401)
    return send_file(f"web/picture_downloads/{guild_id}.zip")


@views.route("/interaction/", methods=["POST"])
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

    t = threading.Thread(name=name, target=module.run, args=[req], kwargs={"client": client, "options": option_level, "res_url": res_url, "db": db})
    t.start()

    if req["guild_id"] not in running_interactions.keys():
        running_interactions[req["guild_id"]] = {}
    running_interactions[req["guild_id"]][location] = {"token": req["token"]}

    return jsonify(
        {
            "type": 5
        }
    )
