import discord
import os

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)

running_interactions = dict()

tokens = dict()


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))
