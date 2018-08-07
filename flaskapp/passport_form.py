from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, TextAreaField,
                     SubmitField, RadioField, SelectField)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class PassportForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    file = FileField('Passport', validators=[FileRequired(),
                                               FileAllowed(['jpg', 'png'],
                                                           '*jpg and *png images only!')
                                               ])
    submit = SubmitField("Send")