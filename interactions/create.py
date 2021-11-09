import time

import requests

from statics import config
from statics import secrets

# url = f"https://discord.com/api/v8/applications/{config.DISCORD_CLIENT_ID}/commands"
url = f"https://discord.com/api/v8/applications/{config.DISCORD_CLIENT_ID}/guilds/844218034666209280/commands"

commands = [
    {
        "name": "ping",
        "description": "Ein bisschen Server Last erzeugen.",
    },
    {
        "name": "bilder_herunterladen",
        "description": "Automatisch Bilder herunterladen!",
        "options": [
            {
                "name": "von",
                "description": "Ab wo Bilder gesucht werden sollen. (Ein Nachrichtenlink)",
                "type": 3,
                "required": True
            },
            {
                "name": "bis",
                "description": "Bis wo Bilder gesucht werden sollen. (Ein Nachrichtenlink)",
                "type": 3,
                "required": True
            }
        ]
    },
    {
        "name": "spediziel",
        "description": "Speditionsziel abrufen und anzeigen."
    },
    {
        "name": "einstellung",
        "description": "Einstellungen ändern",
        "options": [
            {
                "name": "einstellung",
                "description": "Was geändert werden soll",
                "type": 3,
                "required": True
            },
            {
                "name": "wert",
                "description": "Neuer Wert der Einstellung",
                "type": 3,
                "required": True
            }
        ]
    }
]

# For authorization, you can use either your bot token
headers = {
    "Authorization": f"Bot {secrets.DISCORD_BOT_TOKEN}",
    "Content-Type": "application/json"
}

if __name__ == "__main__":
    """
    r = requests.get(url, headers=headers)
    
    for command in r.json():
        time.sleep(3)
        r = requests.delete(url + "/" + command["id"], headers=headers)
        print("deleted command " + command["name"])
        print(r)
        print()
    #"""

    for json in commands:
        time.sleep(1)
        r = requests.post(url, headers=headers, json=json)
        print("created command " + json["name"])
        print(r, r.json())

    exit()

    r = requests.get(f"https://discord.com/api/v8/applications/{config.DISCORD_CLIENT_ID}/commands", headers=headers)
    print(r)
    print(r.json())
