#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


"""
Usage:
    app.py [--port=<port>]

Options:
    --port=<port>         default server port [default: 5000]
"""


import flask
import logging
from flask.ext.babel import Babel
from models import db, User
from datetime import datetime
from uuid import uuid4
from docopt import docopt
from oauth_adapter import OauthAdapter
from logging.handlers import TimedRotatingFileHandler

ARGS = docopt(__doc__, version='0.0.1')

app = flask.Flask(__name__)

app.config.from_pyfile('config.py')

app.static_folder = app.config['STATIC_PATH']
app.template_folder = app.config['TEMPLATE_PATH']
app.root_path = app.config['BASE_DIR']

db.init_app(app)

# init babel
babel = Babel()
babel.init_app(app)
print babel.list_translations()

# init logger
logHandler = TimedRotatingFileHandler(
    app.config['LOGGER_NAME'], when='D')
logHandler.setLevel(logging.INFO)
app.logger.addHandler(logHandler)


@babel.localeselector
def get_locale():
    user = getattr(flask.g, 'user', None)
    if user is not None:
        return getattr(user, 'locale', 'zh')
    accept_languages = app.config.get('ACCEPT_LANGUAGES', ['zh'])
    return flask.request.accept_languages.best_match(accept_languages)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/about')
def about():
    return flask.render_template('about.html')


@app.route('/services')
def services():
    return flask.render_template('services.html')


@app.route('/account/oauth2/signin/<string:oauth_port>')
def oauth2_signin(oauth_port):
    oauth_adapter = OauthAdapter(
        oauth_port, flask.current_app.config['OAUTH2_CONFIG'])
    return flask.redirect(oauth_adapter.client.get_authrize_url())


@app.route('/account/oauth2/callback/<string:oauth_port>')
def oauth2_code_callback(oauth_port):
    code = flask.request.args.get('code')
    oauth_adapter = OauthAdapter(
        oauth_port, flask.current_app.config['OAUTH2_CONFIG'])
    oauth_adapter.client.get_access_token(code)
    userinfo = oauth_adapter.client.get_userinfo()

    user = User.fetchone(
        oauth_id=userinfo['oauth_id'],
        oauth_type=userinfo['oauth_type']
    )

    if not user:
        user = User()

    user.nickname = userinfo['nickname']
    user.avatar = userinfo['avatar']
    user.oauth_id = userinfo['oauth_id']
    user.oauth_type = userinfo['oauth_type']
    user.update_at = datetime.now()
    user.save()

    session_token = uuid4().get_hex()
    flask.session['session-token'] = session_token
    response = flask.make_response(flask.redirect(flask.url_for('index')))
    response.set_cookie('session-token', session_token)
    return response


@app.route('/api/accounts/signin', methods=['POST'])
def signin():
    # username = flask.request.form.get('username')
    # password = flask.request.form.get('password')
    return flask.jsonify({'status': 0, 'message': 'ok', 'sessionid': '123456'})


@app.route('/note/<int:pk>')
def note_detail(pk):
    context = {
        'title': 'my exerise',
        'content': "element in Ajax loaded page, so we don't need here full HTML layout, just the page.",
        'create_at': '2014-08-28',
        'pk': pk
    }
    return flask.render_template('note_detail.html', **context)


@app.route('/note/kind/create')
def create_note_kind():
    context = {}
    return flask.render_template('note_kind_create.html', **context)


@app.route('/note/create/<int:pk>')
def create_note(pk):
    context = {}
    return flask.render_template('note_create.html', **context)


if __name__ == "__main__":
    app.run("0.0.0.0", port=int(ARGS['--port']), debug=True)
