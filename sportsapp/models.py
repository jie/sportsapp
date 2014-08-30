#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class ModelBase(object):
    protected = ['pk', 'id']

    @classmethod
    def fetchall(cls, order=None):
        query = cls.query
        if order is not None:
            query = query.order_by(order)
        return query.all()

    @classmethod
    def fetchone(cls, **filters):
        return cls.query.filter_by(**filters).first()

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        return obj

    def save(self, commit=True):
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
    password = db.Column(db.String(40))
    oauth_id = db.Column(db.String(40))
    oauth_type = db.Column(db.String(12))
    create_at = db.Column(db.DateTime, server_default="current_timestamp")
    update_at = db.Column(db.DateTime)
    is_enable = db.Column(db.Boolean, default=True)


class NoteKind(db.Model, ModelBase):

    __tablename__ = 'note_kind'

    pk = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_at = db.Column(db.DateTime, server_default="current_timestamp")
    update_at = db.Column(db.DateTime)
    is_enable = db.Column(db.Boolean, default=True)
    user = db.relationship('user')


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
    user = db.relationship('user')
    kind = db.relationship('note_kind')
