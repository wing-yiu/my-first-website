import io
import os
import json
import base64
import requests


def image_converter(image_path):
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    return base64.b64encode(content).decode('UTF-8')


def make_request(image_base64):
    img_request = {"requests": [{
                                'image': {'content': image_base64},
                                'features': [{
                                    'type': 'TEXT_DETECTION',
                                    'maxResults': 1
                                    }]
                                }]
                   }

    return requests.post(
        url="https://vision.googleapis.com/v1/images:annotate",
        params={'key': os.environ['GCP_KEY']},
        data=json.dumps(img_request),
        headers={'Content-Type': 'application/json'}
    )


def format_response(response_text):
    text_response = ""

    json_response = json.loads(response_text)
    for page in json_response['responses'][0]['fullTextAnnotation']['pages']:
        for block in page['blocks']:
            for paragraph in block['paragraphs']:
                text = ''
                for word in paragraph['words']:
                    for symbol in word['symbols']:
                        text = text + symbol['text']
                text_response += (text + '\n')
                text_response += '------\n'

    return text_response

