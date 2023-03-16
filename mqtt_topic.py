#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate a random MQTT topic to be used to send command to device.
"""

import os
from hashlib import sha256
import random
import string


current_path = os.path.dirname(os.path.realpath(__file__))
topic_file = os.path.join(current_path, "mqtt_topic.cfg")


def generate_topic():
    random_string = ''.join(random.choices(string.ascii_letters, k=32))
    return sha256(random_string.encode('utf-8')).hexdigest()


topic = generate_topic()
with open(topic_file, "w") as file:
    file.write(topic)

