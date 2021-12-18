""" win 不加空格
    set FLASK_APP=flaskr
    set FLASK_ENV=development
    flask run
"""

""" linux 
    export FLASK_APP=flaskr
    export FLASK_ENV=development
    flask run
"""

import os

from flask import Flask


# The Application Factory / 应用工厂
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)  # app.config.from_pyfile()将查看在instance文件夹的特殊文件
    app.config.from_mapping(
        SECRET_KEY='dev',  # 保证数据安全，发布时需要使用一个随机值来重载它
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),  # db 位置
    )

    if test_config is None:  # test_config 实现测试和开发的配置分离，相互独立
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)  # 确保app.instance_path存在。Flask不会自动创建实例文件夹，但是必须确保创建这个文件夹，
                                        # 因为SQLite数据库文件会被保存在里面。
    except OSError:
        pass

    from . import db  # 注册 db 文件
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
