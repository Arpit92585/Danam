from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for simplicity (use a database in production)
users = []

def create_app():
    app.config.from_pyfile('config.py')
    
    @app.route('/add_user', methods=['POST'])
    def add_user():
        data = request.json
        users.append(data)
        return jsonify({"message": "User added successfully!"}), 200
    
    @app.route('/get_users', methods=['GET'])
    def get_users():
        return jsonify(users), 200

    return app
