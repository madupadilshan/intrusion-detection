from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Requests

# 🔐 **Security Configuration**
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Change for MySQL/PostgreSQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Change this in production!

# Set Admin Password Securely (Best Practice: Store in .env file)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "SuperSecureAdmin123")

# Initialize Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# ✅ **User Model**
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ✅ **AlertLog Model**
class AlertLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # Type of attack (IoT, Cyber, Traditional)
    message = db.Column(db.String(200), nullable=False)  # The alert message
    severity = db.Column(db.String(20), nullable=False)  # Severity (critical, high, low, etc.)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Time of alert

    def __repr__(self):
        return f"<AlertLog {self.type} - {self.severity} at {self.timestamp}>"

# 🔄 **Create Database (If Not Exists)**
with app.app_context():
    db.create_all()

# 🚀 **User Registration (Requires Admin Password)**
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # 🔐 **Admin Password Validation**
    if data.get("admin_password") != ADMIN_PASSWORD:
        return jsonify({'message': '❌ Invalid admin password. Contact an administrator.'}), 403

    # ✅ **Check if Username or Email Already Exists**
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '❌ Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '❌ Email already exists'}), 400

    # 🔑 **Hash Password & Save User**
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '✅ User registered successfully'}), 201

# 🔑 **User Login**
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'message': '✅ Login successful', 'token': access_token}), 200

    return jsonify({'message': '❌ Invalid username or password'}), 401

# 🔐 **Protected Route (Only Accessible After Login)**
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'🔒 Hello, user {current_user}!'}), 200

# 🚨 **Log Alert (New Alert)**
@app.route('/log_alert', methods=['POST'])
def log_alert():
    data = request.get_json()
    
    # Save an alert log
    alert_type = data.get('type')  # IoT, Cyber, Traditional
    alert_message = data.get('message')
    alert_severity = data.get('severity')

    # Create a new alert log entry
    new_alert = AlertLog(type=alert_type, message=alert_message, severity=alert_severity)

    # Save to database
    db.session.add(new_alert)
    db.session.commit()

    return jsonify({'message': '✅ Alert logged successfully!'}), 201

# 🔄 **Fetch Alerts by Date Range**
@app.route('/alerts', methods=['GET'])
def get_alerts():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Convert string dates to datetime objects
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': '❌ Invalid date format. Use YYYY-MM-DD.'}), 400

    # Query the database for alerts within the time range
    alerts = AlertLog.query.filter(AlertLog.timestamp >= start_date, AlertLog.timestamp <= end_date).all()

    if not alerts:
        return jsonify({'message': '❌ No alerts found within the given date range.'}), 404

    # Return the list of alerts as JSON
    alert_list = [{
        'type': alert.type,
        'message': alert.message,
        'severity': alert.severity,
        'timestamp': alert.timestamp
    } for alert in alerts]

    return jsonify({'alerts': alert_list}), 200

# 🔄 **Health Check Route**
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🚀 Intrusion Detection System Backend is Running", "status": "running"}), 200

# 🚀 **Run Flask App on Port 5002**
if __name__ == '__main__':
    app.run(debug=True, port=5002)
