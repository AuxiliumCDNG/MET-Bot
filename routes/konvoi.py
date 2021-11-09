import datetime
import functools

from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_discord import requires_authorization

from globals import db, discord

views = Blueprint("konvoi", __name__, url_prefix="/konvoi/")

def konvoi_manager(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        return view(*args, **kwargs)
    return wrapper

@views.route("/")
@requires_authorization
def konvoi_list():
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM konvois")
        konvois = cursor.fetchall()
    if konvois == ():
        konvois = []

    konvois = sorted(konvois, key=lambda x: int(x["date"].toordinal()) if x["date"] is not None else 0)

    return render_template("konvois.html", user=discord.fetch_user(), konvois=konvois)

@views.route("/<konvoi_id>/")
@requires_authorization
def konvoi(konvoi_id):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
        print(konvoi_data)
    if konvoi_data is None:
        flash("Diesen Konvoi gibt es nicht in der Datenbank.")
        return redirect(url_for("konvoi.konvoi_list"))

    return_data = {
        "name": konvoi_data["name"],
        "Beschreibung": konvoi_data["description"],
        "Datum": konvoi_data["date"],
        "Treffen": konvoi_data["gather"],
        "Abfahrt": konvoi_data["time"],
        "Start": konvoi_data["start"],
        "Ziel": konvoi_data["finish"],
        "Pause": konvoi_data["pause"],
        "TruckersMP Eintrag": konvoi_data["truckersmp"],
        "TruckersMP Server": konvoi_data["server"]
    }

    return render_template("konvoi.html", user=discord.fetch_user(), konvoi=return_data)

@views.route("/create/")
@requires_authorization
@konvoi_manager
def create_konvoi():
    args = {}

    print(request.args)

    if "name" not in request.args.keys():
        return render_template("create_konvoi.html", user=discord.fetch_user())
    if request.args["name"] is None or request.args["name"] == "":
        flash("Der Konvoiname is obligatorisch!")
        return redirect(url_for("konvoi.create_konvoi"))

    for arg in request.args.keys():
        if request.args[arg] == "":
            args[arg] = "NULL"
        else:
            args[arg] = f"'{request.args[arg]}'"

    with db.cursor() as cursor:
        cursor.execute(f"INSERT INTO `konvois` (`name`, `description`, `truckersmp`, `date`, `gather`, `time`, `start`, `finish`, `pause`, `server`) " \
                       f"VALUES ({args['name']},{args['description']}, {args['tmp']}, {args['date']}, {args['gather']}, {args['time']}, {args['start']}, {args['finish']}, {args['pause']}, {args['server']})")

        r = f"/konvoi/{cursor.lastrowid}/"

        db.commit()

    return redirect(r)
