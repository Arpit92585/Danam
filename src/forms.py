from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class UserRequestForm(FlaskForm):
    user = StringField('User', validators=[DataRequired()])
    request_type = SelectField('Request Type', choices=[('Food', 'Food'), ('Clothes', 'Clothes'), ('Aid', 'Aid'), ('Books', 'Books')], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    # status = SelectField('Status', choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], validators=[DataRequired()])
    submit = SubmitField('Add Request')

class VolunteerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Add Volunteer')

class LoginForm(FlaskForm):
    username_or_email = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Username', validators=[Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password')])
    user_type = SelectField('User Type', choices=[('', 'Select User Type'), ('Donor', 'Donor'), ('NGO', 'NGO'), ('Volunteer', 'Volunteer')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered.')

class OnboardingForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=10, max=200)])
    landmark = StringField('Landmark', validators=[Length(max=100)])
    zip_code = StringField('Zip Code', validators=[DataRequired(), Length(min=5, max=10)])
    submit = SubmitField('Complete Registration')
