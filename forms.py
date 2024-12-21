from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, URLField
from wtforms.validators import DataRequired, URL


class AddProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    image_url = URLField("Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Add Product")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("LogIn!")


class ContactForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired()])
    number = StringField(label='Phone Number', validators=[DataRequired()])
    message = TextAreaField(label='Message', validators=[DataRequired()])
    submit = SubmitField(label='Send Message')
