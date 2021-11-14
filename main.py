import _thread
import asyncio
import mimetypes
import os
import time

from flask import render_template, request
from flask_talisman import Talisman

import routes
import statics.secrets as secrets
from bot import client
from globals import app, db, discord
from init import init
from statics import config

if not os.path.exists("web/update_pictures"):
    os.mkdir("web/update_pictures")

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('image/*', '.jpg')


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = secrets.flask_secret_key

# app.debug = True

Talisman(app, content_security_policy=None)

@app.route("/")
def index(*args):
    if discord.authorized:
        user = discord.fetch_user()
    else:
        user = None
    return render_template("index.html", bot=client, user=user)

@app.context_processor
def inject_template_scope():
    injections = dict()

    def cookies_check():
        value = request.cookies.get('cookie_consent')
        return value == 'true'
    injections.update(cookies_check=cookies_check)

    return injections


app.register_blueprint(routes.konvoi.views)
app.register_blueprint(routes.account.views)
app.register_blueprint(routes.misc.views)

if __name__ == "__main__":
    print("Datenbank wird initialisiert...")
    init(db)

    print("Der Bot startet...")

    token = secrets.DISCORD_BOT_TOKEN

    loop = asyncio.get_event_loop()
    loop.create_task(client.start(token))

    _thread.start_new_thread(loop.run_forever, tuple(), {})

    while not client.is_ready():
        time.sleep(1)

    print("Der Webserver wird gestartet...")

    app.run(host=config.bind, port=config.web_port, ssl_context='adhoc')
