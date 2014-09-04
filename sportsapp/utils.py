#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


import error
from hashlib import sha1
from flask import jsonify, session, request
from flask.json import JSONEncoder
from datetime import datetime
from const import ResponseStatus
from functools import wraps
from models import ModelBase


class MyJsonEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, ModelBase):
                return obj.to_dict()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def hash_password(password):
    return sha1(password).hexdigest()


class AjaxResponse(object):

    def __init__(self, status=0, title='ok', message=None, content=None):
        self.status = status
        self.title = title
        self.message = message if message else ResponseStatus[status]['message']
        self.content = content

    def make_response(self):
        return jsonify({
            'status': self.status,
            'title': self.title,
            'message': self.message,
            'content': self.content
        })


def json_response(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        response = AjaxResponse()
        try:
            response.content = func(*args, **kwargs)
        except error.Error, e:
            response.status = e.STATUS_CODE
            response.title = ResponseStatus[e.STATUS_CODE]['title']
            response.message = ResponseStatus[e.STATUS_CODE]['message']
        except Exception, e:
            response.status = -1
            response.title = 'unknown exception'
            response.message = e.message
        response_json = response.make_response()
        return response_json

    return decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('session_token')
        if 'token' not in session.keys() or session['token'] != token:
            raise error.LoginRequiredError()
        return f(*args, **kwargs)
    return decorated_function
