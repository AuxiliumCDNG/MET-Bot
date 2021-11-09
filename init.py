def init(db):
    with db.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS settings ("
                       "id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                       "setting VARCHAR(100),"
                       "value VARCHAR(100)"
                       ")")
        cursor.execute("CREATE TABLE IF NOT EXISTS konvois ("
                       "id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                       "name VARCHAR(255),"
                       "description TEXT,"
                       "truckersmp TEXT,"
                       "gather DATETIME,"
                       "time DATETIME,"
                       "start VARCHAR(255),"
                       "finish VARCHAR(255),"
                       "pause VARCHAR(255),"
                       "server VARCHAR(255),"
                       "token VARCHAR(100)"
                       ")")
