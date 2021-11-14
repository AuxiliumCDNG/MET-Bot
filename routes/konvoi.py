import datetime
from io import BytesIO

from flask import Blueprint, render_template, flash, url_for, redirect, request, abort, send_file
from flask_discord import requires_authorization

from globals import db, discord
from helpers import role_checker

views = Blueprint("konvoi", __name__, url_prefix="/konvoi/")

@views.route("/")
@requires_authorization
@role_checker("fahrer-rolle")
def konvoi_list():
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM konvois")
        konvois = cursor.fetchall()
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
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM konvois")
        konvois = cursor.fetchall()
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
def konvoi(konvoi_id, getter=False):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
    if konvoi_data is None:
        flash("Diesen Konvoi gibt es nicht in der Datenbank.")
        return redirect(url_for("konvoi.konvoi_list"))

    today = datetime.date.today().toordinal()
    try:
        archive = konvoi_data["date"].toordinal() < today
    except AttributeError:
        archive = False

    if archive and not request.path.__contains__("archive"):
        return redirect("/konvoi/archive/%s/" % konvoi_id)

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

    with db.cursor() as cursor:
        cursor.execute(f"SELECT `id`, `konvoi_id`, `text` FROM `konvoi_updates` WHERE `konvoi_id`='{konvoi_id}' ORDER BY `id` DESC")
        updates = cursor.fetchall()
        cursor.execute(f"SELECT `id` FROM `konvoi_updates` WHERE `picture`<>'NULL'")
        pics = [x["id"] for x in cursor.fetchall()]

    return render_template("konvoi.html", user=discord.fetch_user(), konvoi=return_data, archive=archive, updates=updates, pics=pics)

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

    with db.cursor() as cursor:
        cursor.execute(f"INSERT INTO `konvois` (`name`, `description`, `truckersmp`, `date`, `gather`, `time`, `start`, `finish`, `pause`, `server`) " \
                       f"VALUES ({args['name']},{args['description']}, {args['tmp']}, {args['date']}, {args['gather']}, {args['time']}, {args['start']}, {args['finish']}, {args['pause']}, {args['server']})")

        r = f"/konvoi/{cursor.lastrowid}/"

        db.commit()

    return redirect(r)

@views.route("/edit/<int:konvoi_id>/")
@requires_authorization
@role_checker("event-rolle")
def edit_konvoi(konvoi_id):
    with db.cursor() as cursor:
        cursor.execute("SELECT `id` FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
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

    with db.cursor() as cursor:
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

        db.commit()

    flash("Änderungen übernommen")
    return redirect(f"/konvoi/{konvoi_id}/")

@views.route("/update/<int:konvoi_id>/", methods=["GET", "POST"])
@requires_authorization
@role_checker("event-rolle")
def update_konvoi(konvoi_id):
    with db.cursor() as cursor:
        cursor.execute("SELECT `id` FROM konvois WHERE `id`='%s'" % konvoi_id)
        konvoi_data = cursor.fetchone()
    if konvoi_data is None:
        flash("Dieser Konvoi existiert nicht!")
        return redirect(url_for("konvoi.konvoi_list"))

    file = request.files['picture']
    if file.filename != "":
        f = BytesIO(file.stream.read())
    else:
        f = None

    with db.cursor() as cursor:
        values = (konvoi_id, request.form['text'], f.read() if f is not None else 'NULL')
        cursor.execute(f"INSERT INTO `konvoi_updates` (`konvoi_id`, `text`, `picture`) "
                       f"VALUES (%s, %s, %s)", values)
        db.commit()

    if f is not None:
        f.close()

    flash("Update Nachricht gespeichert!")
    return redirect("/konvoi/%s/" % konvoi_id)

@views.route("/updates/pics/<int:update_id>/")
@requires_authorization
@role_checker("fahrer-rolle")
def update_pics(update_id):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM `konvoi_updates` WHERE `id`='%s'" % update_id)
        data = cursor.fetchone()
    if data is None or data["picture"] is None:
        return abort(404)

    f = BytesIO(data["picture"])

    return send_file(f, mimetype="image/jpg")
