from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_very_secret_key_here'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define the database models (tables)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    progress = db.relationship('Progress', backref='author', uselist=False, lazy=True)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

# API endpoint for user registration
@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(email=data['email'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

# API endpoint for user login
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        progress_record = Progress.query.filter_by(user_id=user.id).first()
        return jsonify({
            "message": "Login successful!",
            "userId": user.id,
            "progress": progress_record.data if progress_record else None
        }), 200
    return jsonify({"message": "Login failed."}), 401

# API endpoint to save user progress
@app.route("/save-progress", methods=['POST'])
def save_progress():
    data = request.get_json()
    user_id = data.get('userId')
    progress_data = data.get('progress')

    progress_record = Progress.query.filter_by(user_id=user_id).first()
    if progress_record:
        progress_record.data = progress_data
    else:
        new_progress = Progress(user_id=user_id, data=progress_data)
        db.session.add(new_progress)
        
    db.session.commit()
    return jsonify({"message": "Progress saved successfully!"}), 200

# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create or update your database
    app.run(debug=True)