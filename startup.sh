cd sportsapp
gunicorn -w 4 -b 127.0.0.1:5001 --log-config /usr/webapps/python/sportsapp/logging.conf app:app &