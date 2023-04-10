import sys
import settings
import mysql.connector


def open_db():
    connection = mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        passwd=settings.DB_PASS,
        database=settings.DB_NAME
    )
    db_cursor = connection.cursor(buffered=True)
    return (connection, db_cursor)


def close_db(connection, db_cursor):
    db_cursor.close()
    connection.close()


def init_database(connection, db_cursor):
    print("Creating tables...")

    sql = "create table users (email varchar(255) NOT NULL UNIQUE, password varchar(255) NOT NULL, token varchar(32) UNIQUE)"
    db_cursor.execute(sql)

    sql = "create table devices (name varchar(255) NOT NULL UNIQUE, password varchar(255) NOT NULL, data varchar(512), token varchar(32) UNIQUE)"
    db_cursor.execute(sql)

    sql = "create table guests (email varchar(255), token varchar(32) UNIQUE, valid_until varchar(16))"
    db_cursor.execute(sql)

    connection.commit()


def check_table_exists(connection, db_cursor, tablename):
    db_cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{0}'"
                      "".format(tablename.replace('\'', '\'\'')))
    if db_cursor.fetchone()[0] == 1:
        return True

    return False


def add_user(connection, db_cursor, email: str, password: str = None):
    sql = f"INSERT INTO users(email, password) VALUES ('{email}', '{password}')"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding user to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_user(connection, db_cursor, email: str,):
    sql = f"DELETE FROM users WHERE email = '{email}'"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_user(connection, db_cursor, email: str = None, token: str = None):
    one = True
    if email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    elif token:
        sql = f"SELECT * FROM users WHERE token = '{token}'"
    else:
        sql = f"SELECT * FROM users"

    try:
        db_cursor.execute(sql)
        if one:
            data = db_cursor.fetchone()
            user = {"email": data[0], "password": data[1], "token": data[2]}
        else:
            user = []
            for data in db_cursor.fetchall():
                user.append({"email": data[0], "password": data[1], "token": data[2]})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        user = None

    return user


def update_user(connection, db_cursor, email: str, token: str = None, password: str = None):
    user = get_user(connection, db_cursor, email=email)

    if user:
        if token is not None:
            user["token"] = token
        if password:
            user["password"] = password

        sql = "UPDATE users SET token = '{}', password = '{}' WHERE email = '{}'" \
              "".format(user["token"], user["password"], email)

        try:
            db_cursor.execute(sql)
            connection.commit()
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating user in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_device(connection, db_cursor, name: str, password: str = None):
    sql = f"INSERT INTO devices (name, password) VALUES ('{name}', '{password}')"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding device to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_device(connection, db_cursor, name: str, ):
    sql = f"DELETE FROM devices WHERE name = '{name}'"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing device from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_device(connection, db_cursor, name: str = None, token: str = None):
    one = True
    if name:
        sql = f"SELECT * FROM devices WHERE name = '{name}'"
    elif token:
        sql = f"SELECT * FROM devices WHERE token = '{token}'"
    else:
        sql = f"SELECT * FROM devices"
        one = False

    try:
        db_cursor.execute(sql)
        if one:
            data = db_cursor.fetchone()
            device = {"name": data[0], "password": data[1], "data": data[2], "token": data[3]}
        else:
            device = []
            for data in db_cursor.fetchall():
                device.append({"name": data[0], "password": data[1], "data": data[2], "token": data[3]})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        device = None

    return device


def update_device(connection, db_cursor, name: str, password: str = None, token: str = None, data: str = None):
    device = get_device(connection, db_cursor, name=name)

    if device:
        if token is not None:
            device["token"] = token
        if data:
            device["data"] = data
        if password:
            device["password"] = password

        sql = "UPDATE devices SET token = '{}', data = '{}', password = '{}' WHERE name = '{}'" \
              "".format(device["token"], device["data"], device["password"], name)

        try:
            db_cursor.execute(sql)
            connection.commit()
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating device in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_guest(connection, db_cursor, email: str, token: str, valid_until: str):
    sql = f"INSERT INTO guests (email, token, valid_until) VALUES ('{email}', '{token}', '{valid_until}')"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding guest to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_guest(connection, db_cursor, token: str):
    sql = f"DELETE FROM guests WHERE token = '{token}'"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing guest from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_guest(connection, db_cursor, token: str = None, email: str = None):
    if token:
        sql = f"SELECT * FROM guests WHERE token = '{token}'"
        one = True
    elif email:
        sql = f"SELECT * FROM guests WHERE email = '{email}'"
        one = False
    else:
        return None

    try:
        db_cursor.execute(sql)
        if one:
            data = db_cursor.fetchone()
            guest = {"email": data[0], "token": data[1], "valid_until": data[2]}
        else:
            guest = []
            for data in db_cursor.fetchall():
                guest.append({"email": data[0], "token": data[1], "valid_until": data[2]})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        guest = None

    return guest


def cleanup_expired_links(connection, db_cursor, ):
    sql = f"DELETE FROM guests WHERE valid_until < (NOW() - INTERVAL 1 DAY)"
    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing guest links from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)
