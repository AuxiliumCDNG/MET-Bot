import flask
from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_discord import Unauthorized

from globals import discord, login_redirects, app

views = Blueprint("account", __name__)

@views.route("/login/")
def login():
    if discord.authorized:
        return redirect(url_for("index"))
    if "loginUnderstand" in request.args:
        if request.cookies.get('cookie_consent') != "true":
            flash("Zuerst musst du Cookies akzeptieren, da der Login sonst fehlschlägt!")
            return redirect(url_for("account.login"))
        return discord.create_session(scope=["identify", "guilds"])
    else:
        return render_template("login_splash.html", user=None)
@views.route("/logout/")
def logout():
    discord.revoke()
    flash("Du wurdest ausgelogt!")
    return redirect(url_for("index", _external=True, _scheme='https'))
@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    login_redirects[request.remote_user] = request.url
    return redirect(url_for("account.login", _external=True, _scheme='https'))

@views.route("/callback/")
def callback():
    if request.cookies.get('cookie_consent') != "true":
        return redirect(url_for("account.login"))
    flash("Wir haben dich angemeldet!")
    discord.callback()
    if request.remote_user in login_redirects.keys():
        target = login_redirects[request.remote_user]
        del login_redirects[request.remote_user]
        flash("Du wurdest auf die angeforderte Seite weitergeleitet...")
        return redirect(target)
    return redirect(url_for("index", _external=True, _scheme='https'))

@views.route("/clearCookies/")
def clear_cookies():
    if discord.authorized:
        discord.revoke()

    res = flask.make_response(redirect(url_for("index")))
    for cookie in request.cookies.keys():
        print("deleting", cookie)
        res.set_cookie(cookie, "", expires=0, path="/")

    flash("Alle Cookies wurden gelöscht. Bevor wieder welche gespeichert werden, musst du dies erneut akzeptieren. Ggf. wurdest du ausgeloggt.", category="hold")

    return res

