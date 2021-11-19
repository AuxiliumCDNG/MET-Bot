import functools

import discord.errors as derrors
from flask import abort

from globals import discord, client, connection_pool


def change_setting(setting, value):
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM settings WHERE setting='%s'" % (str(setting)))
        if len(cursor.fetchall()) > 0:
            cursor.execute("UPDATE settings SET value='%s' WHERE setting='%s'" % (str(value), str(setting)))
        else:
            cursor.execute("INSERT INTO settings (setting, value) VALUES ('%s', '%s')" % (str(setting), str(value)))
        con.commit()
        cursor.close()

    return True


def get_setting(setting):
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM settings WHERE setting='%s'" % (str(setting)))
        res = cursor.fetchone()
        cursor.close()

    if res is not None:
        return str(res["value"])
    else:
        return None

def role_checker(role_name):
    def decorator(view):
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            search_role = int(get_setting(role_name)[3:-1])
            authorized = False
            user = client.get_user(discord.user_id)

            if user is None:
                discord.fetch_user()
                user = client.get_user(discord.user_id)  # NEEDS TO CHANGE WITH THE ABOVE!

            for guild in user.mutual_guilds:
                try:
                    guild = client.get_guild(guild.id)
                except derrors.Forbidden:
                    continue

                member = guild.get_member(user.id)
                roles = [role.id for role in member.roles]
                if search_role in roles:
                    authorized = True
                    break

            if not authorized:
                return abort(401)

            return view(*args, **kwargs)
        return wrapper
    return decorator

def roles_getter():
    def decorator(view):
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            user = client.get_user(discord.user_id)

            if user is None:
                discord.fetch_user()
                user = client.get_user(discord.user_id)  # NEEDS TO CHANGE WITH THE ABOVE!

            role_names = []
            for guild in user.mutual_guilds:
                try:
                    guild = client.get_guild(guild.id)
                except derrors.Forbidden:
                    continue

                member = guild.get_member(user.id)
                roles = [role.id for role in member.roles]

                with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
                    for role in roles:
                        cursor.execute(f"SELECT `setting` FROM `settings` WHERE `value`='<@&{role}>'")
                        res = cursor.fetchone()
                        if res is not None:
                            role_names.append(res["setting"])

            return view(roles=role_names, *args, **kwargs)
        return wrapper
    return decorator
