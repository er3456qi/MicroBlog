from app import db
from hashlib import md5


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def avatar(self, size):
        """
        为了美观.用户需要头像,我们不需要在自己的服务器上处理大量的上传图片,
        我们依赖Gravatar服务为我们生成用户头像
        你只需要创建一个用户邮箱的 MD5 哈希，然后将其加入 URL中，像上面你看见的。
        在邮箱 MD5 后，你还需要提供一个定制头像尺寸的数字。
        d=mm 决定什么样的图片占位符当用户没有 Gravatar 账户。
        mm 选项将会返回一个“神秘人”图片，一个人灰色的轮廓。
        s=N 选项要求头像按照以像素为单位的给定尺寸缩放。
        详见: https://gravatar.com/site/implement/images
        """
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?=mm&s=' + str(size)

    @staticmethod
    def make_unique_nickname(nickname):
        """
        防止出现重名
        """
        if User.query.fileter_by(nickname=nickname).first() is None:
            return nickname
        version, new_nickname = 2, ''
        while True:
            new_nickname = nickname + str(version)
            if User.query.fileter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def __repr__(self):
        # __repr__ 方法告诉 Python 如何打印这个类的对象。我们将用它来调试。
        return '<User {}>'.format(self.nickname)

    """
    下面几个方法是Flask-Login 推荐的User类需要实现的方法
    """
    @property
    def is_authenticated(self):
        # 一般而言，这个方法应该只返回 True，
        # 除非表示用户的对象因为某些原因不允许被认证。
        return True

    @property
    def is_active(self):
        # 此方法方法应该返回 True，
        # 除非是用户是无效的， 比如因为他们的账号是被禁止。
        return True

    @property
    def is_anonymous(self):
        #  此方法应该返回 True，除非是伪造的用户不允许登录系统。
        return False

    def get_id(self):
        return str(self.id)
        # try:
        #     return unicode(id)  # python 2
        # except NameError:
        #     return str(self.id)  # python 3


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)