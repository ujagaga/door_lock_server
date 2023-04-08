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

    sql = "create table users (email varchar(255) NOT NULL UNIQUE, password varchar(255) NOT NULL, token varchar(32) UNIQUE, role varchar(5))"
    db_cursor.execute(sql)

    sql = "create table devices (name varchar(255) NOT NULL UNIQUE, password varchar(255) NOT NULL, data varchar(512), token varchar(32) UNIQUE)"
    db_cursor.execute(sql)

    sql = "create table guests (email varchar(255), token varchar(32) UNIQUE, valid_until varchar(16))"
    db_cursor.execute(sql)

    sql = "create table nfc_codes (code varchar(32) UNIQUE, alias varchar(255), created_at varchar(16), email varchar(255), last_used varchar(16))"
    db_cursor.execute(sql)

    connection.commit()


def check_table_exists(connection, db_cursor, tablename):
    db_cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{0}'"
                      "".format(tablename.replace('\'', '\'\'')))
    if db_cursor.fetchone()[0] == 1:
        return True

    return False


def add_user(connection, db_cursor, email: str, password: str = None, role: str = ""):
    sql = f"INSERT INTO users(email, password, role) VALUES ('{email}', '{password}', '{role}')"

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
        return None

    try:
        db_cursor.execute(sql)
        if one:
            data = db_cursor.fetchone()
            if data:
                user = {"email": data[0], "password": data[1], "token": data[2], "role": data[3]}
            else:
                user = None
        else:
            user = []
            raw_data = db_cursor.fetchall()
            if raw_data:
                for data in raw_data:
                    user.append({"email": data[0], "password": data[1], "token": data[2], "role": data[3]})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        user = None

    return user


def update_user(connection, db_cursor, email: str, token: str = None, password: str = None, role: str = None):
    user = get_user(connection, db_cursor, email=email)

    if user:
        if token:
            user["token"] = token
        if password:
            user["password"] = password
        if role:
            user["role"] = role

        sql = "UPDATE users SET token = '{}', password = '{}', role = '{}' WHERE email = '{}'" \
              "".format(user["token"], user["password"], user["role"], email)

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
            if data:
                device = {"name": data[0], "password": data[1], "data": data[2], "token": data[3]}
            else:
                device = None
        else:
            device = []
            raw_data = db_cursor.fetchall()
            if raw_data:
                for data in raw_data:
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
            if data:
                guest = {"email": data[0], "token": data[1], "valid_until": data[2]}
            else:
                guest = None
        else:
            guest = []
            raw_data = db_cursor.fetchall()
            if raw_data:
                for data in raw_data:
                    guest.append({"email": data[0], "token": data[1], "valid_until": data[2]})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        guest = None

    return guest


def delete_nfc_code(connection, db_cursor, code: str = None):
    if code:
        sql = f"DELETE FROM nfc_codes WHERE code = '{code}'"
    else:
        sql = f"DELETE FROM nfc_codes WHERE email IS NULL"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing nfc code from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_nfc_codes(connection, db_cursor, email: str = None, code: str = None, start_id: int = None, max_num: int = 10):
    one = False
    if code:
        sql = f"SELECT * FROM nfc_codes WHERE code = '{code}'"
        one = True
    elif email:
        sql = f"SELECT * FROM nfc_codes WHERE email = '{email}' ORDER BY created_at ASC"
    elif start_id:
        sql = f"SELECT * FROM nfc_codes WHERE email IS NOT NULL ORDER BY created_at ASC " \
              f"LIMIT {start_id}, {start_id + max_num}"
    else:
        sql = f"SELECT * FROM nfc_codes WHERE email IS NULL"

    try:
        db_cursor.execute(sql)
        if one:
            data = db_cursor.fetchone()
            if data:
                codes = {"code": data[0], "alias": data[1], "created_at": data[2], "email": data[3], "last_used": data[4]}
            else:
                codes = None
        else:
            codes = []
            raw_data = db_cursor.fetchall()
            if raw_data:
                for data in raw_data:
                    codes.append({"code": data[0], "alias": data[1], "last_used": data[4]})
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading nfc codes on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        codes = None

    return codes


def update_nfc_code(connection, db_cursor, code: str, email: str = None, last_used: str = None):
    if email:
        sql = f"UPDATE nfc_codes SET email = '{email}' WHERE code = '{code}'"
    elif last_used:
        sql = f"UPDATE nfc_codes SET last_used = '{last_used}' WHERE code = '{code}'"
    else:
        print("ERROR: No parameter to update NFC supplied.")

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR updating nfc code in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_nfc_code(connection, db_cursor, timestamp: str, code: str):
    sql = f"INSERT INTO nfc_codes (code, created_at) VALUES ('{code}', '{timestamp}')"

    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding nfc code to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def cleanup_expired_links(connection, db_cursor):
    sql = f"DELETE FROM guests WHERE valid_until < (NOW() - INTERVAL 1 DAY)"
    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing guest links from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def cleanup_unused_nfc_codes(connection, db_cursor):
    sql = f"DELETE FROM nfc_codes WHERE last_used < (NOW() - INTERVAL 6 MONTH)"
    try:
        db_cursor.execute(sql)
        connection.commit()
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing nfc codes from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)
