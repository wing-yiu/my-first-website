import os
from flask import Flask

app = Flask(__name__)
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/flaskapp/static'

from flaskapp import routes