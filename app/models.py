#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from app.exceptions import ValidationError

class Permission(object):

    '''
        settings about Permissions, using Hex expression
    '''

    SUBMIT_CODE     = 0x01
    EDIT_TAG        = 0x02
    WATCH_CODE      = 0x04
    MODIFY_PROBLEM  = 0x08
    JUDGER          = 0x20
    ADMIN           = 0x40
    SUPER_ADMIN     = 0x80

    def __init__(self):

        pass


class KeyValue(db.Model):

    '''
        define Key-Value database for this judge
    '''

    __tablename__ = 'config'
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)


class Role(db.Model):

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():

        '''
            insert roles to role table
        :return: None
        '''

        # init roles
        roles = {
            'User' : (Permission.SUBMIT_CODE | Permission.MODIFY_CONTEST, True),
            'Local Judger' : (Permission.JUDGER, False),
            'Remote Judger': (Permission.JUDGER, False),
            'Administrator': (Permission.ADMIN, False),
            "Super Administrator": (0xff, False)
        }

        # query and insert roles
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
