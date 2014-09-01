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
import error
import utils
from uuid import uuid4
from flask.ext.babel import Babel
from models import db, User, Note, NoteKind
from oauth_adapter import OauthAdapter
from logging.handlers import TimedRotatingFileHandler

DEFAULT_FETCH_COUNT = 5

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

app.json_encoder = utils.MyJsonEncoder

# init logger
logHandler = TimedRotatingFileHandler(
    app.config['LOGGER_NAME'], when='D')
logHandler.setLevel(logging.INFO)
app.logger.addHandler(logHandler)


def account_signin(user_id):
    """ Create token and user_id in session
    """

    token = uuid4().get_hex()
    flask.session['user_id'] = user_id
    flask.session['token'] = token
    return {'pk': user_id, 'token': token}


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
    user.save()
    account_signin(user.pk)
    response = flask.make_response(flask.redirect(flask.url_for('index')))
    return response


@app.route('/accounts/signup')
def signup():
    return flask.render_template('signup.html')


@app.route('/api/accounts/signin', methods=['POST'])
@utils.json_response
def signin_api():
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')

    user = User.fetchone(email=email)
    if not user:
        raise error.UserNotExist()

    if user.password != utils.hash_password(password):
        raise error.UserPasswordError()

    return account_signin(user.pk)


@app.route('/api/accounts/signup', methods=['POST'])
@utils.json_response
def signup_api():
    email = flask.request.form.get('email')
    nickname = flask.request.form.get('nickname')
    password = flask.request.form.get('password')
    repeat_password = flask.request.form.get('repeat_password')

    if password != repeat_password:
        raise error.RepeatPasswordError()

    user = User.fetchone(email=email)
    if user:
        raise error.UserEmailRegisted()

    user = User.fetchone(nickname=nickname)
    if user:
        raise error.UserNicknameRegisted()

    user = User()
    user.email = email
    user.nickname = nickname
    user.password = utils.hash_password(password)
    user.save()
    return account_signin(user.pk)


@app.route('/note/<int:pk>')
@utils.login_required
def note_detail(pk):
    note = Note.fetchone(pk=pk)
    if not note:
        raise error.NoteNotExist()
    return flask.render_template('note_detail.html', {'note': note})


@app.route('/api/note/fetch/<int:pk>', methods=['POST'])
@utils.json_response
@utils.login_required
def fetch_notes(pk):
    count = flask.request.form.get('count', DEFAULT_FETCH_COUNT)
    notes = Note.fetchmany(
        count,
        order=Note.id.desc(),
        user_id=flask.session['user_id']
    )
    notes = notes.filter(Note.id > pk)
    return notes


@app.route('/kind/create')
def create_kind():
    return flask.render_template('kind_create.html')


@app.route('/note/create/<int:pk>')
def create_note(pk):
    return flask.render_template('note_create.html')


@app.route('/api/kind/create', methods=['POST'])
@utils.json_response
@utils.login_required
def create_kind_api():
    name = flask.request.form.get('name')
    note_kind = NoteKind()
    note_kind.name = name
    note_kind.user_id = flask.session['user_id']
    note_kind.save()
    return {'pk': note_kind.pk}


@app.route('/api/note/create', methods=['POST'])
@utils.json_response
@utils.login_required
def create_note_api():
    kind_id = flask.request.args.get('pk')
    user_id = int(flask.session['user_id'])

    # Check kind owner
    NoteKind.checkUser(kind_id, user_id)
    quantity = flask.request.args.get('quantity')
    content = flask.request.args.get('content')
    note = Note()
    note.kind_id = kind_id
    note.user_id = user_id
    note.content = content
    note.quantity = quantity
    note.save()
    return {'pk': note.pk}


@app.route('/api/kinds')
@utils.json_response
@utils.login_required
def get_kind():
    user_id = int(flask.session['user_id'])
    records = NoteKind.fetchall(user_id=user_id)
    return {'kinds': records}


if __name__ == "__main__":
    from docopt import docopt
    ARGS = docopt(__doc__, version='0.0.1')
    app.run("0.0.0.0", port=int(ARGS['--port']), debug=True)
