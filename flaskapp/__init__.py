import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
CSRFProtect(app)

app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/flaskapp/static'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

from flaskapp import routes