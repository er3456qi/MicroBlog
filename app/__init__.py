from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'  # 让Flask-Login知道是哪个view允许用户登陆
# Flask-OpenID 扩展需要一个存储文件的临时文件夹的路径。
# 对此，我们提供了一个 tmp 文件夹的路径。
oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import views, models
