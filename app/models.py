from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)

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