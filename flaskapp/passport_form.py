from flask_wtf import FlaskForm
from wtforms import (StringField, DateField, TextAreaField,
                     SubmitField, RadioField, SelectField)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class PassportForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    birth_date = DateField('Date of Birth', format='%d/%m/%Y', validators=[DataRequired()])
    passport_num = StringField('Passport Number', validators=[DataRequired()])
    nationality = StringField('Nationality', validators=[DataRequired()])
    expiration_date = DateField('Expiration Date', format='%d/%m/%Y', validators=[DataRequired()])
    file = FileField('Passport Image', validators=[FileRequired(),
                                               FileAllowed(['jpg', 'png'],
                                                           '*jpg and *png images only!')
                                               ])
    submit = SubmitField("Send")