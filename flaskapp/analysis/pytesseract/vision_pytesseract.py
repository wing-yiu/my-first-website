from typing import Text, List
import os
import tempfile

import cv2
import numpy as np
import pytesseract


def run_tesseract_wrapper(input_filename: Text,
                          extension: Text,
                          lang: Text,
                          config: Text) -> Text:
    """
    Function to run tesseract on command line without
    saving the output as a .txt file. Return empty string
    if tesseract is unable to recognise the image.
    """
    with tempfile.NamedTemporaryFile(mode='w+', dir=os.getcwd()) as output:
        try:
            pytesseract.pytesseract.run_tesseract(
                input_filename=input_filename,
                output_filename_base=output.name,
                extension=extension,
                lang=lang,
                config=config)

        except pytesseract.TesseractError:
            # TODO: log the error here instead of print
            print('Error for incompatible config!!!')

        finally:
            with open('{}.{}'.format(output.name, extension), 'r') as file:
                output_text = file.read()
            os.remove('{}.{}'.format(output.name, extension))
            return output_text


def ocr(image: np.ndarray) -> Text:
    """
    Function to compine all processing methods together into
    a single function for ocr.
    """
    # scale image
    large = cv2.resize(image, None, None, fx=1.2, fy=1.2,
                       interpolation=cv2.INTER_LINEAR)

    # sharpen image
    sharp = cv2.filter2D(large, -1,
                         np.array([[-1 / 8, -1 / 8, -1 / 8],
                                   [-1 / 8, 2, -1 / 8],
                                   [-1 / 8, -1 / 8, -1 / 8]]))

    # convert to grayscale
    gray = cv2.cvtColor(sharp, cv2.COLOR_BGR2GRAY)

    # save image as temp file and call tesseract
    with tempfile.NamedTemporaryFile(mode='w+', dir=os.getcwd(),
                                     suffix='.jpg') as image:
        cv2.imwrite(image.name, gray)
        return run_tesseract_wrapper(
            input_filename=image.name,
            extension='txt',
            lang='eng',
            config='--tessdata-dir ./tessdata --oem 0 --psm 1 -c \
                    tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789<"')


def detect_text_pytesseract(image_bytes: bytes) -> List[Text]:
    """
    Given an image in bytes, convert it into a numpy array
    and extract chunks of text in the image using pytesseract.

    :param image_bytes: image to detect text/perform ocr on
    """

    # Process image
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_ANYCOLOR)

    return ocr(img).split('\n')
