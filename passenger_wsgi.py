#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask, g, render_template, request, flash, url_for, redirect, make_response, abort, jsonify
from flask_mail import Message, Mail
import time
import json
import sys
import os
from datetime import datetime, timedelta
import settings
import database
import helper
import paho.mqtt.client as mqtt


sys.path.insert(0, os.path.dirname(__file__))

application = Flask(__name__, static_url_path='/static', static_folder='static')

application.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopOqwer13door'
application.config['SESSION_COOKIE_NAME'] = 'door_locker'

application.config['MAIL_SERVER'] = settings.MAIL_SERVER
application.config['MAIL_PORT'] = 465
application.config['MAIL_USERNAME'] = settings.MAIL_USERNAME
application.config["MAIL_PASSWORD"] = settings.MAIL_PASSWORD
application.config["MAIL_USE_TLS"] = False
application.config["MAIL_USE_SSL"] = True

mail = Mail(application)
mqtt_client = mqtt.Client()


def mqtt_connect():
    mqtt_client.connect(settings.MQTT_BROKER_URL, settings.MQTT_BROKER_PORT, 60)
    mqtt_client.loop_start()


def mqtt_disconnect():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()


def mqtt_publish(topic: str, data: str):
    global mqtt_client

    publish_result = mqtt_client.publish(topic=topic, payload=data, qos=1, retain=False)
    publish_result.wait_for_publish()


@application.before_request
def before_request():
    g.db = database.open_db()


@application.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        database.close_db(g.db)


@application.route('/logout')
def logout():
    token = request.cookies.get('token')
    user = database.get_user(db=g.db, token=token)
    if user:
        database.update_user(db=g.db, email=user["email"], token="")

    return redirect(url_for('index'))


@application.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@application.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = database.get_user(db=g.db, email=email)

    if not user:
        flash('Invalid e-mail or password')
        return redirect(url_for('login'))

    encrypted_pass = helper.hash_password(password)
    if encrypted_pass != user["password"]:
        flash('Invalid e-mail or password.')
        return redirect(url_for('login'))

    token = helper.generate_token()
    database.update_user(db=g.db, email=email, token=token)

    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', token)
    return response


@application.route('/device_login', methods=['GET'])
def device_login():
    args = request.args
    name = args.get("name")
    password = args.get("password")

    if name and password:
        device = database.get_device(db=g.db, name=name)

        if device:
            encrypted_pass = helper.hash_password(password)
            if encrypted_pass != device["password"]:
                response = {"status": "ERROR", "detail": "Invalid name or password"}
            else:
                token = helper.generate_token()
                topic = helper.generate_random_string()
                life_sign = helper.generate_random_string()
                trigger = helper.generate_random_string()

                device_data = json.dumps({
                    "lifesign": life_sign,
                    "trigger": trigger,
                    "topic": topic,
                    "timeout": settings.LIFESIGN_TIMEOUT
                })

                database.update_device(db=g.db, name=name, token=token, data=device_data)

                response = {
                    "status": "OK",
                    "token": token,
                    "lifesign": life_sign,
                    "trigger": trigger,
                    "topic": topic,
                    "timeout": settings.LIFESIGN_TIMEOUT
                }
        else:
            response = {"status": "ERROR", "detail": "Invalid name or password"}
    else:
        response = {"status": "ERROR", "detail": "Missing password or name"}

    return jsonify(response)


