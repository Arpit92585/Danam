class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    assigned_volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'))  # Foreign key reference
    assigned_volunteer = db.relationship('Volunteer', backref='requests')

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    requests = db.relationship('UserRequest', backref='volunteer', lazy=True)
