import sqlite3

import click
from flask import current_app, g  # current_app 一个特殊对象，该对象指向处理请求的 Flask 应用
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:  # g 是个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存可能多个函数都会用到的数据（存储连接，不多次创建）
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 告诉连接返回类似于字典的行，这样可以通过列名称来操作数据

    return g.db


def close_db(e=None):
    db = g.pop('db', None)  # 在g对象中删除连接

    if db is not None:
        db.close()  # 关闭连接


def init_db():
    db = get_db()  # 与mysql中con类似

    with current_app.open_resource('schema.sql') as f:  # open_resource() 打开一个文件
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')  # 将init-db方法变成command对象，当被调用就会执行实例内的行为（相当于定义一条命令叫做init-db） 'flask init-db'
@with_appcontext  # 打印回调 ?
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)  # 告诉Flask在返回响应后进行清理的时候调用此函数
    app.cli.add_command(init_db_command)  # 添加一个新的可以与Flask一起工作的命令
