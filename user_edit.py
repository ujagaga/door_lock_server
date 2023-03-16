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

ROLE_ADMIN = "admin"
ROLE_GUEST = "guest"


def hash_password(plain_text_password: str) -> str:
    return sha256(plain_text_password.encode('utf-8')).hexdigest()


def init_database():
    if not os.path.isfile(database_file):
        # Database does not exist. Create one
        db = sqlite3.connect(database_file)

        sql = "create table users (email TEXT, password TEXT, token TEXT, role TEXT, valid_until INTEGER)"
        db.execute(sql)
        db.commit()
        db.close()

        if not os.path.isfile(database_file):
            sys.exit("ERROR: Failed to create the database")


def get_user_from_db(email: str = None) -> dict:
    data = None

    if email:
        sql = f"SELECT * FROM users WHERE email = '{email}'"
    else:
        sql = "SELECT * FROM users"

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


def delete_user(email: str):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(f"DELETE FROM users WHERE username = '{email}'")
    con.commit()
    con.close()


def write_new_user(password: str, email: str, role: str = ROLE_ADMIN, valid_until: int = -1):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users(password, email, token, role, valid_until) VALUES (?, ?, ?, ?, ?)",
        (hash_password(password), email, "", role, valid_until)
    )
    con.commit()
    con.close()


def modify_user(email: str, password: str = None, role: str = None):
    user = get_user_from_db(email=email)

    if not user:
        print('ERROR: No user found in dbd matching username: "{username}"')
        return

    if password:
        user["password"] = hash_password(password)
    if role:
        user["role"] = role

    sql = "UPDATE users SET password = '{}', role = '{}', WHERE email = '{}'" \
          "".format(user["password"], user["role"], user["email"])

    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    con.close()


def list_users(email: str = None):
    users = get_user_from_db(email=email)

    if len(users) == 0:
        message = "INFO: No users found in database"
        if email is not None:
            message += f" with email: {email}."
        else:
            message += "."

        print(message)
    else:
        message = "INFO: Listing users in database"
        if email is not None:
            message += f" with email: {email}"
        message += ":"

        print(message)
        for user in users:
            print("\t", user)


def validate_email(email: str):
    # Check if e-mail is valid
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, args.email):
        sys.exit(f"ERROR: Invalid e-mail: {email}")


def validate_password(password: str):
    if " " in args.password:
        sys.exit("ERROR: Password can not contain spaces.")
    if len(args.password) < 5:
        sys.exit("ERROR: Password can not be shorter than 5 characters.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--password", help="Password", required=False)
    parser.add_argument("-e", "--email", help="E-mail", required=False)
    parser.add_argument("-r", "--role", help="Access role", required=False, choices=[ROLE_ADMIN, ROLE_GUEST])
    parser.add_argument("-o", "--operation", help="Operation", required=True,
                        choices=['add', 'delete', 'modify', 'list'])

    args = parser.parse_args()

    if not os.path.isfile(database_file):
        init_database()

    if args.operation == 'list':
        list_users()

    elif args.operation == 'add':
        if not args.password or not args.email:
            sys.exit("ERROR: Please provide all parameters to create a new user (password and email)")

        # Check if user with same username exists
        users = get_user_from_db(email=args.email)
        if len(users) > 0:
            sys.exit(f"ERROR: User exists: {users[0]}")

        validate_email(args.email)

        validate_password(args.password)

        print(
            f"INFO: Creating a new user: "
            f"\n\temail:    {args.email}"
            f"\n\tpassword: {args.password}"            
            f"\n\trole:    {args.role}"
            )
        write_new_user(email=args.email, password=args.password, role=args.role)
        list_users(email=args.email)

    elif args.operation == 'delete':
        if not args.email:
            sys.exit("ERROR: Please provide email of the user to delete.")

        users = get_user_from_db(email=args.email)
        if len(users) > 0:
            print(f"INFO: Deleting user with email: {args.email}")
            delete_user(args.email)
        list_users(email=args.email)

    elif args.operation == 'modify':
        if not args.email:
            sys.exit("ERROR: Please provide email of the user to modify.")

        if not args.password and not args.role:
            sys.exit("ERROR: Please provide password, and/or role to modify.")

        if args.password:
            validate_password(args.password)
        elif args.email:
            validate_email(args.email)

        print(f"INFO: Modifying user: {args.email}")
        modify_user(email=args.email, password=args.password, role=args.role)

        list_users(email=args.email)
