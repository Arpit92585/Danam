from flask import Blueprint, render_template, request, jsonify

main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    # Dummy data for the dashboard
    requests_data = [
        {
            'user': 'John Doe',
            'type': 'Food',
            'location': 'New York, NY',
            'status': 'Pending',
            'lat': 40.7128,
            'lng': -74.0060
        },
        # More dummy requests
    ]
    
    # Passing the data to the template
    return render_template('dashboard.html', requests_data=requests_data)

@main.route('/approve_request', methods=['POST'])
def approve_request():
    user_id = request.json['user_id']
    # Logic to approve the request
    return jsonify({"message": f"Request for {user_id} approved successfully!"})

@main.route('/watch_location', methods=['POST'])
def watch_location():
    user_id = request.json['user_id']
    lat = request.json['lat']
    lng = request.json['lng']
    # Logic to watch the location
    return jsonify({"message": f"Watching location for {user_id}", "lat": lat, "lng": lng})
