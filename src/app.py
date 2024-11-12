import atexit
import shutil
import os
import email
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from forms import UserRequestForm, VolunteerForm, RegistrationForm, LoginForm  # Ensure VolunteerForm, RegistrationForm, and LoginForm are imported
from flask_cors import CORS
from flask_session import Session
from models import db, UserRequest, Volunteer, User  # Import the db and models
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

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


# -------------------------------------------------------------------------------------------------
# --------------------------------------------- LoginManager --------------------------------------
# -------------------------------------------------------------------------------------------------

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(full_name=form.full_name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

# Route for User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

# Route for User Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))

# -------------------------------------------------------------------------------------------------
# --------------------------------------------- Routes/Views --------------------------------------
# -------------------------------------------------------------------------------------------------

# Route for Homepage
@app.route('/')
def homepage():
    requests = UserRequest.query.all()
    return render_template('home.html', requests=requests)

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
    return render_template('dashboard.html', form=form)

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

    return render_template('ngo_dashboard.html', requests=requests)

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
    return render_template('add_volunteer.html', form=form)

# Route for displaying available volunteers
@app.route('/available_volunteers')
def available_volunteers():
    volunteers = Volunteer.query.all()
    return render_template('available_volunteers.html', volunteers=volunteers)

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

    return render_template('assign_volunteer.html', user_request=user_request, volunteers=volunteers)

@app.route('/user_request/<int:request_id>')
def user_request(request_id):
    user_request = UserRequest.query.get_or_404(request_id)  # Ensure you're retrieving the user request correctly
    assigned_volunteer = Volunteer.query.get(user_request.assigned_volunteer_id) if user_request.assigned_volunteer_id else None
    return render_template('user_request.html', request=user_request, assigned_volunteer=assigned_volunteer)


@app.route('/functionalities')
def functionalities():
    return render_template('functionalities.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

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
    atexit.register(prompt_and_delete_folders)
    # app.run(host='192.168.29.235') # for hosting the local host will only run on ridhim's desktop (Comment this line and uncomment the one below)
    app.run(debug=True)
