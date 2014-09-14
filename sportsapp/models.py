#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang

import sqlalchemy
from hashlib import sha1
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class ModelBase(object):
    protected = ['pk', 'id']

    @classmethod
    def fetchall(cls, order=None, **filters):
        query = cls.query
        if order is not None:
            query = query.order_by(order)
        return query.filter_by(**filters).all()

    @classmethod
    def fetchmany(cls, count, order=None, **filters):
        query = cls.query
        if order is not None:
            query = query.order_by(order)
        return query.filter_by(**filters).limit(count)

    @classmethod
    def fetchone(cls, **filters):
        return cls.query.filter_by(**filters).first()

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj

    def save(self, commit=True):
        if hasattr(self, 'update_at'):
            self.update_at = datetime.now()
        db.session.add(self)
        if commit:
            self.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            self.commit()
        return self

    def commit(self):
        try:
            db.session.commit()
            db.session.refresh(self)
        except:
            db.session.rollback()
            raise

    def flush(self):
        db.session.flush()
        db.session.refresh(self)

    def update(self, commit=True, **kwargs):
        for key, val in kwargs.iteritems():
            if getattr(self, key, None) != val and key not in self.protected:
                setattr(self, key, val)

        db.session.add(self)

        if commit is False:
            self.flush()
        else:
            self.commit()


class User(db.Model, ModelBase):

    __tablename__ = 'user'

    pk = db.Column('id', db.Integer, primary_key=True)
    nickname = db.Column(db.String(36), unique=True)
    email = db.Column(db.String(32))
    avatar = db.Column(db.String(128))
    password = db.Column(db.String(40))
    oauth_id = db.Column(db.String(40))
    oauth_type = db.Column(db.String(12))
    create_at = db.Column(db.DateTime, server_default="current_timestamp")
    update_at = db.Column(db.DateTime)
    is_enable = db.Column(db.Boolean, default=True)
    status = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'pk': self.pk,
            'nickname': self.nickname,
            'email': self.email,
            'create_at': self.create_at,
            'status': self.status,
            'avatar': self.avatar
        }

    def set_password(self, password):
        self.password = sha1(password).hexdigest()

    @classmethod
    def checkUserinfo(cls, pk, email, nickname, password):
        user = cls.query.filter(
            cls.pk != pk,
            sqlalchemy.or_(cls.nickname == nickname, cls.email == email),
        ).first()
        return True if user else False


class NoteKind(db.Model, ModelBase):

    __tablename__ = 'note_kind'

    pk = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_at = db.Column(db.DateTime, server_default="current_timestamp")
    update_at = db.Column(db.DateTime)
    is_enable = db.Column(db.Boolean, default=True)
    user = db.relationship('User')

    def to_dict(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'create_at': self.create_at
        }


class Note(db.Model, ModelBase):

    __tablename__ = 'note'

    pk = db.Column('id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    kind_id = db.Column(db.Integer, db.ForeignKey('note_kind.id'))
    quantity = db.Column(db.Integer)
    content = db.Column(db.String)
    create_at = db.Column(db.DateTime, server_default="current_timestamp")
    update_at = db.Column(db.DateTime)
    is_enable = db.Column(db.Boolean, default=True)
    user = db.relationship('User')
    kind = db.relationship('NoteKind')

    def to_dict(self):
        return {
            'pk': self.pk,
            'user': self.user,
            'kind': self.kind,
            'quantity': self.quantity,
            'content': self.content,
            'create_date': self.create_at.strftime('%Y-%m-%d')
        }

    def avatar_url(self):
        return self.avatar


class Dairy(db.Model, ModelBase):

    __tablename__ = 'dairy'

    pk = db.Column('id', db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_at = db.Column(db.DateTime, server_default="current_timestamp")
    update_at = db.Column(db.DateTime)
    is_enable = db.Column(db.Boolean, default=True)
    user = db.relationship('User')

    def to_dict(self):
        return {
            'pk': self.pk,
            'user': self.user,
            'title': self.title,
            'content': self.content,
            'create_date': self.create_at.strftime('%Y-%m-%d')
        }
