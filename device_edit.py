#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import database
import helper


def list_devices(name: str = None):
    devices = database.get_device(name=name)

    message = "INFO: Listing devices in database"

    if name:
        print(f'{message} with name "{name}":')
        if devices:
            print("\t", devices)
        else:
            print("\tINFO: No device found with specified name!")
    else:
        print(f'{message}:')
        if len(devices) == 0:
            print("\tINFO: No devices found in database.")
        else:
            for device_obj in devices:
                print("\t", device_obj)


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
    parser.add_argument("-n", "--name", help="Device name", required=False)
    parser.add_argument("-o", "--operation", help="Operation", required=True,
                        choices=['add', 'delete', 'modify', 'list'])

    args = parser.parse_args()

    db = database.open_db()
    if not database.check_table_exists("devices"):
        database.init_database()

    if args.operation == 'list':
        list_devices()

    elif args.operation == 'add':
        if not args.password or not args.name:
            sys.exit("ERROR: Please provide both name and password to create a new device")

        device = database.get_device(name=args.name)
        if device:
            sys.exit(f"ERROR: Device exists: {device}")

        validate_password(args.password)

        print(
            f"INFO: Creating a new device: "
            f"\n\tname:    {args.name}"
            f"\n\tpassword: {args.password}"            
            )
        database.add_device(name=args.name, password=helper.hash_password(args.password))

        print("Checking result:")
        list_devices(name=args.name)

    elif args.operation == 'delete':
        if not args.name:
            sys.exit("ERROR: Please provide name of the device to delete.")

        print(f"INFO: Deleting device with name: {args.name}")
        database.delete_device(name=args.name)

        print("Checking result:")
        list_devices(name=args.name)

    elif args.operation == 'modify':
        if not args.name:
            sys.exit("ERROR: Please provide name of the device to modify.")

        if args.password:
            validate_password(args.password)
        else:
            sys.exit("ERROR: Please provide password to set.")

        print(f"INFO: Modifying device: {args.name}")
        database.update_device(name=args.name, password=helper.hash_password(args.password))

        print("Checking result:")
        list_devices(name=args.name)

    database.close_db()
