import os

import discord as discord_bot
import mysql.connector
import mysql.connector.cursor
import pymysql
from dbutils.pooled_db import PooledDB
from flask import Flask
from flask_discord import DiscordOAuth2Session

from statics import config

app = Flask("MET_Bot", static_folder='web/public/', static_url_path='', template_folder='web/templates/')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = config.Discord.client_id
app.config["DISCORD_CLIENT_SECRET"] = config.Discord.client_secret
app.config["DISCORD_REDIRECT_URI"] = f"{config.address}/callback/"
app.config["DISCORD_BOT_TOKEN"] = config.Discord.bot_token

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

discord = DiscordOAuth2Session(app)

db = pymysql.connect(
    host=config.DB.host,
    user=config.DB.user,
    password=config.DB.password,
    db=config.DB.db,
    cursorclass=pymysql.cursors.DictCursor
)

connection_pool = PooledDB(mysql.connector, 5,
                           host=config.DB.host,
                           port=config.DB.port,
                           user=config.DB.user,
                           password=config.DB.password,
                           db=config.DB.db,
                           buffered=True
                           )

connection_pool.connection().cursor().execute("SET NAMES UTF8")

intents = discord_bot.Intents.default()
intents.reactions = True
intents.members = True
intents.guilds = True
client = discord_bot.Client(intents=intents, member_cache_flags=discord_bot.MemberCacheFlags().from_intents(intents))

running_interactions = dict()

tokens = dict()

login_redirects = {}

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))
