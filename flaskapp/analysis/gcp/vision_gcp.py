from typing import List, Text

from google.cloud import vision_v1p3beta1 as vision  # beta version


def detect_text_gcp(image_bytes: bytes) -> List[Text]:
    """
    Given an image in bytes, recognize text
    in the image and return it as a list of text chunks
    :param image_bytes: image in bytes to perform OCR on
    """

    client = vision.ImageAnnotatorClient()

    image = vision.types.Image(content=image_bytes)

    image_context = vision.types.ImageContext(language_hints=['en'])

    response = client.document_text_detection(image=image,
                                              image_context=image_context)

    text_chunks = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                chunk = ''
                for word in paragraph.words:
                    for symbol in word.symbols:
                        chunk = chunk + symbol.text
                text_chunks.append(chunk)

    return text_chunks
