import os

from flask import Flask, render_template, request, flash, jsonify
from werkzeug import secure_filename

from flaskapp import app
from flaskapp.vision_api import (image_converter,
                                 make_request,
                                 format_response)
from flaskapp.passport_form import PassportForm


@app.route('/')
def index():
    user = {'username': 'Wing Yiu'}
    return render_template('index.html',
                           title='Home',
                           user=user)


@app.route('/upload2')
def upload2():
    return jsonify({'name': 'wy', 'prop': 'a value'})


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = PassportForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['file']

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
            file.save(filepath)

            # perform ocr
            image_64 = image_converter(filepath)
            response = make_request(image_64)
            ocr_text = format_response(response.text)
            return render_template('ocr_result.html',
                                   ocr_image=filename,
                                   ocr_results=ocr_text)

        else:
            return render_template('upload.html', form=form)
    return render_template('upload.html', form=form)


# perform ocr using api
# @app.route('/ocr/<filename>/<ocr_text>', methods=['GET', 'POST'])
# def ocr(filename, ocr_text):
    # if request.method == 'POST':
    #     f = request.files['file']
    #     # save file to local
    #     filename = secure_filename(f.filename)
    #     filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    #     f.save(filepath)
    #
    #     # perform ocr
    #     image_64 = image_converter(filepath)
    #     response = make_request(image_64)
    #     ocr_text = format_response(response.text)

    # # render ocr results
    # return render_template('ocr_result.html',
    #                        ocr_image=filename,
    #                        ocr_results=ocr_text)

# # perform ocr on the file using python client
# from flaskapp.vision import detect_text
# 
# 
# @app.route('/ocr', methods=['GET', 'POST'])
# def ocr_file():
#     if request.method == 'POST':
#         f = request.files['file']
#         # save file to local
#         filename = secure_filename(f.filename)
#         filepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
#         f.save(filepath)
# 
#         # perform ocr
#         ocr_text = detect_text(filepath)
# 
#     # render ocr results
#     return render_template('ocr_result.html',
#                            ocr_image=filename,
#                            ocr_results=ocr_text)
