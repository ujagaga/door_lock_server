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


def perform_unlock():
    devices = database.get_device(g.connection, g.db_cursor)
    if devices:
        mqtt_connect()
        for device in devices:
            if device["data"]:
                device_data = json.loads(device["data"])
                topic = device_data.get("topic", "")
                trigger = device_data.get("trigger", "")

                mqtt_publish(topic=topic, data=trigger)
        mqtt_disconnect()


@application.before_request
def before_request():
    g.connection, g.db_cursor = database.open_db()


@application.teardown_request
def teardown_request(exception):
    if hasattr(g, 'connection'):
        database.close_db(g.connection, g.db_cursor)


@application.route('/logout')
def logout():
    token = request.cookies.get('token')
    user = database.get_user(g.connection, g.db_cursor, token=token)
    if user:
        database.update_user(g.connection, g.db_cursor, email=user["email"], token="")

    return redirect(url_for('index'))


@application.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@application.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = database.get_user(g.connection, g.db_cursor, email=email)
    if not user:
        flash('Neispravna e-mail adresa ili lozinka.')
        return redirect(url_for('login'))

    encrypted_pass = helper.hash_password(password)
    if encrypted_pass != user["password"]:
        flash('Neispravno korisničko ime ili lozinka.')
        return redirect(url_for('login'))

    token = helper.generate_token()
    database.update_user(g.connection, g.db_cursor, email=email, token=token)

    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', token)
    return response


@application.route('/device_login', methods=['GET'])
def device_login():
    args = request.args
    name = args.get("name")
    password = args.get("password")

    if name and password:
        device = database.get_device(g.connection, g.db_cursor, name=name)

        if device:
            encrypted_pass = helper.hash_password(password)
            if encrypted_pass != device["password"]:
                response = {"status": "ERROR", "detail": "Bad password or name"}
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

                database.update_device(g.connection, g.db_cursor, name=name, token=token, data=device_data)

                response = {
                    "status": "OK",
                    "token": token,
                    "lifesign": life_sign,
                    "trigger": trigger,
                    "topic": topic,
                    "timeout": settings.LIFESIGN_TIMEOUT
                }
        else:
            response = {"status": "ERROR", "detail": "Bad password or name"}
    else:
        response = {"status": "ERROR", "detail": "Missing password or name"}

    return jsonify(response)


@application.route('/device_ping', methods=['GET'])
def device_ping():
    args = request.args
    token = args.get("token")

    if token:
        device = database.get_device(g.connection, g.db_cursor, token=token)
        if device:
            try:
                devices = database.get_device(g.connection, g.db_cursor)

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
        device = database.get_device(g.connection, g.db_cursor, token=token)
        if device:
            try:
                # Update device ping time
                raw_data = device["data"]
                device_data = json.loads(raw_data)

                device_data["ping_time"] = int(time.time())
                database.update_device(g.connection, g.db_cursor, name=device["name"], data=json.dumps(device_data))

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

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        return redirect(url_for('login'))

    database.cleanup_expired_links(g.connection, g.db_cursor)

    guest_links = database.get_guest(g.connection, g.db_cursor, email=user["email"])

    assigned_nfc_codes = database.get_nfc_codes(g.connection, g.db_cursor, email=user["email"])
    unassigned_nfc_code = database.get_nfc_codes(g.connection, g.db_cursor)

    start_date = helper.date_to_string(datetime.now())
    end_date = helper.date_to_string(datetime.now() + timedelta(days=7))

    connected_devices = []
    devices = database.get_device(g.connection, g.db_cursor)
    if devices:
        for device in devices:
            dev_data = device["data"]
            if not dev_data:
                device_data = {}
            else:
                device_data = json.loads(dev_data)
            ping_time = device_data.get("ping_time", 0)
            dev_connected = (time.time() - ping_time) < (settings.LIFESIGN_TIMEOUT * 1.5)
            connected_devices.append({"name": device["name"], "connected": dev_connected})

    return render_template(
        'index.html',
        token=token,
        guest_links=guest_links,
        start_date=start_date,
        end_date=end_date,
        connected_devices=connected_devices,
        nfc_codes=assigned_nfc_codes,
        new_code=unassigned_nfc_code
    )


@application.route('/unlock', methods=['GET'])
def unlock():
    args = request.args
    token = args.get("token")

    if token:
        # Unlocking using token from url
        guest = database.get_guest(g.connection, g.db_cursor, token=token)
        if guest:
            valid_until = helper.string_to_date(guest["valid_until"])
            today = datetime.now().replace(minute=0, hour=0, second=0)

            if valid_until < today:
                return render_template('token_expired.html')
        else:
            user = database.get_user(g.connection, g.db_cursor, token=token)
            if not user:
                return render_template('token_expired.html')
    else:
        # Unlocking using normal user link
        token = request.cookies.get('token')
        if token:
            user = database.get_user(g.connection, g.db_cursor, token=token)
            if not user:
                return redirect(url_for('login'))

    if not token:
        abort(404)

    perform_unlock()

    return render_template('unlock.html')


@application.route('/reset_password', methods=['GET'])
def reset_password():
    return render_template('reset_password.html')


@application.route('/reset_password', methods=['POST'])
def reset_password_post():
    email = request.form.get('email')
    user = database.get_user(g.connection, g.db_cursor, email=email)

    flash('Ako je priložena e-mail adresa u našoj bazi, poslaćemo Vam e-mail sa linkom za reset.')
    if user:
        token = helper.generate_token()
        database.update_user(g.connection, g.db_cursor, email=email, token=token)

        base_url = request.base_url.replace("reset_password", "set_password")

        reset_link = f"{base_url}?token={token}"

        mail_message = Message('Reset lozinke portala za otključavanje vrata', sender="do_not_reply@door_lock.lt19",
                               recipients=[email])
        mail_message.html = "<p>Da biste resetovali lozinku za pristup portalu za otključavanje vrata " \
                            "u Laze Telečkog 19, kliknite <a href='{}'>ovde</a>.</p>".format(reset_link)
        mail.send(mail_message)

    return redirect(url_for('index'))


