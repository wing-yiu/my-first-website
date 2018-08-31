"""Utility class to extract information from passport machine readable zone (MRZ)"""

import re
from typing import Text, Dict
from datetime import datetime


class MRZ(object):
    """
    Object that describes all the properties in a passport MRZ
    """

    def __init__(self,
                 imagestring: Text):
        """
        initialise MRZ object with a string describing the MRZ
        on a passport. new lines are delimited by \n
        :param imagestring: string of MRZ retrieved from pytesseract
        """
        self.imagestring = imagestring
        self.string_list = self.imagestring.split('\n')
        self.first_row = self.string_list[0]
        self.second_row = self.string_list[1]

    @property
    def document_type(self):
        return self.first_row[0] == 'P'

    @property
    def passport_type(self):
        """
        only applicable for countries that distinguish
        between different types of passports
        """
        if self.first_row[1] == '<':
            return 'NA'

        return self.first_row[1]

    @property
    def country_code(self):
        """
        passport issuing country
        """
        return re.sub('<', '', self.first_row[2:5])

    @property
    def name(self):
        return self.first_row[5:44]

    @property
    def surname(self):
        return list(filter(None, self.name.split('<')))[0]

    @property
    def given_name(self):
        name = list(filter(None, self.name.split('<')))[1:]
        return ' '.join(name)

    @property
    def passport_number(self):
        return re.sub('<', '', self.second_row[0:9])

    @property
    def nationality(self):
        return re.sub('<', '', self.second_row[10:13])

    @property
    def date_of_birth(self):
        date = self.second_row[13:19]
        dob = datetime.strptime(date, '%y%m%d')

        # known issue with datetime library that confuses
        # any year <= 68 to become 2068 instead of 1968
        if dob > datetime.now():
            return (dob.replace(year=dob.year-100)).strftime('%d/%m/%Y')

        return dob.strftime('%d/%m/%Y')

    @property
    def gender(self):
        if self.second_row[20] != 'M' and self.second_row[20] != 'F':
            return 'Unspecified'
        return self.second_row[20]

    @property
    def expiration_date(self):
        date = self.second_row[21:27]
        return datetime.strptime(date, '%y%m%d').strftime('%d/%m/%Y')

    @property
    def personal_number(self):
        """
        Only applicable for countries that have a personal number
        """
        if re.sub('<', '', self.second_row[28:42]):
            return re.sub('<', '', self.second_row[28:42])
        return 'NA'

    @property
    def checkdigit_1(self):
        """
        check digit over second row, characters [0:9] (passport number)
        """
        return check_digit(self.second_row[0:9])

    @property
    def checkdigit_2(self):
        """
        check digit over second row, characters [13:19] (date of birth)
        """
        return check_digit(self.second_row[13:19])

    @property
    def checkdigit_3(self):
        """
        check digit over second row, characters [21:27] (expiration date)
        """
        return check_digit(self.second_row[21:27])

    @property
    def checkdigit_4(self):
        """
        check digit over second row, characters [28:42] (personal number)
        """
        if self.personal_number == 'NA':
            return '<'
        return check_digit(self.second_row[28:42])

    @property
    def checkdigit_final(self):
        """
        check digit over second row, characters [0:10], [13:20], [21:43]
        """
        return check_digit(self.second_row[0:10] +
                           self.second_row[13:20] +
                           self.second_row[21:43])

    @property
    def is_valid(self):
        """
        determine whether the string provided is a valid MRZ
        - can be split into 2 lines, 44 characters each
        - check digits are correct
        """
        return ((len(self.string_list) == 2) and
                (len(self.first_row) == 44) and
                (len(self.second_row) == 44) and
                (str(self.checkdigit_1) == self.second_row[9]) and
                (str(self.checkdigit_2) == self.second_row[19]) and
                (str(self.checkdigit_3) == self.second_row[27]) and
                (str(self.checkdigit_4) == self.second_row[42]) and
                (str(self.checkdigit_final) == self.second_row[43]))

    def to_dict(self) -> Dict:
        return {'document_type': self.document_type,
                'passport_type': self.passport_type,
                'country_code': self.country_code,
                'surname': self.surname,
                'given_name': self.given_name,
                'passport_number': self.passport_number,
                'nationality': self.nationality,
                'date_of_birth': self.date_of_birth,
                'gender': self.gender,
                'expiration_date': self.expiration_date,
                'personal_number': self.personal_number,
                'checkdigit_1': self.checkdigit_1,
                'checkdigit_2': self.checkdigit_2,
                'checkdigit_3': self.checkdigit_3,
                'checkdigit_4': self.checkdigit_4,
                'checkdigit_final': self.checkdigit_final,
                'is_valid': self.is_valid
                }


def check_digit(substring) -> int:
    """
    Given a string, compute its check digit based on a given formula
    http://www.highprogrammer.com/alan/numbers/mrp.html#countrycodes

    The check digit calculation is as follows:
    each position is assigned a value;
    for the digits 0 to 9 it is the value of the digits,
    for the letters A to Z this is 10 to 35,
    for the filler < this is 0.
    The value of each position is then multiplied by its weight;
    the weight of the first position is 7, of the second it is 3, and of the third it is 1,
    and after that the weights repeat 7, 3, 1, and so on.
    All values are added together and the remainder of the
    final value divided by 10 is the check digit.
    """
    reference = {'<': 0, '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                 '6': 6, '7': 7, '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12,
                 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18,
                 'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24,
                 'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29, 'U': 30,
                 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35}

    # convert string to list of digits
    charlist = [reference[char] for char in list(substring)]

    # create a repeated list of [7, 3, 1]
    checklist = [7, 3, 1] * (len(charlist)//3 + 1)

    # multiply charlist by checklist
    checkdigit = sum([a*b for a,b in zip(charlist,checklist)])

    return checkdigit % 10
