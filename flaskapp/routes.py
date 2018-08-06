import os

from flask import Flask, render_template, request
from werkzeug import secure_filename

from flaskapp import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Wing Yiu'}
    return render_template('index.html', title='Home', user=user)


@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/ocr', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      f.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
      return 'file uploaded successfully'