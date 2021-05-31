import asyncio
import datetime
import shutil
import time
import os
import secrets
import zipfile

import discord.errors
import requests
import validators

from globals import zipdir, tokens
from interactions.create import headers
from statics import config

def run(req, client=None, options=None, mysql=None, res_url=None):
    begin = [option["value"] for option in options if option["name"] == "von"][0]
    end = [option["value"] for option in options if option["name"] == "bis"][0]

    if not validators.url(begin):
        json = {
            "content": f"Der Link beim Argument **von** ist nicht korrekt!",
            "embeds": [],
            "allowed_mentions": []
        }
        requests.patch(res_url, json=json, headers=headers)
        return
    if not validators.url(end):
        json = {
            "content": f"Der Link beim Argument **bis** ist nicht korrekt!",
            "embeds": [],
            "allowed_mentions": []
        }
        requests.patch(res_url, json=json, headers=headers)
        return

    begin = [int(element) for element in begin.split("channels/")[1].split("/")]
    end = [int(element) for element in end.split("channels/")[1].split("/")]

    print(begin)
    print(end)

    guild = asyncio.run_coroutine_threadsafe(client.fetch_guild(int(req["guild_id"])), client.loop).result()

    if begin[0] != guild.id or end[0] != guild.id:
        json = {
            "content": f"Diese Nachrichten befinden sich nicht auf diesem Server!",
            "embeds": [],
            "allowed_mentions": []
        }
        requests.patch(res_url, json=json, headers=headers)
        return
    if begin[1] != end[1]:
        json = {
            "content": f"Die Nachrichten befinden sich nicht im gleichen Kanal!",
            "embeds": [],
            "allowed_mentions": []
        }
        requests.patch(res_url, json=json, headers=headers)
        return

    channel = client.get_channel(begin[1])
    try:
        message1 = asyncio.run_coroutine_threadsafe(channel.fetch_message(begin[2]), client.loop).result()
        message2 = asyncio.run_coroutine_threadsafe(channel.fetch_message(end[2]), client.loop).result()
    except discord.errors.NotFound:
        json = {
            "content": f"Die Nachrichten konnten nicht gefunden werden!",
            "embeds": [],
            "allowed_mentions": []
        }
        requests.patch(res_url, json=json, headers=headers)
        return

    asyncio.set_event_loop(client.loop)

    history = channel.history(limit=None, before=message2, after=message1)
    messages = asyncio.run_coroutine_threadsafe(history.flatten(), client.loop).result()
    messages.append(message1)
    messages.append(message2)

    if os.path.exists(f"web/picture_downloads/{guild.id}/"):
        shutil.rmtree(f"web/picture_downloads/{guild.id}/")

    os.makedirs(f"web/picture_downloads/{guild.id}/")

    for message in messages:
        if not message.attachments:
            continue
        if "image" in message.attachments[0].content_type:
            asyncio.run_coroutine_threadsafe(message.attachments[0].save(f"web/picture_downloads/{guild.id}/{message.attachments[0].filename}"), client.loop).result()

    zipf = zipfile.ZipFile(f"web/picture_downloads/{guild.id}.zip", 'w', zipfile.ZIP_DEFLATED)
    zipdir(f"web/picture_downloads/{guild.id}/", zipf)
    zipf.close()

    if guild.id not in tokens.keys():
        tokens[guild.id] = {}
    tokens[guild.id]["pictures"] = secrets.token_urlsafe(20)

    link = f"{config.address}/pictures/{guild.id}/{tokens[guild.id]['pictures']}"
    json = {
            "content": f"Der Download steht bereit!\n{link}\nDer Link ist solange gültig, bis der nächste Bild-Download gestartet wird.",
            "embeds": [],
            "allowed_mentions": []
            }

    r = requests.patch(res_url, json=json, headers=headers)
    return
