import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')  # 创建一个module 需要在应用工厂注册 auth包括 注册 & 登录


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",  # 对密码进行加密，生成hash字符串 占位符自动转义输入值 抵御SQL注入攻击
                    (username, generate_password_hash(password)),  # werkzeug库
                )
                db.commit()
            except db.IntegrityError:  # 用户名已存在情况（数据库中设置username为UNIQUE）
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))  # 注册成功后跳转到登录页面（url_for好处在于如果以后需要修改该视图对应的url，那么不用修改所有涉及到url的代码）

        flash(error)  # 发送一条消息

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()  # session 储存横跨请求的值 id被储存到一个新的会话中 会话数据被储存到一个向浏览器发送的cookie中aaa
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request  # 注册一个在视图函数之前运行的函数，不论其 URL 是什么。检查用户 id是否已经储存在session中，并从数据库中获取用户数据，然后储存在 g.user 中。
# g.user 的持续时间比请求要长。 如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """
    装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。新的函数检查用户 是否已载入。
    如果已载入，那么就继续正常执行原视图，否则就重定向到登录页面。
    我们会在博客视图中使用这个装饰器。
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
