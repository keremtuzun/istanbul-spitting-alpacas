from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    # New relationship to store progress data
    progress = db.relationship('Progress', backref='user', lazy=True)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goals = db.Column(db.String(500), nullable=False)
    actuals = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('home.html')

@app.route('/save_progress', methods=['POST'])
@login_required
def save_progress():
    data = request.json
    goals_data = data.get('goals')
    actuals_data = data.get('actuals')
    
    # Check if a progress entry already exists for the user
    existing_progress = Progress.query.filter_by(user_id=current_user.id).first()
    
    if existing_progress:
        existing_progress.goals = goals_data
        existing_progress.actuals = actuals_data
    else:
        new_progress = Progress(goals=goals_data, actuals=actuals_data, user_id=current_user.id)
        db.session.add(new_progress)
    
    db.session.commit()
    return jsonify({'success': True}), 200

@app.route('/get_progress', methods=['GET'])
@login_required
def get_progress():
    progress = Progress.query.filter_by(user_id=current_user.id).first()
    if progress:
        return jsonify({
            'goals': progress.goals,
            'actuals': progress.actuals
        }), 200
    else:
        return jsonify({'goals': '[]', 'actuals': '[]'}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)