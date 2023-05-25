from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, NumberRange


# Form fields for update reviews and rating
class UpdateForm(FlaskForm):
    rating = FloatField('Your Rating Out of 10',
                        validators=[DataRequired(), NumberRange(min=0, max=10, message="out of range")])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField('Done')


# Form fields for movie search
class AddMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField('Add Movie')


# Form fields for new user registration
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField('Register')


# Form fields for login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField('Login')

