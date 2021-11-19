from globals import connection_pool

def init():
    with connection_pool.connection() as con, con.cursor(dictionary=True) as cursor:
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
                       "date DATE,"
                       "gather TIME,"
                       "time TIME,"
                       "start VARCHAR(255),"
                       "finish VARCHAR(255),"
                       "pause VARCHAR(255),"
                       "server VARCHAR(255),"
                       "token VARCHAR(100)"
                       ")")
        cursor.execute("CREATE TABLE IF NOT EXISTS konvoi_updates ("
                       "id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"
                       "konvoi_id INT,"
                       "text TEXT,"
                       "picture MEDIUMBLOB"
                       ")")
        cursor.execute("CREATE TABLE IF NOT EXISTS presence ("
                       "user_id BIGINT UNSIGNED PRIMARY KEY NOT NULL,"
                       "konvoi_id INT,"
                       "status VARCHAR(255)"
                       ")")
        con.commit()
        cursor.close()
