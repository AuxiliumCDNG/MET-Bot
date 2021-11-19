import asyncio
import datetime
from io import BytesIO

import flask
from flask import Blueprint, render_template, flash, url_for, redirect, request, abort, send_file
from flask_discord import requires_authorization

from globals import connection_pool, discord, client
from helpers import role_checker, roles_getter

views = Blueprint("konvoi", __name__, url_prefix="/konvoi/")


class KonvoiNotFoundError(Exception):
    pass

def is_archive(konvoi_id):
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
        cursor.close()
    if konvoi_data is None:
        raise KonvoiNotFoundError

    today = datetime.date.today().toordinal()
    try:
        archive = konvoi_data["date"].toordinal() < today
    except AttributeError:
        archive = False

    return archive, konvoi_data

@views.route("/")
@requires_authorization
@role_checker("fahrer-rolle")
def konvoi_list():
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM konvois")
        konvois = cursor.fetchall()
        cursor.close()
    if konvois == ():
        konvois = []

    konvois = sorted(konvois, key=lambda x: int(x["date"].toordinal()) if x["date"] is not None else 0)

    today = datetime.date.today().toordinal()

    konvois = [x for x in konvois if x["date"] is None or x["date"].toordinal() >= today]

    return render_template("konvois.html", user=discord.fetch_user(), title="Kommende Konvois", konvois=konvois)

@views.route("/archive/")
@requires_authorization
@role_checker("fahrer-rolle")
def konvoi_archive():
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM konvois")
        konvois = cursor.fetchall()
        cursor.close()
    if konvois == ():
        konvois = []

    konvois = sorted(konvois, key=lambda x: int(x["date"].toordinal()) if x["date"] is not None else 0)

    today = datetime.date.today().toordinal()
    konvois = [x for x in konvois if x["date"] is not None and x["date"].toordinal() < today]

    return render_template("konvois.html", user=discord.fetch_user(), title="Ältere Konvois", konvois=konvois)

