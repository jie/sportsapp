#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


import fabric


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def reload(work_path='/usr/webapps/python/sportsapp'):
    """ Restarting sportsapp
    """
    with fabric.api.cd(work_path):
        fabric.api.sudo('sh shutdown.sh')
        fabric.api.sudo('sh startup.sh')


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def stop(work_path='/usr/webapps/python/sportsapp'):
    """ Stopping sportsapp
    """
    with fabric.api.cd(work_path):
        fabric.api.sudo('sh shutdown.sh')


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def start(work_path='/usr/webapps/python/sportsapp'):
    """ Starting sportsapp
    """
    with fabric.api.cd(work_path):
        fabric.api.sudo('sh startup.sh')


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def update(work_path='/usr/webapps/python/sportsapp'):
    """ Update sportsapp from github
    """
    with fabric.api.cd(work_path):
        fabric.api.sudo('git pull')


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def nginx_reload():
    """ Reload nginx
    """
    fabric.api.sudo('nginx -s reload')


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def nginx_stop():
    """ Stop nginx
    """
    fabric.api.sudo('nginx -s stop')


@fabric.api.hosts('zhouyang@teldrassil.zhouyang.me')
def nginx_start():
    """ Stop start
    """
    fabric.api.sudo('nginx -s start')
