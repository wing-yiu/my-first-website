import os

from flask import Flask, render_template, request
from werkzeug import secure_filename

from flaskapp import app
from flaskapp.vision import detect_text

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Wing Yiu'}
    return render_template('index.html',
                           title='Home',
                           user=user)


@app.route('/upload')
def upload():
   return render_template('upload.html')


# perform ocr on the file and render, but DO NOT SAVE
@app.route('/ocr2', methods=['GET', 'POST'])
def ocr_file():
   if request.method == 'POST':
        f = request.files['file']
        # save file to local
        filename = secure_filename(f.filename)
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
        f.save(filepath)
        
        # perform ocr
        ocr_text = detect_text(filepath)
    
    # render ocr results
   return render_template('ocr_result.html',
                          ocr_image=filename,
                          ocr_results=ocr_text)