# TODO: create a flask app and implement all required routes here

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.get('/user/<int:uid>')
@app.get('/user/@<string:username>')
@app.get('/user/')

def get_userinfo(uid=None, username=None):

    if uid is not None:
       return f'User ID: {escape(uid)}'

    elif username is not None:
       return f'User Profile: {escape(username)}'
    else:
       return f'User Profile: guest'