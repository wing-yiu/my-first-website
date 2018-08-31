"""Utility class to extract information from passport machine readable zone (MRZ)"""

from typing import Text


class MRZWindow(object):
    """
    Object that describes all the properties in a passport MRZ.
    We extract attributes from the MRZ text based on the position
    of the characters in the string.

    OCR text might not be 100% accurate, so we relax the constraints
    by extracting characters at the position +/- some margin of error.

    e.g. passport number at position [44:52], we will extract
    positions [44-error_margin : 52+error_margin]
    """

    def __init__(self,
                 imagestring: Text):
        """
        initialise MRZ object with a string describing the MRZ
        on a passport. new lines are delimited by \n
        :param imagestring: string of MRZ retrieved from image
        """
        self.imagestring = imagestring
        self.error_margin = 1 + abs(len(imagestring) - 88)

    def error_range(self, start_ind, end_ind):
        """
        Given the expected start/end positions, expand the search area
        by adding error_margin to the start/end positions
        """
        return max(0, start_ind - self.error_margin), \
               min(end_ind + self.error_margin, len(self.imagestring))

    @property
    def document_type(self):
        start, end = self.error_range(0, 0)
        return self.imagestring[start:end]

    @property
    def passport_type(self):
        """
        only applicable for countries that distinguish
        between different types of passports
        """
        start, end = self.error_range(1, 1)
        return self.imagestring[start:end]

    @property
    def country_code(self):
        """
        passport issuing country
        """
        start, end = self.error_range(2, 5)
        return self.imagestring[start:end]

    @property
    def name(self):
        start, end = self.error_range(5, 44)
        return self.imagestring[start:end]

    @property
    def surname(self):
        return list(filter(None, self.name.split('<')))[0]

    @property
    def given_name(self):
        name = list(filter(None, self.name.split('<')))[1:]
        return ' '.join(name)

    @property
    def passport_number(self):
        start, end = self.error_range(44, 53)
        return self.imagestring[start:end]

    @property
    def nationality(self):
        start, end = self.error_range(54, 57)
        return self.imagestring[start:end]

    @property
    def date_of_birth(self):
        start, end = self.error_range(57, 63)
        return self.imagestring[start:end]

    @property
    def gender(self):
        start, end = self.error_range(64, 65)
        return self.imagestring[start:end]

    @property
    def expiration_date(self):
        start, end = self.error_range(65, 71)
        return self.imagestring[start:end]

    @property
    def personal_number(self):
        """
        Only applicable for countries that have a personal number
        """
        start, end = self.error_range(72, 86)
        return self.imagestring[start:end]