@views.route("/<int:konvoi_id>/")
@views.route("/archive/<int:konvoi_id>/")
@requires_authorization
@role_checker("fahrer-rolle")
@roles_getter()
def konvoi(konvoi_id, getter=False, roles=None):
    try:
        archive, konvoi_data = is_archive(konvoi_id)
    except KonvoiNotFoundError:
        flash("Dieser Konvoi existiert nicht!")
        return redirect(url_for("konvoi.konvoi_list"))

    if archive and not request.path.__contains__("archive"):
        return redirect("/konvoi/archive/%s/" % konvoi_id)
    elif not archive and request.path.__contains__("archive"):
        return redirect("/konvoi/%s/" % konvoi_id)

    return_data = {
        "id": konvoi_data["id"],
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

    if getter:
        return konvoi_data

    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute(f"SELECT `id`, `konvoi_id`, `text` FROM `konvoi_updates` WHERE `konvoi_id`='{konvoi_id}' ORDER BY `id` DESC")
        updates = cursor.fetchall()

        cursor.execute(f"SELECT `id` FROM `konvoi_updates` WHERE `picture`<>'NULL'")
        pics = [x["id"] for x in cursor.fetchall()]

        cursor.execute(f"SELECT `user_id`, `status` FROM `presence` WHERE `user_id`='{discord.user_id}' AND `konvoi_id`='{konvoi_id}'")
        res = cursor.fetchone()
        user_presence = res["status"] if res is not None else "unselected"

        if "event-rolle" in roles:
            cursor.execute(f"SELECT `user_id`, `status` FROM `presence` WHERE`konvoi_id`='{konvoi_id}'")
            res = cursor.fetchall()

            konvoi_presence = dict()
            for pres in res:
                user = client.get_user(int(pres["user_id"]))
                if user is None:
                    user = asyncio.run_coroutine_threadsafe(client.fetch_user(int(pres["user_id"])), client.loop).result()
                konvoi_presence[pres["user_id"]] = {"status": pres["status"], "name": user.name if user is not None else pres["user_id"]}

            presence_chart_data = [len([x for x in konvoi_presence.keys() if konvoi_presence[x]["status"] == "attend"]),
                                   len([x for x in konvoi_presence.keys() if konvoi_presence[x]["status"] == "missing"]),
                                   len([x for x in konvoi_presence.keys() if konvoi_presence[x]["status"] == "unsure"])]
        else:
            konvoi_presence = None
            presence_chart_data = None

        cursor.close()
        con.close()

    return render_template("konvoi.html",
                           user=discord.fetch_user(),
                           roles=roles,
                           konvoi=return_data,
                           archive=archive,
                           updates=updates,
                           pics=pics,
                           presence=user_presence,
                           konvoi_presence=konvoi_presence,
                           presence_chart_data=presence_chart_data)

@views.route("/create/")
@requires_authorization
@role_checker("event-rolle")
def create_konvoi():
    args = {}

    print(request.args)

    if "name" not in request.args.keys():
        return render_template("create_konvoi.html", user=discord.fetch_user(), fill={})
    if request.args["name"] is None or request.args["name"] == "":
        flash("Der Konvoiname is obligatorisch!")
        return redirect(url_for("konvoi.create_konvoi"))

    for arg in request.args.keys():
        if request.args[arg] == "":
            args[arg] = "NULL"
        else:
            args[arg] = f"'{request.args[arg]}'"

    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute(f"INSERT INTO `konvois` (`name`, `description`, `truckersmp`, `date`, `gather`, `time`, `start`, `finish`, `pause`, `server`) " \
                       f"VALUES ({args['name']},{args['description']}, {args['tmp']}, {args['date']}, {args['gather']}, {args['time']}, {args['start']}, {args['finish']}, {args['pause']}, {args['server']})")

        r = f"/konvoi/{cursor.lastrowid}/"

        con.commit()
        cursor.close()

    return redirect(r)

@views.route("/edit/<int:konvoi_id>/")
@requires_authorization
@role_checker("event-rolle")
def edit_konvoi(konvoi_id):
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT `id` FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
        cursor.close()
    if konvoi_data is None:
        flash("Dieser Konvoi existiert nicht!")
        return redirect(url_for("konvoi.konvoi_list"))

    if "name" not in request.args.keys():
        konvoi_data = konvoi(konvoi_id, getter=True)

        for key in konvoi_data.keys():
            if konvoi_data[key] is None:
                konvoi_data[key] = ""

        return render_template("create_konvoi.html", user=discord.fetch_user(), fill=konvoi_data)

    args = {}

    if request.args["name"] is None or request.args["name"] == "":
        flash("Der Konvoiname is obligatorisch!")
        return redirect(url_for("konvoi.create_konvoi"))

    for arg in request.args.keys():
        if request.args[arg] == "":
            args[arg] = "NULL"
        else:
            args[arg] = f"'{request.args[arg]}'"

    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute(f"UPDATE `konvois` SET `name`={args['name']}, "
                       f"`description`={args['description']}, "
                       f"`truckersmp`={args['tmp']}, "
                       f"`date`={args['date']}, "
                       f"`gather`={args['gather']}, "
                       f"`time`={args['time']}, "
                       f"`start`={args['start']}, "
                       f"`finish`={args['finish']}, "
                       f"`pause`={args['pause']}, "
                       f"`server`={args['server']} "
                       f"WHERE `id`='{konvoi_id}'")

        con.commit()
        cursor.close()

    flash("Änderungen übernommen")
    return redirect(f"/konvoi/{konvoi_id}/")

@views.route("/update/<int:konvoi_id>/", methods=["GET", "POST"])
@requires_authorization
@role_checker("event-rolle")
def update_konvoi(konvoi_id):
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT `id` FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
        cursor.close()
    if konvoi_data is None:
        flash("Dieser Konvoi existiert nicht!")
        return redirect(url_for("konvoi.konvoi_list"))

    file = request.files['picture']
    if file.filename != "":
        f = BytesIO(file.stream.read())
    else:
        f = None

    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        values = (konvoi_id, request.form['text'], f.read() if f is not None else 'NULL')
        cursor.execute(f"INSERT INTO `konvoi_updates` (`konvoi_id`, `text`, `picture`) "
                       f"VALUES (%s, %s, %s)", values)
        con.commit()
        cursor.close()

    if f is not None:
        f.close()

    flash("Update Nachricht gespeichert!")
    return redirect("/konvoi/%s/" % konvoi_id)

@views.route("/updates/pics/<int:update_id>/")
@requires_authorization
@role_checker("fahrer-rolle")
def update_pics(update_id):
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM `konvoi_updates` WHERE `id`='%s'" % update_id)
        data = cursor.fetchone()
        cursor.close()
    if data is None or data["picture"] is None:
        return abort(404)

    f = BytesIO(data["picture"])

    return send_file(f, mimetype="image/jpg")

@views.route("/presence/<int:konvoi_id>/")
@requires_authorization
@role_checker("fahrer-rolle")
def presence(konvoi_id):
    if request.args["status"] not in ["attend", "missing", "unsure"]:
        return abort(flask.Response(response="Valid arguments for 'status' are: 'attend', 'missing', and 'unsure'", status=400))

    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute(f"INSERT INTO `presence` (`user_id`, `konvoi_id`, `status`) "
                       f"VALUES ('{discord.user_id}', '{konvoi_id}', '{request.args['status']}') "
                       f"ON DUPLICATE KEY "
                       f"UPDATE `status`='{request.args['status']}'")

        con.commit()
        con.close()

    flash("Deine Rückmeldung wurde gespeichert. Vielen Dank!")
    return redirect(url_for("konvoi.konvoi", konvoi_id=konvoi_id))
