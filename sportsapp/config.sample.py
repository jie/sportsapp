#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang

import os

DEBUG = True

SECRET_KEY = '123456'

BASE_DIR = ''
BOWER_PATH = ""

LOGGER_NAME = 'sportsapp.log'
STATIC_PATH = os.path.join(BASE_DIR, 'static')
TEMPLATE_PATH = os.path.join(BASE_DIR, 'template')


# Redis session
REDIS = {
    'db': 0,
    'host': '127.0.0.1',
    'port': 6379,
    'timeout': 8,
}

SESSION_PREFIX = "sportsapp:sid:"

# Flask-sqlalchemy
SQLALCHEMY_DATABASE_URI = 'mysql://sportsapp:sportsapp@127.0.0.1/sportsapp'

# Recaptcha
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

# Flask-babel
BABEL_DEFAULT_LOCALE = 'zh_CN'
BABEL_DEFAULT_TIMEZONE = 'Asia/ShangHai'


# Flask-oauthlib
OAUTH2_CONFIG = {
    'github': {
        'name': 'github',
        'client': 'GithubOauthClient',
        'params': {
            'key': '',
            'secret': '',
            'endpoint': 'https://api.github.com/',
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'scope': 'user'
        },
        'callback': '/account/oauth2/callback/github',
        'api': {
            'userinfo': 'user'
        }
    },
}
