# TODO: create a flask app and implement all required routes here

from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.get('/user/<int:uid>')
@app.get('/user/@<string:username>')
@app.get('/user/')
@app.get('/lotto/<int:n>/<int:k>')
@app.get('/search')

def get_userinfo(uid=None, username=None):

    if uid is not None:
       return f'User ID: {escape(uid)}'

    elif username is not None:
       return f'User Profile: {escape(username)}'
    else:
       return f'User Profile: guest'

def get_lotto(n=None, k = None):

   if k>n:
      return f'Error: sample size k cannot exceed total range', 400
   
   lotto_numbers = random.sample(range(1, n + 1), k)
   return ' '.join(map(str, lotto_numbers))
   
def get_search():
    query = request.args.get('query', 'everything')
    page = request.args.get('page', '1')
    
    try:
        page = int(page)
    except ValueError:
        return 'Error: page must be an integer', 400
        
    return f'Page {page} of search results for "{escape(query)}"'