@application.route('/device_ping', methods=['GET'])
def device_ping():
    args = request.args
    token = args.get("token")

    if token:
        device = database.get_device(db=g.db, token=token)
        if device:
            try:
                devices = database.get_device(db=g.db)

                if devices:
                    mqtt_connect()

                    for item in devices:
                        device_data = json.loads(item["data"])
                        topic = device_data["topic"]
                        lifesign = device_data["lifesign"]

                        mqtt_publish(topic=topic, data=lifesign)

                    mqtt_disconnect()

                response = {"status": "OK"}
            except Exception as exc:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(f"ERROR: parsing device on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
                response = {"status": "ERROR", "detail": "JSON parsing error"}
        else:
            response = {"status": "ERROR", "detail": "Unauthorized"}
    else:
        response = {"status": "ERROR", "detail": "Missing token"}

    return jsonify(response)


@application.route('/device_lifesign_confirm', methods=['GET'])
def device_lifesign_confirm():
    args = request.args
    token = args.get("token")

    if token:
        device = database.get_device(db=g.db, token=token)
        if device:
            try:
                # Update device ping time
                raw_data = device["data"]
                device_data = json.loads(raw_data)

                device_data["ping_time"] = int(time.time())
                database.update_device(db=g.db, name=device["name"], data=json.dumps(device_data))

                response = {"status": "OK"}
            except Exception as exc:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(f"ERROR: parsing device on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)
                response = {"status": "ERROR", "detail": "JSON parsing error"}
        else:
            response = {"status": "ERROR", "detail": "Unauthorized"}
    else:
        response = {"status": "ERROR", "detail": "Missing token"}

    return jsonify(response)


@application.route('/', methods=['GET'])
def index():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    database.cleanup_expired_links(db=g.db)

    guest_links = database.get_guest(db=g.db, email=user["email"])
    start_date = helper.date_to_string(datetime.now())
    end_date = helper.date_to_string(datetime.now() + timedelta(days=7))

    connected_devices = []
    devices = database.get_device(db=g.db)
    if devices:
        for device in devices:
            device_data = json.loads(device["data"])
            ping_time = device_data.get("ping_time", 0)
            dev_connected = (time.time() - ping_time) < (settings.LIFESIGN_TIMEOUT * 1.5)
            connected_devices.append({"name": device["name"], "connected": dev_connected})

    return render_template(
        'index.html',
        guest_links=guest_links,
        start_date=start_date,
        end_date=end_date,
        connected_devices=connected_devices
    )


@application.route('/unlock', methods=['GET'])
def unlock():
    args = request.args
    token = args.get("token")

    if token:
        # Unlocking using temporary link
        guest = database.get_guest(db=g.db, token=token)
        if guest:
            valid_until = helper.string_to_date(guest["valid_until"])
            today = datetime.now().replace(minute=0, hour=0, second=0)

            if valid_until < today:
                return render_template('token_expired.html')
        else:
            return render_template('token_expired.html')
    else:
        # Unlocking using normal user link
        token = request.cookies.get('token')
        if token:
            user = database.get_user(db=g.db, token=token)
            if not user:
                return redirect(url_for('login'))

    if not token:
        abort(404)

    devices = database.get_device(db=g.db)
    if devices:
        mqtt_connect()
        for device in devices:
            if device["data"]:
                device_data = json.loads(device["data"])
                topic = device_data.get("topic", "")
                trigger = device_data.get("trigger", "")

                mqtt_publish(topic=topic, data=trigger)
        mqtt_disconnect()

    return render_template('unlock.html')


@application.route('/reset_password', methods=['GET'])
def reset_password():
    return render_template('reset_password.html')


@application.route('/reset_password', methods=['POST'])
def reset_password_post():
    email = request.form.get('email')
    user = database.get_user(db=g.db, email=email)

    flash('If the provided e-mail address is in our database, we will send you a reset link.')
    if user:
        token = helper.generate_token()
        database.update_user(db=g.db, email=email, token=token)

        base_url = request.base_url.replace("reset_password", "set_password")

        reset_link = f"{base_url}?token={token}"

        mail_message = Message('Reset unlock portal password.', sender="do_not_reply@door.lock",
                               recipients=[email])
        mail_message.html = "<p>To reset your password, klick the following <a href='{}'>link</a>.</p>".format(reset_link)
        mail.send(mail_message)

    return redirect(url_for('index'))


@application.route('/set_password', methods=['GET'])
def set_password():
    args = request.args
    token = args.get("token")

    user = database.get_user(db=g.db, token=token)
    if not user:
        abort(404)

    return render_template('set_password.html', token=token)


@application.route('/set_password', methods=['POST'])
def set_password_post():
    password_1 = request.form.get('password_1')
    password_2 = request.form.get('password_2')
    token = request.form.get('token')
    user = database.get_user(db=g.db, token=token)

    if not user:
        flash("Error: Invalid token or expired link!")
        return redirect(url_for('index'))

    if password_1 != password_2:
        flash("Error: Passwords are not the same!")
        return redirect(url_for('set_password', token=token))

    ret_val = helper.validate_password(password_1)

    if ret_val == 0:
        hashed_password = helper.hash_password(password_1)
        database.update_user(db=g.db, email=user["email"], password=hashed_password)

        flash("Your password was changed successfully. You may now use it to login.")
        return redirect(url_for('login'))
    else:
        if ret_val == 0:
            flash("Error: Password can not contain empty spaces!")
        else:
            flash("Error: Password can not be shorter than 5 characters!")
        return redirect(url_for('set_password', token=token))


@application.route('/get_temporary_unlock_link', methods=['POST'])
def get_temporary_unlock_link():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    valid_until = request.form.get('valid_until')

    valid_date = helper.string_to_date(valid_until)
    if valid_date is None:
        valid_date = datetime.now() + timedelta(days=7)
        valid_until = helper.date_to_string(valid_date)

    token = helper.generate_token()
    database.add_guest(db=g.db, email=user["email"], token=token, valid_until=valid_until)

    return redirect(url_for('index'))


@application.route('/delete_temporary_unlock_link', methods=['GET'])
def delete_temporary_unlock_link():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(db=g.db, token=token)
    if not user:
        return redirect(url_for('login'))

    args = request.args
    link_token = args.get("link_token")

    database.delete_guest(db=g.db, token=link_token)
    return redirect(url_for('index'))
