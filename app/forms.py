from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(Form):
    # DataRequired ��֤��ֻ�Ǽ򵥵ؼ����Ӧ���ύ�������Ƿ��ǿա�
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


