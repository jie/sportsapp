#!/usr/bin/env python
# encoding: utf-8
# @author: ZhouYang


import fabric

host = 'zhouyang@teldrassil.zhouyang.me'
path = '/usr/webapps/python/sportsapp'


@fabric.api.hosts(host)
def reload(path=path):
    """ Restarting sportsapp
    """
    with fabric.api.cd(path):
        print fabric.colors.green("stoping server")
        fabric.api.sudo('sh shutdown.sh')
        print fabric.colors.green("starting server")
        fabric.api.sudo('sh startup.sh')
        print fabric.colors.green("starting finished")


@fabric.api.hosts(host)
def stop(path=path):
    """ Stopping sportsapp
    """
    with fabric.api.cd(path):
        fabric.api.sudo('sh shutdown.sh')


@fabric.api.hosts(host)
def start(path=path):
    """ Starting sportsapp
    """
    with fabric.api.cd(path):
        fabric.api.sudo('sh startup.sh')


@fabric.api.hosts(host)
def update(path=path, sqls=None):
    """ Update sportsapp from github
    """
    with fabric.api.cd(path):
        fabric.api.sudo('git pull')

    if sqls:
        print fabric.colors.green("start execute sql files")
        sqls_list = sqls.split(',')
        for sql in sqls_list:
            print fabric.colors.green("executing %s" % sql)
            fabric.api.run(
                "mysql -usportsapp -psportsapp sportsapp < " + path + "/sportsapp/sql/" + sql)
    else:
        print fabric.colors.yellow("sqls is None, task over")


@fabric.api.hosts(host)
def nginx_reload():
    """ Reload nginx
    """
    fabric.api.sudo('nginx -s reload')


@fabric.api.hosts(host)
def nginx_stop():
    """ Stop nginx
    """
    fabric.api.sudo('nginx -s stop')


@fabric.api.hosts(host)
def nginx_start():
    """ Stop start
    """
    fabric.api.sudo('nginx')
