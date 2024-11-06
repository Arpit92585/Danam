from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class UserRequestForm(FlaskForm):
    user = StringField('User', validators=[DataRequired()])
    request_type = SelectField('Request Type', choices=[('Food', 'Food'), ('Clothes', 'Clothes'), ('Aid', 'Aid'), ('Books', 'Books')], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], validators=[DataRequired()])
    submit = SubmitField('Add Request')

class VolunteerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Add Volunteer')



