from flask_wtf import FlaskForm
from wtforms import  StringField, EmailField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length





class ContactForm(FlaskForm):
    name = StringField('Name', validators=[Length(min=2)])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Subject', validators=[Length(min=2)])
    phone = StringField('Phone')
    message = TextAreaField('Message', validators=[Length(min=2)])
    submit = SubmitField('Contact Me')



class SignIn(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Length(min=2)])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Signin')


class Registration(FlaskForm):
    username = StringField('Name', validators=[Length(min=2)])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Register')

class ContentForm(FlaskForm):
    header = StringField(label='Header', validators=[DataRequired(), Length(min=2, max=50)])
    paragraph = TextAreaField(label='Paragraph', validators=[DataRequired(), Length(min=52, max=100)])
    image = StringField(label='Image_Url')
    category = StringField(label='Category', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Add')

class EditForm(FlaskForm):
    header = StringField(label='Header', validators=[DataRequired(), Length(min=2, max=15)])
    paragraph = TextAreaField(label='Paragraph', validators=[DataRequired(), Length(min=2, max=100)])
    image = StringField(label='Image_Url')
    category = StringField(label='Category', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Edit')