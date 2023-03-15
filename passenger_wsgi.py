#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from flask import Flask, g, render_template, request, flash, url_for, redirect, make_response
from werkzeug.utils import secure_filename
import json
import sys
import requests
import sqlite3
import os
import urllib.parse
from datetime import datetime, timedelta
import string
import random
from hashlib import sha256


sys.path.insert(0, os.path.dirname(__file__))

db_path = "database.db"
application = Flask(__name__, static_url_path='/static', static_folder='static')

application.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopOqwer13door'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
application.config['SESSION_COOKIE_NAME'] = 'door_locker'

ROLE_ADMIN = "admin"
ROLE_GUEST = "guest"


def init_database():
    if not os.path.isfile(db_path):
        # Database does not exist. Create one
        db = sqlite3.connect(db_path)

        sql = "create table users (username TEXT, email TEXT, password TEXT, token TEXT, role TEXT, " \
              "valid_until INTEGER)"
        db.execute(sql)
        db.commit()

        db.close()


def query_db(db, query, args=(), one=False):
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def exec_db(query):
    g.db.execute(query)
    if not query.startswith('SELECT'):
        g.db.commit()


def get_user(username: str = None, token: str = None, email: str = None):
    data = None

    if username:
        sql = f"SELECT * FROM users WHERE username = '{username}'"
    elif token:
        sql = f"SELECT * FROM users WHERE token = '{token}'"
    elif email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    else:
        return None

    try:
        user = query_db(g.db, sql, one=True)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)

    return user


def update_user(username: str, token: str = None, email: str = None, password: str = None, role: str = None, valid_until: int = -1):
    user = get_user(username=username)

    if user:
        if token:
            user["token"] = token
        if email:
            user["email"] = email
        if password:
            user["password"] = password
        if role:
            user["role"] = role
        if valid_until:
            user["valid_until"] = valid_until

        sql = f"UPDATE users SET token = '{token}', email = '{email}', password = '{password}', role = '{role}', " \
              f"valid_until = '{valid_until}' WHERE username = '{username}'"
    else:
        sql = f"INSERT INTO users (username, password, role, email, valid_until) " \
              f"VALUES ('{username}', '{password}', '{role}', '{email}', '{valid_until}')"

    try:
        exec_db(sql)
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR writing user to db on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


def generate_token():
    return ''.join(random.choices(string.ascii_letters, k=32))


def encrypt_password(password: str):
    return sha256(password.encode('utf-8')).hexdigest()


@application.before_request
def before_request():
    if not os.path.isfile(db_path):
        init_database()

    g.db = sqlite3.connect(db_path)


@application.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@application.route('/logout')
def logout():
    token = request.cookies.get('token')
    user = get_user(token=token)
    if user:
        update_user(username=user["username"], token="")

    return redirect(url_for('index'))


@application.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@application.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = get_user(username=username)

    if not user:
        flash('Neispravno korisničko ime ili lozinka.')
        return redirect(url_for('login'))

    encrypted_pass = encrypt_password(password)
    if encrypted_pass != user["password"]:
        flash('Neispravno korisničko ime ili lozinka.')
        return redirect(url_for('login'))

    token = generate_token()
    update_user(username=username, token=token)

    response = make_response(redirect(url_for('admin')))
    response.set_cookie('token', token)
    return response


@application.route('/', methods=['GET'])
def index():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = get_user(token=token)
    if not user:
        return redirect(url_for('login'))

    if not user["role"] == ROLE_ADMIN:
        return redirect(url_for('login'))

    return render_template('index.html')


@application.route('/unlock', methods=['GET'])
def unlock():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = get_user(token=token)
    if not user:
        return redirect(url_for('login'))

    return render_template('unlock.html')


