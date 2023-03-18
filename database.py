import sys
import sqlite3
import os
from datetime import datetime


current_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_path, "database.db")


def init_database():
    if not os.path.isfile(db_path):
        # Database does not exist. Create one
        db = sqlite3.connect(db_path)

        sql = "create table users (email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, token TEXT UNIQUE)"
        db.execute(sql)
        db.commit()

        sql = "create table devices (name TEXT NOT NULL UNIQUE, password TEXT NOT NULL, data TEXT, token TEXT UNIQUE)"
        db.execute(sql)
        db.commit()

        sql = "create table guests (email TEXT, token TEXT UNIQUE, valid_until INTEGER)"
        db.execute(sql)
        db.commit()

        db.close()


def open_db():
    init_database()
    return sqlite3.connect(db_path)


def close_db(db):
    db.close()


def query_db(db, query, args=(), one=False):
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def exec_db(db, query):
    db.execute(query)
    if not query.startswith('SELECT'):
        db.commit()


def add_user(db, email: str, password: str = None):
    sql = f"INSERT INTO users(email, password) VALUES ('{email}', '{password}')"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding user to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_user(db, email: str,):
    sql = f"DELETE FROM users WHERE email = '{email}'"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing user from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_user(db, email: str = None, token: str = None):
    one = True
    if email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    elif token:
        sql = f"SELECT * FROM users WHERE token = '{token}'"
    else:
        sql = f"SELECT * FROM users"
        one = False

    try:
        user = query_db(db, sql, one=one)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        user = None

    return user


def update_user(db, email: str, token: str = None, password: str = None):
    user = get_user(db=db, email=email)

    if user:
        if token is not None:
            user["token"] = token
        if password:
            user["password"] = password

        sql = "UPDATE users SET token = '{}', password = '{}' WHERE email = '{}'" \
              "".format(user["token"], user["password"], email)

        try:
            exec_db(db, sql)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating user in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_device(db, name: str, password: str = None):
    sql = f"INSERT INTO devices (name, password) VALUES ('{name}', '{password}')"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding device to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_device(db, name: str, ):
    sql = f"DELETE FROM devices WHERE name = '{name}'"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing device from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_device(db, name: str = None, token: str = None):
    one = True
    if name:
        sql = f"SELECT * FROM devices WHERE name = '{name}'"
    elif token:
        sql = f"SELECT * FROM devices WHERE token = '{token}'"
    else:
        sql = f"SELECT * FROM devices"
        one = False

    try:
        device = query_db(db, sql, one=one)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        device = None

    return device


def update_device(db, name: str, password: str = None, token: str = None, data: str = None):
    device = get_device(db, name=name)

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
            exec_db(db, sql)
        except Exception as exc:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("ERROR updating device in db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def add_guest(db, email: str, token: str, valid_until: str):
    sql = f"INSERT INTO guests (email, token, valid_until) VALUES ('{email}', '{token}', '{valid_until}')"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR adding guest to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def delete_guest(db, token: str):
    sql = f"DELETE FROM guests WHERE token = '{token}'"

    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing guest from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def get_guest(db, token: str = None, email: str = None):
    if token:
        sql = f"SELECT * FROM guests WHERE token = '{token}'"
        one = True
    elif email:
        sql = f"SELECT * FROM guests WHERE email = '{email}'"
        one = False
    else:
        return None

    try:
        device = query_db(db, sql, one=one)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
        device = None

    return device


def cleanup_expired_links(db):
    sql = f"DELETE FROM guests WHERE valid_until < date('now', '-1 day')"
    try:
        exec_db(db, sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR removing guest links from db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)
