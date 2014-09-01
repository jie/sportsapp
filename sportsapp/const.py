#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


ResponseStatus = {
    0: {
        'title': 'ok',
        'message': 'request fulfill'
    },

    -1: {
        'title': 'unknown exception',
        'message': 'unknown exception'
    },

    -2: {
        'title': 'session expired',
        'message': 'session has expired, please re-login'
    },

    -11: {
        'title': 'user not exist',
        'message': 'user not exist'
    },

    -12: {
        'title': 'user password error',
        'message': 'password check fail'
    },

    -13: {
        'title': 'repeat password error',
        'message': 'repeat password error'
    },

    -14: {
        'title': 'user email has registed',
        'message': 'user email has registed'
    },

    -15: {
        'title': 'user nickname has registed',
        'message': 'user nickname has registed'
    },

    -21: {
        'title': 'note not exist',
        'message': 'request note not found'
    }
}