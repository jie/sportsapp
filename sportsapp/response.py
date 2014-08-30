#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


from flask import jsonify


class AjaxResponse(object):

    def __init__(self, status=0, title='ok', message='', content=None):
        self.status = status
        self.title = title
        self.message = message
        self.content = content

    def make_response(self):
        return jsonify({
            'status': self.status,
            'title': self.title,
            'message': self.message,
            'content': self.content
        })
