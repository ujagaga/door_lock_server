# Door lock server
Python Flask server with user login and generating temporary url.
This server is intended for controlling a WiFi enabled door lock at a guesthouse. 
Besides a web UI, there is an MQTT client, so WiFi enabled embedded devices can connect to a server and receive commands.

NOTE: this version uses sqlite database and is simpler for local development, but on hosting it does not perform well, 
so there is also branch "lt19mysql" which uses MySql and works better. It is intended for use at a specific address, 
so you should go through HTML and adjust.

## Installing dependencies

    pip install flask requests flask_mail mysql-connector-python paho-mqtt

## Preparing and using
To enable e-mail sending in case you lose your password, create a settings.py file like the settings.py.example attached here.
If you wish to use G-mail to send emails, you will need to set up an App password 
(https://support.google.com/accounts/answer/185833?hl=en).

Before you run the app, you should create an admin user:

    ./user_edit.py -o add -e some_address@email.com -p admin123

I am using a free public mqtt server, so the security is not very high. If you wish more security, use a mqtt server 
where you can set credentials. Devices connected to the MQTT server also have an account in my database, so create them:

    ./device_edit.py -o add -n device_name -p dev_pass

These credentials will be used by the device to login to page at:

    http://<your_server_tld>/device_login&name=<device_name>&password=<dev_pass>

The server will respond with a json array similar to:
{
  "status": "OK",
  "timeout": 120,
  "lifesign": "443b25b1997e50514db23a2b7a6d8279b3e3334cff22ae5d1afc429e41dd4213",  
  "token": "awWuxjqCMTWruhGPdPaacArEcPPMppoA",
  "topic": "80e5043888b6d6794f4e7380a33f58432739df84999b8f626dac49d891c96309",
  "trigger": "f6c0f5f9c1e862377a1a76fd21d911fc0a308014dffc9f1daa1032d0fc1a1cff"
}

Every time a device logs in, this data changes, so the device can initiate change in topic and data it will respond to.
This is to enable simple change in topic in case the topic is already used by some other device. All you need to do 
is make your device login when ever it receives an unexpected string.

The timeout is the number of seconds after which the device should ping the server. If the device does not ping 
the server for too long, it will be considered unconnected and displayed on the webpage.

Your device can ping the server at:

    http://<your_server_tld>/device_ping&token=<device_token>

This will cause the server to send the lifesign string to all connected devices via MQTT.
If the device gets the lifesign string via MQTT, it should make an http GET request to:

    http://<your_server_tld>/device_lifesign_confirm&token=<device_token>

The server will then mark the device as online.

When you click the unlock button, the server will send the trigger string to all devices via MQTT.

## Run locally
    export FLASK_APP=passenger_wsgi.py
    export FLASK_DEBUG=True
    flask run
    
## Change history

22.03.2023. Finished hardware code for ESP8266.
TODO: add language support.

18.03.2023. Adding temporary link generating.

17.03.2023. Functional app with user login, password recovery, device login and MQTT communication.
TODO: add generating temporary unlock string for guests.
TODO: add language support.

15.03.2023. Just starting. Not yet functional app. 
