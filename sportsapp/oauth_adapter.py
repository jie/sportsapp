#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang

"""
An oauth2 client library using requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using exist client:

1. Provide OAUTH2_CONFIG config map:

    OAUTH2_CONFIG = {
        'github': {
            'name': 'github',
            'client': 'GithubOauthClient', # client is the client class name
            'params': {
                'key': 'xxxxx',
                'secret': 'xxxxx-xxxxx-xxxxx',
                'endpoint': 'https://api.github.com/',
                'authorize_url': 'https://github.com/login/oauth/authorize',
                'access_token_url': 'https://github.com/login/oauth/access_token',
                'scope': 'user'
            },
            'callback': 'http://you_callback_url',
            'api': {
                'userinfo': 'user'
            }
        },
    }

2. Write an redirect handler for oauth2 server. Example for flask:

    @account_app.route('/oauth2/signin/<string:oauth_port>')
    def oauth2_signin(oauth_port):
        oauth_adapter = OauthAdapter(oauth_port, OAUTH2_CONFIG)
        return redirect(oauth_adapter.client.get_authrize_url())

3. Write an callback handler for oauth2 server. Example for flask:

    @account_app.route('/oauth2/callback/<string:oauth_port>')
    def oauth2_code_callback(oauth_port):
        code = request.args.get('code')
        oauth_adapter = OauthAdapter(oauth_port, OAUTH2_CONFIG)
        oauth_adapter.client.get_access_token(code)
        userinfo = oauth_adapter.client.get_userinfo()
        do_something_with_userinfo(userinfo)

"""


import random
import requests
from urllib import urlencode
from urlparse import parse_qs


class AbstractOauthClient(object):

    def __init__(self, oauth_config):
        self.oauth_config = oauth_config
        self.key = oauth_config['params']['key']
        self.secret = oauth_config['params']['secret']
        self.scope = oauth_config['params']['scope']
        self.endpoint = oauth_config['params']['endpoint']
        self.authorize_url = oauth_config['params']['authorize_url']
        self.access_token_url = oauth_config['params']['access_token_url']
        self.openid_url = oauth_config['params'].get('openid_url')

    def get_random_state(self):
        return str(random.randint(1, 100000))

    def get_redirect_uri(self, uri, payload):
        return "{uri}?{params}".format(uri=uri, params=urlencode(payload))

    def get_api_uri(self, api):
        return "{endpoint}{api}".format(endpoint=self.endpoint, api=api)

    def get_resource(self, api, params=None, headers=None):
        api_uri = self.get_api_uri(api)
        return requests.get(api_uri, params=params, headers=headers)

    def parse_access_token(self, response):
        raise Exception(
            'Must IMPL the method to deal with requests access_token response')

    def get_authrize_url(self):
        raise Exception(
            'Must IMPL the method to get authorize_url')

    def get_access_token(self, code, **kwargs):
        raise Exception(
            'Must IMPL the method to get access_token')

    def get_userinfo(self):
        raise Exception(
            'Must IMPL the method to get userinfo')


class QQOauthClient(AbstractOauthClient):

    def get_authrize_url(self):
        payload = {
            'response_type': 'code',
            'client_id': self.key,
            'redirect_uri': self.oauth_config['callback'],
            'scope': self.scope,
            'state': self.get_random_state()
        }
        return self.get_redirect_uri(self.authorize_url, payload)

    def get_access_token(self, code, **kwargs):
        payload = {
            'code': code,
            'client_id': self.key,
            'client_secret': self.secret,
            'redirect_uri': self.oauth_config['callback'],
            'grant_type': 'authorization_code',
        }
        res = requests.get(self.access_token_url, params=payload)
        self.parse_access_token(res)

    def get_userinfo(self):
        payload = {
            'oauth_consumer_key': self.key,
            'access_token': self.access_token,
            'openid': self.openid
        }
        response = self.get_resource(
            self.oauth_config['api']['userinfo'], payload)
        res = response.json()
        userinfo = {}
        userinfo['nickname'] = res['nickname']
        userinfo['oauth_id'] = self.openid
        userinfo['oauth_type'] = self.oauth_config['name']
        userinfo['avatar'] = res.get('figureurl_2') or res.get('figureurl_qq_2')
        return userinfo

    def parse_access_token(self, response):
        res_map = parse_qs(response.text, keep_blank_values=False)
        self.access_token = res_map['access_token'][0]
        self.get_openid()

    def get_openid(self):
        response = requests.get(self.openid_url, params=dict(access_token=self.access_token))
        res_map = parse_qs(response.text, keep_blank_values=False)
        self.openid = res_map['openid'][0]


