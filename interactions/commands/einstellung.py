import requests

from helpers import change_setting, get_setting
from interactions.create import headers


def run(req, options=None, res_url=None, **kwargs):
    setting = [option["value"] for option in options if option["name"] == "einstellung"][0]
    value = [option for option in options if option["name"] == "wert"][0]

    change = True

    print(value)

    # Prechecks for "fahrer_rolle"
    if setting == "fahrer-rolle":
        if not value["value"].startswith("<@&"):  # if value is not a role
            change = False
            json = {
                "content": "Bei der Einstellung **fahrer_rolle** wird eine Rolle erwartet.",
                "embeds": [],
                "allowed_mentions": []
            }

    # Prechecks for "event_rolle"
    if setting == "event-rolle":
        if not value["value"].startswith("<@&"):  # if value is not a role
            change = False
            json = {
                "content": "Bei der Einstellung **event_rolle** wird eine Rolle erwartet.",
                "embeds": [],
                "allowed_mentions": []
            }

    # only change the setting if prechecks allow
    if change:
        change_setting(setting, value["value"])
        json = {
            "content": "Der Wert der Einstellung **%s** ist nun **%s**." % (setting, get_setting(setting)),
            "embeds": [],
            "allowed_mentions": []
        }

    r = requests.patch(res_url, json=json, headers=headers)
    return
