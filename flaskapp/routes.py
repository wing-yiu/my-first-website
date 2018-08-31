from flask import render_template, jsonify, request, abort

from flaskapp import app
from flaskapp.analysis.gcp.vision_gcp import detect_text_gcp
from flaskapp.analysis.ctpn.vision_ctpn import detect_text_ctpn
from flaskapp.analysis.pytesseract.vision_pytesseract import detect_text_pytesseract
from flaskapp.analysis.utils.text_utils import (process_text,
                                                extract_mrz_from_chunks,
                                                extract_mrz_from_pairs)
from flaskapp.analysis.utils.validate_form import validate_form


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result_gcp', methods=['POST'])
def result_gcp():
    if not request.files['passportPhoto']:
        abort(400)

    image_bytes = request.files['passportPhoto'].read()
    text_chunks = detect_text_gcp(image_bytes)
    ocr_text = process_text(text_chunks)
    mrz_text = extract_mrz_from_chunks(text_chunks)
    validation = validate_form(form_data=request.form,
                               ocr_text=ocr_text,
                               mrz_text=mrz_text,
                               surname_field='surname',
                               name_field='givenName',
                               gender_field='gender',
                               dob_field='dob',
                               passport_num_field='passportNumber',
                               nationality_field='nationality',
                               expiry_field='passportExpiryDate')
    return jsonify(validation), 200


@app.route('/result_ctpn', methods=['POST'])
def result_ctpn():
    if not request.files['passportPhoto']:
        abort(400)

    image_bytes = request.files['passportPhoto'].read()
    text_chunks = detect_text_ctpn(image_bytes=image_bytes,
                                   sess=app.config['tf_session'])
    ocr_text = process_text(text_chunks)
    mrz_text = extract_mrz_from_chunks(text_chunks)
    validation = validate_form(form_data=request.form,
                               ocr_text=ocr_text,
                               mrz_text=mrz_text,
                               surname_field='surname',
                               name_field='givenName',
                               gender_field='gender',
                               dob_field='dob',
                               passport_num_field='passportNumber',
                               nationality_field='nationality',
                               expiry_field='passportExpiryDate')
    return jsonify(validation), 200


@app.route('/result_pytesseract', methods=['POST'])
def result_pytesseract():
    if not request.files['passportPhoto']:
        abort(400)

    image_bytes = request.files['passportPhoto'].read()
    text_chunks = detect_text_pytesseract(image_bytes=image_bytes)
    ocr_text = process_text(text_chunks)
    mrz_text = extract_mrz_from_pairs(text_chunks)
    validation = validate_form(form_data=request.form,
                               ocr_text=ocr_text,
                               mrz_text=mrz_text,
                               surname_field='surname',
                               name_field='givenName',
                               gender_field='gender',
                               dob_field='dob',
                               passport_num_field='passportNumber',
                               nationality_field='nationality',
                               expiry_field='passportExpiryDate')
    return jsonify(validation), 200
