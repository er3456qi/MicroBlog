from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'  # 让Flask-Login知道是哪个view允许用户登陆
# Flask-OpenID 扩展需要一个存储文件的临时文件夹的路径。
# 对此，我们提供了一个 tmp 文件夹的路径。
oid = OpenID(app, os.path.join(basedir, 'tmp'))

if not app.debug:
    import logging
    # bug 邮件报告
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    """
    bug 记录日志. logging.Formatter 类能够定制化日志信息的格式。
    由于这些信息记录到一个文件中，我们希望它们提供尽可能多的信息，所以我们写一个时间戳，
    日志记录级别和消息起源于以及日志消息和堆栈跟踪的文件和行号。
    日志文件将会在 tmp 目录，名称为 microblog.log。
    我们使用了 RotatingFileHandler 以至于生成的日志的大小是有限制的。
    在这个例子中，我们的日志文件的大小限制在 1 兆，我们将保留最后 10 个日志文件作为备份。
    """
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')


from app import views, models
