from app import app
from flask import render_template


@app.route('/')
@app.route('/index')
def index():
    title = 'Hi there'
    user = {'nickname': 'Wnbot' }
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
    return render_template('index.html', title=title, user=user, posts=posts)