def change_setting(setting, value, db):
    with db.cursor() as cursor:
        if cursor.execute("SELECT * FROM settings WHERE setting='%s'" % (str(setting))) > 0:
            cursor.execute("UPDATE settings SET value='%s' WHERE setting='%s'" % (str(value), str(setting)))
        else:
            cursor.execute("INSERT INTO settings (setting, value) VALUES ('%s', '%s')" % (str(setting), str(value)))
        db.commit()

    return True


def get_setting(setting, db):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM settings WHERE setting='%s'" % (str(setting)))
        res = cursor.fetchone()

    if res is not None:
        return str(res["value"])
    else:
        return None
