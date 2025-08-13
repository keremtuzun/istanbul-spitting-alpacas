from flask import Flask, request, jsonify, session
from flask_cors import CORS
import uuid # For generating user IDs

app = Flask(__name__)
CORS(app, supports_credentials=True) # Enable CORS for frontend communication
app.secret_key = 'your_secret_key_here' # Replace with a strong secret key

# In-memory storage for demonstration purposes
# In a real app, use a database (e.g., SQLite, PostgreSQL)
users = {} # {email: {password: '...', user_id: '...', progress: {goals: {}, actuals: {}}}}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('username') # Changed from 'email' to 'username' to match frontend script
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if email in users:
        return jsonify({'message': 'User already exists'}), 409

    user_id = str(uuid.uuid4())
    users[email] = {
        'password': password,
        'user_id': user_id,
        'progress': {
            'goals': {'Notes': 0, 'Debate': 0, 'Quiz': 0, 'PracticeLab': 0, 'Documents': 0, 'Flashcards': 0},
            'actuals': {'Notes': 0, 'Debate': 0, 'Quiz': 0, 'PracticeLab': 0, 'Documents': 0, 'Flashcards': 0}
        }
    }
    return jsonify({'message': 'User registered successfully', 'userId': user_id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('username') # Changed from 'email' to 'username' to match frontend script
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = users.get(email)
    if user and user['password'] == password:
        session['user_id'] = user['user_id'] # Store user_id in session
        session['user_email'] = email # Store user_email in session
        return jsonify({
            'message': 'Login successful',
            'userId': user['user_id'],
            'progress': user['progress'] # Send progress data on login
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/save_progress', methods=['POST'])
def save_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    data = request.json
    goals = data.get('goals')
    actuals = data.get('actuals')
    
    for email, user_data in users.items():
        if user_data['user_id'] == user_id:
            user_data['progress'] = {
                'goals': goals,
                'actuals': actuals
            }
            return jsonify({"message": "Progress saved successfully"}), 200
            
    return jsonify({"error": "User not found"}), 404

@app.route('/get_progress', methods=['GET'])
def get_progress():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
        
    for email, user_data in users.items():
        if user_data['user_id'] == user_id:
            progress = user_data.get('progress', {'goals': {}, 'actuals': {}})
            return jsonify(progress), 200
            
    return jsonify({"error": "User not found"}), 404

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return jsonify({'message': 'User is logged in'}), 200
    return jsonify({'message': 'User is not logged in'}), 401

if __name__ == '__main__':
    app.run(debug=True)

