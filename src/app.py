import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from forms import UserRequestForm, VolunteerForm  # Ensure VolunteerForm is imported
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///requests.db'
db = SQLAlchemy(app)




# Model for User Requests
class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)

# Model for Volunteers
class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

# Route for Homepage
@app.route('/')
def homepage():
    requests = UserRequest.query.all()
    return render_template('homepage.html', requests=requests)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


def GeminiFunction(prompt):
    # Replace with the actual call to Google Gemini API
    # Below is a placeholder for demonstration purposes
    response = requests.post('https://example.com/gemini-api', json={'prompt': prompt})
    return response.json().get('text', 'Error generating response')

@app.route('/resume/create', methods=['POST'])
def create_resume():
    # Getting form fields from the request
    fullName = request.form.get('fullName')
    email = request.form.get('email')
    linkedin = request.form.get('linkedin')
    education = request.form.get('education')
    experience = request.form.get('experience')
    skills = request.form.get('skills')
    extracurricular = request.form.get('extracurricular')
    currentPosition = request.form.get('currentPosition')
    currentLength = request.form.get('currentLength')
    currentTechnologies = request.form.get('currentTechnologies')
    workHistory = json.loads(request.form.get('workHistory'))

    # Save uploaded headshot
    headshot = request.files['headshotImage']
    filename = secure_filename(headshot.filename)
    headshot.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    image_url = f"/uploads/{filename}"

    # Generate AI content
    prompt1 = f"I am writing a resume. My details are \n name: {fullName}, \n role: {currentPosition} ({currentLength} years). \n I work with the following technologies: {currentTechnologies}."
    objective = GeminiFunction(prompt1)

    # ... Create other prompts similarly

    # Assemble the response data
    result = {
        "fullName": fullName,
        "email": email,
        "linkedin": linkedin,
        "education": education,
        "experience": experience,
        "skills": skills,
        "extracurricular": extracurricular,
        "currentPosition": currentPosition,
        "currentLength": currentLength,
        "currentTechnologies": currentTechnologies,
        "image_url": image_url,
        "workHistory": workHistory,
        "objective": objective
    }
    return jsonify({"message": "Resume created successfully", "data": result})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(port=4000, debug=True)
