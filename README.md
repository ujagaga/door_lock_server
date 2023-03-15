# Door lock server
Python Flask server with user login and generating temporary url.
This server is intended for controlling a WiFi enabled door lock at a guesthouse. 
Besides a web UI, there is a websocket server so WiFi enabled embedded devices can connect and receive commands.

## Installing dependencies
	pip install flask flask-sqlalchemy requests

## Run locally

    export FLASK_APP=passenger_wsgi.py
    export FLASK_ENV=development
    flask run
    
## Change history

15.03.2023. Just starting. Not yet functional app. 