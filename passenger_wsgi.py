#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

from flask import Flask, g, render_template, request, flash, url_for, redirect, make_response, jsonify
from werkzeug.utils import secure_filename
from flask_mqtt import Mqtt
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
# import paho.mqtt.client as paho
# from paho.mqtt.properties import Properties
# from paho.mqtt.packettypes import PacketTypes

sys.path.insert(0, os.path.dirname(__file__))

current_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(current_path, "database.db")
# db_path = "database.db"
application = Flask(__name__, static_url_path='/static', static_folder='static')

application.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopOqwer13door'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
application.config['SESSION_COOKIE_NAME'] = 'door_locker'

application.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
application.config['MQTT_BROKER_PORT'] = 1883
application.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
application.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
application.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
application.config['MQTT_TLS_ENABLED'] = False  # If your server supports TLS, set it T

topic_file = os.path.join(current_path, "mqtt_topic.cfg")

ROLE_ADMIN = "admin"
ROLE_GUEST = "guest"

mqtt_client = Mqtt(application)


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
        user = None

    return user


def update_user(username: str, token: str = None, email: str = None, password: str = None, role: str = None, valid_until: int = -1):
    user = get_user(username=username)

    print("Reading user: ", user)
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
        print("Reading user modified: ", user)

        sql = "UPDATE users SET token = '{}', email = '{}', password = '{}', role = '{}', valid_until = '{}' " \
              "WHERE username = '{}'".format(user["token"], user["email"], user["password"],
                                             user["role"], user["valid_until"], username)
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


def hash_password(password: str):
    return sha256(password.encode('utf-8')).hexdigest()


def mqtt_publish():
    try:
        file = open(topic_file, "r")
        topic = file.readline()
        file.close()

        ret = mqtt_client.publish(topic, 'unlock')

        if ret[0] != 0:
            print(f"ERROR publishing to MQTT. Error code: {ret}!", flush=True)

    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("ERROR publishing to MQTT on line {}!\n\t{}".format(exc_tb.tb_lineno, exc), flush=True)


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

    encrypted_pass = hash_password(password)
    if encrypted_pass != user["password"]:
        flash('Neispravno korisničko ime ili lozinka.')
        return redirect(url_for('login'))

    token = generate_token()
    update_user(username=username, token=token)

    response = make_response(redirect(url_for('index')))
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

    mqtt_publish()
    return render_template('unlock.html')
