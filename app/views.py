from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, lm, db, oid
from .forms import LoginForm, EditForm
from .models import User
from datetime import datetime


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    login_required 装饰器确保了这页只被已经登录的用户看到。
    """
    title = 'Hi there'
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
             'author': { 'nickname': 'Susan' },
             'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title=title,
                           user=user,
                           posts=posts)


@lm.user_loader
def load_user(id):
    """
    此函数用于从数据库中加载用户.这个函数将被Flask-Login使用.
    You will need to provide a user_loader callback.
    This callback is used to reload the user object from the user ID stored in the session.
    请注意在 Flask-Login 中的用户 ids 永远是 unicode 字符串，
    因此在我们把 id 发送给 Flask-SQLAlchemy 之前，把 id 转成整型是必须的，
    否则会报错！
    """
    return User.query.get(int(id))


@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    """
    装饰器oid.loginhandle 告诉 Flask-OpenID 这是我们的登录视图函数。
    在函数开始的时候，我们检查 g.user 是否被设置成一个认证用户，如果是的话将会被重定向到首页。
    Flask 中的 g 全局变量是一个在请求生命周期中用来存储和共享数据。我们将登录的用户存储在这里(g)。
    oid.try_login 被调用是为了触发用户使用 Flask-OpenID 认证。
    该函数有两个参数，用户在 web 表单提供的 openid 以及我们从 OpenID 提供商得到的数据项列表。
    OpenID 认证异步发生。
    如果认证成功的话，Flask-OpenID 将会调用一个注册了 oid.after_login 装饰器的函数。
    如果失败的话，用户将会回到登陆页面。
    """
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    """
    :param resp: 包含了从 OpenID 提供商返回来的信息。
    """
    if resp.email is None or resp.email == '':
        flash("invalid login. Please try again")
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:  # 如果邮箱地址在数据库中没有,则是新用户,需要将其添加到数据库
        nickname = resp.nickname
        if nickname is None or nickname == '':
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)  # 正常登陆
    # next保存了用户在未登录时想访问需要登陆的那个页面,如果没有的话就回主页
    return redirect(request.args.get('next') or url_for('index'))


@app.before_request
def before_request():
    """
    为了确定用户是否已经登陆,我们在login视图中检查了g.user.
    为了实现这个我们用 Flask 的 before_request 装饰器.
    任何使用了 before_request 装饰器的函数在接收请求之前都会运行
    全局变量 current_user 是被 Flask-Login 设置的，
    因此我们只需要把它赋给 g.user ，让访问起来更方便。
    有了这个，所有请求将会访问到登录用户，即使在模版里。
    """
    g.user = current_user
    if g.user.is_authenticated():
        # 更新最近访问时间
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    u = User.query.filter_by(nickname=nickname).first()
    if u is None:
        flash('User' + nickname + ' not found')
        return redirect(url_for('index'))
    posts = {
        {'author': u, 'body': 'Test post #1'},
        {'author': u, 'body': 'Test post #2'}
    }
    return render_template('user.html',
                           user=u,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """
    需要注意的是,这里使用了 rollback 声明。
    这是很有必要的因为这个函数是被作为异常的结果被调用。
    如果异常是被一个数据库错误触发，数据库的会话会处于一个不正常的状态，
    因此我们必须把会话回滚到正常工作状态在渲染 500 错误页模板之前。
    """
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can not follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.followed(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found'.format(nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can not unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))