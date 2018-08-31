from typing import Text, Dict
import re
from datetime import datetime

from flaskapp.analysis.utils.mrz_window import MRZWindow


def validate_form(form_data: Dict,
                  ocr_text: Text,
                  mrz_text: Text,
                  surname_field: Text,
                  name_field: Text,
                  gender_field: Text,
                  dob_field: Text,
                  passport_num_field: Text,
                  nationality_field: Text,
                  expiry_field: Text) -> Dict:
    """
    Given form data, validate whether the values in form_data can be
    found in ocr_text (for name/surname) or mrz_text (all other fields)
    and return a dictionary of {field: bool}
    :param form_data: Dict of form fields {field: value}
    :param ocr_text: Text extracted from image OCR
    :param mrz_text: Text extracted from image OCR that represents MRZ
    :param surname_field: field name in form representing surname
    :param name_field: field name in form representing given name
    :param gender_field: field name in form representing gender
    :param dob_field: field name in form representing date of birth
    :param passport_num_field: field name in form representing passport number
    :param nationality_field: field name in form representing nationality
    :param expiry_field: field name in form representing expiration date
    """

    is_valid = dict()
    mrz = MRZWindow(mrz_text)

    # Name validation based on ocr_text because long names
    # may be truncated in MRZ. Split name into individual words
    # and see if each word in name exists in ocr_text
    is_valid[surname_field] = all(
        [re.sub('[^a-zA-Z0-9]', '', word).lower() in ocr_text
         for word in form_data.get(surname_field).split(' ')])

    is_valid[name_field] = all(
        [re.sub('[^a-zA-Z0-9]', '', word).lower() in ocr_text
         for word in form_data.get(name_field).split(' ')])

    # Match remaining fields with MRZ
    is_valid[passport_num_field] = (re.sub('[^a-zA-Z0-9]',
                                           '',
                                           form_data.get(passport_num_field))
                                    .lower() in mrz.passport_number)

    is_valid[nationality_field] = (re.sub('[^a-zA-Z0-9]',
                                          '',
                                          form_data.get(nationality_field))
                                   .lower() in mrz.nationality)

    is_valid[gender_field] = (re.sub('[^a-zA-Z0-9]',
                                     '',
                                     form_data.get(gender_field))
                              .lower() in mrz.gender)

    # Date fields must be converted to %y%m%d format to match MRZ
    expiry = datetime.strptime(form_data.get(expiry_field), "%Y-%m-%d").strftime('%y%m%d')
    is_valid[expiry_field] = re.sub('[^a-zA-Z0-9]',
                                    '',
                                    expiry) in mrz.expiration_date

    dob = datetime.strptime(form_data.get(dob_field), "%Y-%m-%d").strftime('%y%m%d')
    is_valid[dob_field] = re.sub('[^a-zA-Z0-9]',
                                 '',
                                 dob) in mrz.date_of_birth

    return is_valid