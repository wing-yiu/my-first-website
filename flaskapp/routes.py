import os

from flask import Flask, render_template, request
from werkzeug import secure_filename

from flaskapp import app
from flaskapp.vision import detect_text


@app.route('/')
def index():
    user = {'username': 'Wing Yiu'}
    return render_template('index.html',
                           title='Home',
                           user=user)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')


# perform ocr on the file using python client
@app.route('/ocr', methods=['GET', 'POST'])
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


# perform ocr using api
from flaskapp.vision_api import (image_converter,
                                 make_request,
                                 format_response)


@app.route('/ocr2', methods=['GET', 'POST'])
def ocr_text():
    if request.method == 'POST':
        f = request.files['file']
        # save file to local
        filename = secure_filename(f.filename)
        filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
        f.save(filepath)

        # perform ocr
        image_64 = image_converter(filepath)
        response = make_request(image_64)
        ocr_text = format_response(response.text)

    # render ocr results
    return render_template('ocr_result.html',
                           ocr_image=filename,
                           ocr_results=ocr_text)