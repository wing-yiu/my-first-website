import io
from PIL import Image, ImageDraw
from google.cloud import vision_v1p3beta1 as vision # beta version


def detect_text(path, draw=True):
    """Detects handwritten characters in a local image.

    Args:
    path: The path to the local file.
    """

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Language hint codes for handwritten OCR:
    # en-t-i0-handwrit, mul-Latn-t-i0-handwrit
    # Note: Use only one language hint code per request for handwritten OCR.
    image_context = vision.types.ImageContext(
        language_hints=['en'])

    response = client.document_text_detection(image=image,
                                              image_context=image_context)
    
    text_response = ""

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                text = ''
                for word in paragraph.words:
                    for symbol in word.symbols:
                        text = text + symbol.text
                text_response += (text + '\n')
                text_response += 'Paragraph confidence: {}\n'.format(paragraph.confidence)
                text_response += '------\n'
                # print(text)
                # print('Paragraph confidence: {}'.format(paragraph.confidence))
                # print('------')

    if draw:
        im = Image.open(path)
        draw = ImageDraw.Draw(im)
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    box = paragraph.bounding_box.vertices
                    draw.polygon([
                        box[0].x, box[0].y,
                        box[1].x, box[1].y,
                        box[2].x, box[2].y,
                        box[3].x, box[3].y], None, 'red')
        im.save(path)

    return text_response