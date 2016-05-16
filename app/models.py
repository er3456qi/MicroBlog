from app import db
from hashlib import md5

# 一个多对多的关注与被关注的关系表
# 我们并没有像对 users 和 posts 一样把它声明为一个模式。
# 因为这是一个辅助表，我们使用 flask-sqlalchemy 中的低级的 APIs 来创建没有使用关联模式。
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    """
    ‘User’ 是这种关系中的右边的表(实体)(左边的表/实体是父类)。
    因为定义一个自我指向的关系，我们在两边使用同样的类。
    secondary 指明了用于这种关系的辅助表。
    primaryjoin 表示辅助表中连接左边实体(发起关注的用户)的条件。
    注意因为 followers 表不是一个模式，获得字段名的语法有些怪异。
    secondaryjoin 表示辅助表中连接右边实体(被关注的用户)的条件。
    backref 定义这种关系将如何从右边实体进行访问。
    当我们做出一个名为 followed 的查询的时候，将会返回所有跟左边实体联系的右边的用户。
    当我们做出一个名为 followers 的查询的时候，将会返回一个所有跟右边联系的左边的用户。
    lazy 指明了查询的模式。dynamic 模式表示直到有特定的请求才会运行查询，这是对性能有很好的考虑。
    lazy 是与 backref 中的同样名称的参数作用是类似的，但是这个是应用于常规查询。
    """
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic'
                               )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_followed.remove(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id))\
                        .filter(followers.c.follower_id == self.id)\
                        .order_by(Post.timestamp.desc())

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



