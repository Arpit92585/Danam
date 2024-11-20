import atexit
import shutil
import os
import email
from flask import Flask, render_template, redirect, url_for, flash, request, session, make_response
from flask_sqlalchemy import SQLAlchemy

from forms import UserRequestForm, VolunteerForm, RegisterForm, LoginForm, OnboardingForm

from flask_cors import CORS
from flask_session import Session
from models import db, UserRequest, Volunteer, User, UserRole  # Import the db and models
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Resource, Api

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the db object with the app
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginStatus(Resource):
    def get(self):
        if 'email' in session:
            user = User.query.filter_by(email=session['email']).first()
            if user:
                return {
                    'status': 'logged_in',
                    'username': user.name,
                    'profile_image': session.get('profile_image'),
                    'role': user.role
                }
        return {'status': 'logged_out'}

api = Api(app)
api.add_resource(LoginStatus, '/api/login_status')

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes/Views --------------------------------------
# -------------------------------------------------------------------------------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    register_form = RegisterForm()
    # if user already in session redirect to dashboard
    if 'user_name' in session:
        print(f'User already in session: {session["user_name"]}')
        return redirect(url_for('dashboard'))
    
    if register_form.submit.data and register_form.validate_on_submit():
        print(f'Register button clicked data: {register_form.data}')
        # Handle Registration
        hashed_password = generate_password_hash(register_form.password.data)
        new_user = User(
            name=register_form.name.data,
            email=register_form.email.data,
            password=hashed_password,
            role=register_form.user_type.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session['user_type'] = new_user.role
        session['user_name'] = new_user.name
        session['email'] = new_user.email
        flash('Registration successful. You are now logged in.', 'success')
        return redirect(url_for('dashboard'))
    
    if login_form.submit.data and login_form.validate_on_submit():
        print(f'Login button clicked data: {login_form.data}')
        # Handle Login
        user = User.query.filter((User.email == login_form.username_or_email.data) | (User.name == login_form.username_or_email.data)).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user)
            session['user_type'] = user.role
            session['user_name'] = user.name
            session['email'] = user.email
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email/username or password', 'danger')
    
    return render_template('logins/login.html', login_form=login_form, register_form=register_form)

# Route for User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    #clear session everything from session
    session.clear()
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))


# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Onboarding ----------------------------------------
# -------------------------------------------------------------------------------------------------
@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    form = OnboardingForm()
    if 'email' in session:
        form.email.data = session['email']
    if form.validate_on_submit():
        # Save the onboarding details to the database
        # For demonstration, we'll just flash a message
        flash('Registration complete!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('logins/onboarding.html', form=form)

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Dashboard -----------------------------------------
# -------------------------------------------------------------------------------------------------

# Route for User Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = UserRequestForm()
    if form.validate_on_submit():
        new_request = UserRequest(
            user=form.user.data,
            request_type=form.request_type.data,
            location=form.location.data,
            status=form.status.data
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Request added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('dashboards/dashboard.html', form=form)

# Route for NGO Dashboard
@app.route('/ngo_dashboard', methods=['GET', 'POST'])
def ngo_dashboard():
    requests = UserRequest.query.all()
    
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        new_status = request.form.get('new_status')
        user_request = UserRequest.query.get(request_id)
        if user_request:
            user_request.status = new_status
            db.session.commit()
            flash('Status updated successfully!', 'success')
            return redirect(url_for('ngo_dashboard'))

    return render_template('dashboards/ngo_dashboard.html', requests=requests)

@app.route('/volunteer_dashboard')
def volunteer_dashboard():
    return render_template('dashboards/volunteer_dashboard.html')

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes/Views --------------------------------------
# -------------------------------------------------------------------------------------------------

# Route for Homepage
@app.route('/')
def homepage():
    requests = UserRequest.query.all()
    return render_template('routes/home.html', requests=requests)



# Route for adding a volunteer
@app.route('/add_volunteer', methods=['GET', 'POST'])
def add_volunteer():
    form = VolunteerForm()
    if form.validate_on_submit():
        new_volunteer = Volunteer(
            name=form.name.data,
            location=form.location.data,
            phone_number=form.phone_number.data
        )
        db.session.add(new_volunteer)
        db.session.commit()
        flash('Volunteer added successfully!', 'success')
        return redirect(url_for('available_volunteers'))  
    return render_template('routes/add_volunteer.html', form=form)

# Route for displaying available volunteers
@app.route('/available_volunteers')
def available_volunteers():
    volunteers = Volunteer.query.all()
    return render_template('routes/available_volunteers.html', volunteers=volunteers)

@app.route('/assign_volunteer/<int:request_id>', methods=['GET', 'POST'])
def assign_volunteer(request_id):
    user_request = UserRequest.query.get_or_404(request_id)
    volunteers = Volunteer.query.all()  # Get all available volunteers

    if request.method == 'POST':
        volunteer_id = request.form.get('volunteer_id')
        volunteer = Volunteer.query.get(volunteer_id)
        if volunteer:
            user_request.assigned_volunteer_id = volunteer.id  # Assign volunteer to request
            db.session.commit()
            flash(f'Volunteer {volunteer.name} assigned successfully!', 'success')
            return redirect(url_for('ngo_dashboard'))  # Redirect to NGO dashboard or wherever appropriate

    return render_template('routes/assign_volunteer.html', user_request=user_request, volunteers=volunteers)

@app.route('/user_request/<int:request_id>')
def user_request(request_id):
    user_request = UserRequest.query.get_or_404(request_id)  # Ensure you're retrieving the user request correctly
    assigned_volunteer = Volunteer.query.get(user_request.assigned_volunteer_id) if user_request.assigned_volunteer_id else None
    return render_template('routes/user_request.html', request=user_request, assigned_volunteer=assigned_volunteer)


@app.route('/functionalities')
def functionalities():
    return render_template('routes/functionalities.html')

@app.route('/aboutus')
def aboutus():
    return render_template('routes/aboutus.html')

def prompt_and_delete_folders():
    folders_to_delete = ['instance', '__pycache__']
    print('\n')
    for folder in folders_to_delete:
        if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)
                print(f"Deleted folder: {folder}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    # atexit.register(prompt_and_delete_folders)

    # app.run(host='192.168.29.235')
    app.run(debug=True)
