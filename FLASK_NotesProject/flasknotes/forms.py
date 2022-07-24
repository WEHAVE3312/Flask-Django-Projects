from ast import Sub
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField,BooleanField, TextAreaField
from wtforms.validators import DataRequired,Length,EqualTo,ValidationError
from flasknotes.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    #Busca dentro de la base de datos si los campos existen, en ese caso regresare una alerta
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username its already taken!')
    
class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class NewNote(FlaskForm):
    content = StringField('New Note',validators=[DataRequired()])
    submit = SubmitField('Add!')
    
