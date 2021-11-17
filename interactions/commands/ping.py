import time

import requests

from interactions.create import headers


def run(req, res_url=None, **kwargs):
    time.sleep(3)

    json = {
            "content": "Meine CPU bedankt sich...und, achja:\nPong :ping_pong:",
            "embeds": [],
            "allowed_mentions": []
            }

    r = requests.patch(res_url, json=json, headers=headers)
    return