class GithubOauthClient(AbstractOauthClient):

    def get_authrize_url(self):
        payload = {
            'client_id': self.key,
            'redirect_uri': self.oauth_config['callback'],
            'scope': self.scope,
            'state': self.get_random_state()
        }
        return self.get_redirect_uri(self.authorize_url, payload)

    def get_access_token(self, code, **kwargs):
        payload = {
            'code': code,
            'client_id': self.key,
            'client_secret': self.secret,
            'redirect_uri': self.oauth_config['callback']
        }
        res = requests.post(self.access_token_url, payload)
        self.parse_access_token(res)

    def get_userinfo(self):
        payload = {
            'client_id': self.key,
            'client_secret': self.secret,
            'access_token': self.access_token
        }
        response = self.get_resource(
            self.oauth_config['api']['userinfo'], payload)
        res = response.json()
        userinfo = {}
        userinfo['nickname'] = res['login']
        userinfo['oauth_id'] = res['id']
        userinfo['oauth_type'] = self.oauth_config['name']
        userinfo['email'] = res['email']
        userinfo['homepage'] = res['blog'] or res['home_url']
        userinfo['avatar'] = res['avatar_url']
        return userinfo

    def parse_access_token(self, response):
        res_map = parse_qs(response.text, keep_blank_values=False)
        self.access_token = res_map['access_token'][0]


class DoubanOauthClient(AbstractOauthClient):

    def get_authrize_url(self):
        payload = {
            'client_id': self.key,
            'redirect_uri': self.oauth_config['callback'],
            'scope': self.scope,
            'state': self.get_random_state(),
            'response_type': 'code'
        }
        return self.get_redirect_uri(self.authorize_url, payload)

    def get_access_token(self, code, **kwargs):
        payload = {
            'code': code,
            'client_id': self.key,
            'client_secret': self.secret,
            'redirect_uri': self.oauth_config['callback'],
            'grant_type': 'authorization_code',
        }
        res = requests.post(self.access_token_url, payload)
        self.parse_access_token(res)

    def get_userinfo(self):
        response = self.get_resource(
            self.oauth_config['api']['userinfo'],
            params=None,
            headers={'Authorization': 'Bearer {access_token}'.format(
                access_token=self.access_token)}
        )
        res = response.json()
        userinfo = {}
        userinfo['nickname'] = res['name']
        userinfo['oauth_id'] = self.openid
        userinfo['oauth_type'] = self.oauth_config['name']
        userinfo['avatar'] = res['large_avatar']
        userinfo['homepage'] = res['alt']
        return userinfo

    def parse_access_token(self, response):
        res = response.json()
        self.access_token = res['access_token']
        self.openid = res['douban_user_id']


class WeiboOauthClient(AbstractOauthClient):

    def get_authrize_url(self):
        payload = {
            'client_id': self.key,
            'redirect_uri': self.oauth_config['callback'],
            'scope': self.scope,
            'state': self.get_random_state(),
            'response_type': 'code'
        }
        return self.get_redirect_uri(self.authorize_url, payload)

    def get_access_token(self, code, **kwargs):
        payload = {
            'code': code,
            'client_id': self.key,
            'client_secret': self.secret,
            'redirect_uri': self.oauth_config['callback'],
            'grant_type': 'authorization_code',
        }
        res = requests.post(self.access_token_url, payload)
        self.parse_access_token(res)

    def get_userinfo(self):
        payload = {
            'uid': self.openid,
            'access_token': self.access_token
        }
        response = self.get_resource(
            self.oauth_config['api']['userinfo'],
            params=payload,
        )
        res = response.json()
        userinfo = {}
        userinfo['nickname'] = res['screen_name']
        userinfo['oauth_id'] = self.openid
        userinfo['oauth_type'] = self.oauth_config['name']
        userinfo['avatar'] = res['profile_image_url']
        userinfo['homepage'] = res['url']
        return userinfo

    def parse_access_token(self, response):
        res = response.json()
        self.access_token = res['access_token']
        self.openid = res['uid']


class OauthAdapter(object):

    OAUTH2_CLIENTS_MAP = {
        'GithubOauthClient': GithubOauthClient,
        'QQOauthClient': QQOauthClient,
        'DoubanOauthClient': DoubanOauthClient,
        'WeiboOauthClient': WeiboOauthClient
    }

    @staticmethod
    def LoadOauth2Clients(cls, **kwargs):
        cls.OAUTH2_CLIENTS_MAP.update(**kwargs)

    def __init__(self, oauth_port, oauth_config, is_mock=True):
        self.oauth_port = oauth_port
        self.oauth_config = oauth_config
        self.is_mock = is_mock
        self.get_oauth_client()

    def get_oauth_client(self):
        client_kw = self.oauth_config[self.oauth_port]
        self.client = self.OAUTH2_CLIENTS_MAP[client_kw['client']](client_kw)
