#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


class Error(Exception):
    pass


class LoginRequiredError(Error):

    """ Raise when session expired
    """
    STATUS_CODE = -2


class WrongPermissionError(Error):

    """ Raise when permission error
    """

    STATUS_CODE = -3


class UserNotExist(Error):

    STATUS_CODE = -11


class UserPasswordError(Error):

    STATUS_CODE = -12


class RepeatPasswordError(Error):

    STATUS_CODE = -13


class UserEmailRegisted(Error):

    STATUS_CODE = -14


class UserNicknameRegisted(Error):

    STATUS_CODE = -15


class UserStatusError(Error):

    STATUS_CODE = -16


class NoteNotExist(Error):

    STATUS_CODE = -21


class KindExistError(Error):
    STATUS_CODE = -22


class KindNoteExistError(Error):
    STATUS_CODE = -23