@application.route('/set_password', methods=['GET'])
def set_password():
    args = request.args
    token = args.get("token")

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        abort(404)

    return render_template('set_password.html', token=token)


@application.route('/set_password', methods=['POST'])
def set_password_post():
    password_1 = request.form.get('password_1')
    password_2 = request.form.get('password_2')
    token = request.form.get('token')
    user = database.get_user(g.connection, g.db_cursor, token=token)

    if not user:
        flash("Greška: neispravan token ili je link istekao!")
        return redirect(url_for('index'))

    if password_1 != password_2:
        flash("Greška: lozinke nisu iste!")
        return redirect(url_for('set_password', token=token))

    ret_val = helper.validate_password(password_1)

    if ret_val == 0:
        hashed_password = helper.hash_password(password_1)
        database.update_user(g.connection, g.db_cursor, email=user["email"], password=hashed_password)

        flash("Lozinka je uspešno promenjena. Sada možete da se logujete sa njom.")
        return redirect(url_for('login'))
    else:
        if ret_val == 0:
            flash("Greška: Lozinka ne može da sadrži prazna mesta!")
        else:
            flash("Greška: lozinke ne može da bude kraća od 5 karaktera!")
        return redirect(url_for('set_password', token=token))


@application.route('/get_temporary_unlock_link', methods=['POST'])
def get_temporary_unlock_link():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        return redirect(url_for('login'))

    valid_until = request.form.get('valid_until')

    valid_date = helper.string_to_date(valid_until)
    if valid_date is None:
        valid_date = datetime.now() + timedelta(days=7)
        valid_until = helper.date_to_string(valid_date)

    token = helper.generate_token()
    database.add_guest(g.connection, g.db_cursor, email=user["email"], token=token, valid_until=valid_until)

    return redirect(url_for('index'))


@application.route('/delete_temporary_unlock_link', methods=['GET'])
def delete_temporary_unlock_link():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        return redirect(url_for('login'))

    args = request.args
    link_token = args.get("link_token")

    database.delete_guest(g.connection, g.db_cursor, token=link_token)
    return redirect(url_for('index'))


@application.route('/device_report_nfc_code', methods=['GET'])
def device_report_nfc_code():
    args = request.args
    token = args.get("token")

    if token:
        code = args.get("code")
        if code:
            # Delete unassigned codes
            database.delete_nfc_code(g.connection, g.db_cursor)

            timestamp = helper.date_to_string(datetime.today())

            existing_code = database.get_nfc_codes(g.connection, g.db_cursor, timestamp, code=code)
            if existing_code:
                database.update_nfc_code(g.connection, g.db_cursor, code=code, last_used=timestamp)

                if existing_code["email"]:
                    perform_unlock()
            else:
                database.add_nfc_code(g.connection, g.db_cursor, timestamp=timestamp, code=code.replace('"', ''))

            response = {"status": "OK"}
        else:
            response = {"status": "ERROR", "detail": "Missing code"}
    else:
        response = {"status": "ERROR", "detail": "Missing token"}

    return jsonify(response)


@application.route('/device_get_nfc_codes', methods=['GET'])
def device_get_nfc_codes():
    args = request.args
    token = args.get("token")

    if token:
        device = database.get_device(g.connection, g.db_cursor, token=token)
        if device:
            start_from = args.get("start")
            max_count = args.get("max")

            if start_from:
                start = int(start_from)
            else:
                start = 0

            if max_count:
                max = int(max_count)
            else:
                max = 10

            nfc_codes = database.get_nfc_codes(g.connection, g.db_cursor, start_id=start, max_num=max)
            codes = []
            if nfc_codes:
                for code in nfc_codes:
                    codes.append(code["code"])

            response = {"status": "OK", "codes": codes}
        else:
            response = {"status": "ERROR", "detail": "Unauthorized"}

    else:
        response = {"status": "ERROR", "detail": "Missing token"}

    return jsonify(response)


@application.route('/authorize_nfc_code', methods=['GET'])
def authorize_nfc_code():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        return redirect(url_for('login'))

    args = request.args
    code = args.get("code")

    return render_template('authorize_nfc_code.html', token=token, code=code)


@application.route('/authorize_nfc_code', methods=['POST'])
def authorize_nfc_code_post():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        return redirect(url_for('login'))

    code = request.form.get('code')
    print(f"**** code --{code}--")
    if code:

        alias = request.form.get('alias')
        if not alias or len(alias) < 3:
            return redirect(url_for('authorize_nfc_code', token=token, code=code))

        database.update_nfc_code(g.connection, g.db_cursor, code=code, email=user["email"], alias=alias)

        database.cleanup_unused_nfc_codes(g.connection, g.db_cursor)
    else:
        flash('Greška: neispravan NFC kod.')

    return redirect(url_for('index'))


@application.route('/delete_nfc_code', methods=['GET'])
def delete_nfc_code():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    user = database.get_user(g.connection, g.db_cursor, token=token)
    if not user:
        return redirect(url_for('login'))

    args = request.args
    code = args.get("code")
    if code:
        database.delete_nfc_code(g.connection, g.db_cursor, code=code)
    else:
        flash('Greška: neispravan NFC kod.')

    return redirect(url_for('index'))


