from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    code_id = StringField("Código de Estudante", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    remember_me = BooleanField("remember_me")

class Cadastro(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    code_id = StringField("Código de Estudante", validators=[DataRequired()])
    email = EmailField("email", validators=[DataRequired()])
    tel = StringField("tel", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class UpdateProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    code_id = StringField("Código de Estudante", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    tel = StringField("tel", validators=[DataRequired()])

class QuestionForm(FlaskForm):
    question_text = StringField('question', validators=[DataRequired()])
    answer = StringField('answer', validators=[DataRequired()])