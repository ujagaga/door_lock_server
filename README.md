# Door lock server
Python Flask server with user login and generating temporary url.
This server is intended for controlling a WiFi enabled door lock at a guesthouse. 
Besides a web UI, there is a websocket server so WiFi enabled embedded devices can connect and receive commands.

## Installing dependencies
	pip install flask flask-sqlalchemy requests flask_mqtt flask_mail

## Preparing
Before you run the app, you should create an admin user:

    ./user_edit.py -o add -u admin -e some_address@email.com -p admin123 -r admin 

I am using a free public mqtt server, so the security is not very high. If you wish more security, use a mqtt server 
where you can set credentials. For my project, I will use a random topic to add to security. This is good enough for me:

    ./mqtt_topic.py

This script will create a file "mqtt_topic.cfg" where you can find the topic to which will be posted, 
so you can use it for your device.

## Run locally
    export FLASK_APP=passenger_wsgi.py
    export FLASK_DEBUG=True
    flask run
    
## Change history

15.03.2023. Just starting. Not yet functional app. 