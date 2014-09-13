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
import error
import utils
from uuid import uuid4
from datetime import datetime, timedelta
from flask.ext.babel import Babel
from models import db, User, Note, NoteKind, Dairy
from oauth_adapter import OauthAdapter

DEFAULT_FETCH_COUNT = 10

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


@babel.localeselector
def get_locale():
    user = getattr(flask.g, 'user', None)
    if user is not None:
        return getattr(user, 'locale', 'zh_Hans_CN')
    accept_languages = app.config.get('ACCEPT_LANGUAGES', ['zh_Hans_CN'])
    return flask.request.accept_languages.best_match(accept_languages)

app.json_encoder = utils.MyJsonEncoder


def account_signin(user_id):
    """ Create token and user_id in session
    """

    token = uuid4().get_hex()
    flask.session['user_id'] = user_id
    flask.session['token'] = token
    return {'pk': user_id, 'token': token}


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
        user.oauth_id = userinfo['oauth_id']
        user.oauth_type = userinfo['oauth_type']

    user.nickname = userinfo['nickname']
    user.avatar = userinfo['avatar']
    user.oauth_id = userinfo['oauth_id']
    user.oauth_type = userinfo['oauth_type']
    user.save()
    session_token = account_signin(user.pk)
    response = flask.make_response(flask.redirect(flask.url_for('index')))
    response.set_cookie('session_token', session_token['token'])
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


# @app.route('/api/accounts/signup', methods=['POST'])
# @utils.json_response
# def signup_api():
#     email = flask.request.form.get('email')
#     nickname = flask.request.form.get('nickname')
#     password = flask.request.form.get('password')
#     repeat_password = flask.request.form.get('repeat_password')

#     if password != repeat_password:
#         raise error.RepeatPasswordError()

#     user = User.fetchone(email=email)
#     if user:
#         raise error.UserEmailRegisted()

#     user = User.fetchone(nickname=nickname)
#     if user:
#         raise error.UserNicknameRegisted()

#     user = User()
#     user.email = email
#     user.nickname = nickname
#     user.password = utils.hash_password(password)
#     user.save()
#     return account_signin(user.pk)


@app.route('/note/<int:pk>')
@utils.login_required
def note_detail(pk):
    note = Note.fetchone(pk=pk)
    if not note:
        raise error.NoteNotExist()
    return flask.render_template('note_detail.html', **{'note': note})


@app.route('/kind/create')
def create_kind():
    return flask.render_template('kind_create.html')


@app.route('/note/create/<int:pk>')
@utils.login_required
def create_note(pk):
    note_kind = NoteKind.fetchone(pk=pk, user_id=flask.session['user_id'])
    if not note_kind:
        raise error.KindNoteExistError()
    return flask.render_template('note_create.html', kind=note_kind)


@app.route('/dairy/create')
def create_dairy():
    return flask.render_template('dairy_create.html')


@app.route('/api/user/info', methods=['GET'])
@utils.json_response
# @utils.login_required
def get_userinfo_api():
    user_id = flask.session['user_id']
    userinfo = User.fetchone(pk=user_id)
    return userinfo


@app.route('/api/dairy/create', methods=['POST'])
@utils.json_response
@utils.login_required
def create_dairy_api():
    title = flask.request.form.get('title')
    content = flask.request.form.get('content')
    user_id = flask.session['user_id']
    record = Dairy()
    record.title = title
    record.content = content
    record.user_id = user_id
    record.save()
    return {'pk': record.pk}


@app.route('/api/kind/create', methods=['POST'])
@utils.json_response
@utils.login_required
def create_kind_api():
    name = flask.request.form.get('name')
    user_id = flask.session['user_id']
    note_kind = NoteKind.fetchone(name=name, user_id=user_id)
    if note_kind:
        raise error.KindExistError()

    note_kind = NoteKind()
    note_kind.name = name
    note_kind.user_id = user_id
    note_kind.save()
    return {'pk': note_kind.pk}


@app.route('/api/note/create', methods=['POST'])
@utils.json_response
@utils.login_required
def create_note_api():
    kind_id = flask.request.form.get('kind_id')
    quantity = flask.request.form.get('quantity')
    content = flask.request.form.get('content')
    user_id = int(flask.session['user_id'])

    # Check kind owner
    note_kind = NoteKind.fetchone(pk=kind_id, user_id=user_id)
    if not note_kind:
        raise error.KindNoteExistError()

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
def get_kinds():
    user_id = int(flask.session['user_id'])
    records = NoteKind.fetchall(user_id=user_id)
    return {'kinds': records}


@app.route('/api/notes')
@utils.json_response
@utils.login_required
def get_notes():
    user_id = int(flask.session['user_id'])
    notes = Note.query.filter(
        Note.user_id == user_id,
        Note.create_at >= datetime.now() - timedelta(days=7),
        Note.is_enable == 1
    )
    notes = notes.order_by(Note.create_at.desc())
    dairies = Dairy.query.filter(
        Dairy.user_id == user_id,
        Dairy.create_at >= datetime.now() - timedelta(days=7),
        Dairy.is_enable == 1
    )
    records = notes.all()
    records.extend(dairies.all())
    records = sorted(records, key=lambda x: x.create_at, reverse=True)
    return {'notes': records}


@app.route('/api/note/delete', methods=['POST'])
@utils.json_response
@utils.login_required
def delete_note():
    pk = flask.request.form.get('pk')
    user_id = int(flask.session['user_id'])
    note = Note.fetchone(pk=pk, user_id=user_id)
    if not note:
        raise error.NoteNotExist()
    note.is_enable = 0
    note.save()
    return {'pk': pk}


if __name__ == "__main__":
    from docopt import docopt
    ARGS = docopt(__doc__, version='0.0.1')
    app.run("0.0.0.0", port=int(ARGS['--port']), debug=True)
