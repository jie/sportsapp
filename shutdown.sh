#!/bin/sh
pkill -f '/usr/bin/python /usr/local/bin/gunicorn -w 4 -b 127.0.0.1:5001 --log-config /usr/webapps/python/sportsapp/logging.conf -D app:app'