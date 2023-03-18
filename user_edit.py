#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import database
import helper


def list_users(db_obj, email: str = None):
    users = database.get_user(db=db_obj, email=email)
    message = "INFO: Listing users in database"

    if email:
        print(f'{message} with e-mail "{email}":')
        if users:
            print("\t", users)
        else:
            print("\tINFO: No user found with specified e-mail!")
    else:
        print(f'{message}:')
        if len(users) == 0:
            print("\tINFO: No users found in database.")
        else:
            for user_obj in users:
                print("\t", user_obj)


def validate_email(email: str):
    if not helper.validate_email(email):
        sys.exit(f"ERROR: Invalid e-mail: {email}")


def validate_password(password: str):
    ret_val = helper.validate_password(password)
    if ret_val == 1:
        sys.exit("ERROR: Password can not contain spaces.")
    elif ret_val == 2:
        sys.exit("ERROR: Password can not be shorter than 5 characters.")
    else:
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--password", help="Password", required=False)
    parser.add_argument("-e", "--email", help="E-mail", required=False)
    parser.add_argument("-o", "--operation", help="Operation", required=True,
                        choices=['add', 'delete', 'modify', 'list'])

    args = parser.parse_args()

    db = database.open_db()

    if args.operation == 'list':
        list_users(db_obj=db)

    elif args.operation == 'add':
        if not args.password or not args.email:
            sys.exit("ERROR: Please provide both password and email to create a new user")

        # Check if user with same username exists
        user = database.get_user(db=db, email=args.email)
        if user:
            sys.exit(f"ERROR: User exists: {user}")

        validate_email(args.email)

        validate_password(args.password)

        print(
            f"INFO: Creating a new user: "
            f"\n\temail:    {args.email}"
            f"\n\tpassword: {args.password}"            
            )

        database.add_user(db=db, email=args.email, password=helper.hash_password(args.password))
        print("Checking result:")
        list_users(db_obj=db, email=args.email)

    elif args.operation == 'delete':
        if not args.email:
            sys.exit("ERROR: Please provide email of the user to delete.")

        print(f"INFO: Deleting user with email: {args.email}")
        database.delete_user(db=db, email=args.email)

        print("Checking result:")
        list_users(db_obj=db, email=args.email)

    elif args.operation == 'modify':
        if not args.email:
            sys.exit("ERROR: Please provide email of the user to modify.")

        if not args.password:
            sys.exit("ERROR: Please provide password to set.")

        validate_password(args.password)

        print(f"INFO: Modifying user: {args.email}")
        database.update_user(db=db, email=args.email, password=helper.hash_password(args.password))

        print("Checking result:")
        list_users(db_obj=db, email=args.email)

    database.close_db(db)
