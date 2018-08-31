from typing import List, Text
import re


def process_text(text_chunks: List[Text]) -> Text:
    """
    Given text chunks from image OCR results, apply
    preprocessing steps (lowercase, remove symbols etc.)
    and convert it into a single string
    :param text_chunks: string
    """
    text = ' '.join(text_chunks)
    text = re.sub('\n', '', text)
    text = re.sub('[^a-zA-Z0-9]', '', text)
    return text.lower()


def extract_mrz_from_chunks(text_chunks: List[Text]) -> Text:
    """
    Given text chunks from image OCR results, extract
    the chunk that is most likely to be an MRZ and apply
    preprocessing steps (lowercase, remove symbols etc.)
    :param text_chunks: list of text
    """

    # the chunk with most number of '<' is most likely to be MRZ
    text = max(text_chunks, key=lambda chunk: chunk.count('<'))
    text = re.sub('[^<a-zA-Z0-9]', '', text)
    return text.lower()


def extract_mrz_from_pairs(text_chunks: List[Text]) -> Text:
    """
    Given the special case where pytesseract recognises the MRZ
    as two separate chunks (usually consecutive), we split
    the chunks into pairs and find the pair that is most likely to
    contain the MRZ
    :param text_chunks: list of text
    """

    # ['a', 'b', 'c', 'd', 'e'] -> ['ab', 'bc', 'cd', 'de']
    # from the merged pairs, we guess which is most likely to contain MRZ
    text_chunks = list(filter(None, text_chunks))
    pairs = [a + b for a, b in zip(text_chunks, text_chunks[1:])]
    return extract_mrz_from_chunks(pairs)
