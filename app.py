from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# Load .env file FIRST before anything else
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
except Exception:
    pass

from database import init_db
from routes.auth import auth_bp
from routes.enquiries import enquiries_bp
from routes.followups import followups_bp
from routes.demos import demos_bp
from routes.counselors import counselors_bp
from routes.analytics import analytics_bp

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

app.config['JWT_SECRET_KEY'] = 'infinity-coders-secret-2024-hackathon'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(enquiries_bp, url_prefix='/api/enquiries')
app.register_blueprint(followups_bp, url_prefix='/api/followups')
app.register_blueprint(demos_bp, url_prefix='/api/demos')
app.register_blueprint(counselors_bp, url_prefix='/api/counselors')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('public', path)):
        return send_from_directory('public', path)
    return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("  Infinity Coders - Enquiry Portal")
    print("  Running at: http://localhost:5000")
    print("  Admin: admin@infinitycoders.com / Admin@123")
    print("=" * 50)
    app.run(debug=True, port=5000)
