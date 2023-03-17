#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from hashlib import sha256
import sqlite3
import re
import os

current_path = os.path.dirname(os.path.realpath(__file__))
database_file = os.path.join(current_path, "database.db")


def hash_password(plain_text_password: str) -> str:
    return sha256(plain_text_password.encode('utf-8')).hexdigest()


def init_database():
    if not os.path.isfile(database_file):
        # Database does not exist. Create one
        db = sqlite3.connect(database_file)

        sql = "create table users (email TEXT, password TEXT, token TEXT, role TEXT, valid_until INTEGER)"
        db.execute(sql)
        db.commit()

        sql = "create table devices (name TEXT, password TEXT, data TEXT, token TEXT)"
        db.execute(sql)
        db.commit()

        db.close()

        if not os.path.isfile(database_file):
            sys.exit("ERROR: Failed to create the database")


def get_device_from_db(name: str = None) -> dict:
    data = None

    if name:
        sql = f"SELECT * FROM devices WHERE name = '{name}'"
    else:
        sql = "SELECT * FROM devices"

    try:
        con = sqlite3.connect(database_file)
        cur = con.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        con.close()

        return data
    except Exception as exc:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"ERROR reading data on line {exc_tb.tb_lineno}!\n\t{exc}", flush=True)

    return data


def delete_device(name: str):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(f"DELETE FROM devices WHERE name = '{name}'")
    con.commit()
    con.close()


def write_new_device(name: str, password: str):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO devices(name, password, data, token) VALUES (?, ?, ?, ?)",
        (name, hash_password(password), "", "")
    )
    con.commit()
    con.close()


def modify_device(name: str, password: str):
    device = get_device_from_db(name=name)

    if not device:
        print('ERROR: No device found in db matching name: "{name}"')
        return

    sql = "UPDATE devices SET password = '{}' WHERE name = '{}'".format(name, hash_password(password))

    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()


def list_devices(name: str = None):
    devices = get_device_from_db(name=name)

    if len(devices) == 0:
        message = "INFO: No devices found in database"
        if name is not None:
            message += f" with name: {name}."
        else:
            message += "."

        print(message)
    else:
        message = "INFO: Listing devices in database"
        if name is not None:
            message += f" with name: {name}"
        message += ":"

        print(message)
        for device in devices:
            print("\t", device)


def validate_password(password: str):
    if " " in args.password:
        sys.exit("ERROR: Password can not contain spaces.")
    if len(args.password) < 5:
        sys.exit("ERROR: Password can not be shorter than 5 characters.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--password", help="Password", required=False)
    parser.add_argument("-n", "--name", help="Device name", required=False)
    parser.add_argument("-o", "--operation", help="Operation", required=True,
                        choices=['add', 'delete', 'modify', 'list'])

    args = parser.parse_args()

    if not os.path.isfile(database_file):
        init_database()

    if args.operation == 'list':
        list_devices()

    elif args.operation == 'add':
        if not args.password or not args.name:
            sys.exit("ERROR: Please provide both name and password to create a new device")

        devices = get_device_from_db(name=args.name)
        if len(devices) > 0:
            sys.exit(f"ERROR: Device exists: {device[0]}")

        validate_password(args.password)

        print(
            f"INFO: Creating a new device: "
            f"\n\temail:    {args.name}"
            f"\n\tpassword: {args.password}"            
            )
        write_new_device(name=args.name, password=args.password)
        list_devices(name=args.name)

    elif args.operation == 'delete':
        if not args.name:
            sys.exit("ERROR: Please provide name of the device to delete.")

        devices = get_device_from_db(name=args.name)
        if len(devices) > 0:
            print(f"INFO: Deleting device with name: {args.name}")
            delete_device(args.name)
        list_devices(name=args.name)

    elif args.operation == 'modify':
        if not args.name:
            sys.exit("ERROR: Please provide name of the device to modify.")

        if args.password:
            validate_password(args.password)
        else:
            sys.exit("ERROR: Please provide password to modify.")

        print(f"INFO: Modifying device: {args.name}")
        modify_device(name=args.name, password=args.password)

        list_devices(name=args.name)
