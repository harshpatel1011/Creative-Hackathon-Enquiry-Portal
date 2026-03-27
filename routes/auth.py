from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt, re, secrets
from datetime import datetime, timedelta
from database import get_db
from email_utils import (
    send_verification_email,
    send_welcome_email,
    send_admin_notification
)

auth_bp = Blueprint('auth', __name__)

# ── Helpers ─────────────────────────────────────────────────────
def _hash(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def _check(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def valid_email(e):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', e) is not None

def _gen_token():
    return secrets.token_urlsafe(48)

def _token_expiry():
    return (datetime.utcnow() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')


# ── Login ────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if not user or not _check(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Block unverified users
    if not user['is_email_verified']:
        return jsonify({
            'error': 'Please verify your email before logging in. Check your inbox for the verification link.',
            'unverified': True,
            'email': email
        }), 403

    # Block deactivated users
    if not user['is_active']:
        return jsonify({'error': 'Your account has been deactivated. Contact admin.'}), 403

    token = create_access_token(identity=str(user['id']))
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'role': user['role']}
    })


# ── Register ─────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    data     = request.get_json() or {}
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone    = data.get('phone', '').strip()

    # Validation
    errors = {}
    if not name or len(name) < 2:
        errors['name'] = 'Full name must be at least 2 characters'
    if not email or not valid_email(email):
        errors['email'] = 'Enter a valid email address'
    if not password or len(password) < 6:
        errors['password'] = 'Password must be at least 6 characters'
    if errors:
        return jsonify({'error': 'Validation failed', 'fields': errors}), 400

    conn = get_db()

    # Duplicate email check
    existing = conn.execute("SELECT id, is_email_verified FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        if existing['is_email_verified']:
            conn.close()
            return jsonify({'error': 'An account with this email already exists'}), 409
        else:
            # Resend verification for unverified duplicate
            token    = _gen_token()
            expiry   = _token_expiry()
            now_str  = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute(
                "UPDATE users SET verification_token=?, verification_token_expiry=?, last_verification_sent=? WHERE email=?",
                (token, expiry, now_str, email)
            )
            conn.commit()
            conn.close()
            send_verification_email(name, email, token)
            return jsonify({
                'message': 'A new verification email has been sent. Please check your inbox.',
                'verify_pending': True
            }), 200

    # Create user (inactive, unverified)
    token   = _gen_token()
    expiry  = _token_expiry()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    cursor = conn.execute(
        """INSERT INTO users
           (name, email, password_hash, role, phone, is_active, is_email_verified,
            verification_token, verification_token_expiry, last_verification_sent)
           VALUES (?,?,?,?,?,0,0,?,?,?)""",
        (name, email, _hash(password), 'counselor', phone, token, expiry, now_str)
    )
    conn.commit()
    conn.close()

    # Send emails (non-blocking – failures logged, not raised)
    send_verification_email(name, email, token)
    send_admin_notification(name, email, phone)

    return jsonify({
        'message': f'Account created! A verification email has been sent to {email}. Please verify to log in.',
        'verify_pending': True,
        'email': email
    }), 201


# ── Verify Email ─────────────────────────────────────────────────
@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE verification_token=?", (token,)
    ).fetchone()

    if not user:
        conn.close()
        return jsonify({'success': False, 'reason': 'invalid'}), 404

    # Check expiry
    if user['verification_token_expiry']:
        try:
            expiry = datetime.strptime(user['verification_token_expiry'], '%Y-%m-%d %H:%M:%S')
            if datetime.utcnow() > expiry:
                conn.close()
                return jsonify({'success': False, 'reason': 'expired'}), 410
        except Exception:
            pass

    # Activate user
    conn.execute(
        """UPDATE users
           SET is_email_verified=1, is_active=1,
               verification_token=NULL, verification_token_expiry=NULL
           WHERE id=?""",
        (user['id'],)
    )
    conn.commit()
    conn.close()

    send_welcome_email(user['name'], user['email'])
    return jsonify({'success': True, 'message': 'Email verified successfully!'}), 200


# ── Resend Verification ──────────────────────────────────────────
@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    data  = request.get_json() or {}
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

    if not user:
        # Security: don't leak whether email exists
        conn.close()
        return jsonify({'message': 'If that email exists, a verification link has been sent.'}), 200

    if user['is_email_verified']:
        conn.close()
        return jsonify({'message': 'Your email is already verified. You can log in.'}), 200

    # Rate limit: 1 resend per 3 minutes
    if user['last_verification_sent']:
        try:
            last = datetime.strptime(user['last_verification_sent'], '%Y-%m-%d %H:%M:%S')
            wait = (last + timedelta(minutes=3)) - datetime.utcnow()
            if wait.total_seconds() > 0:
                secs = int(wait.total_seconds())
                conn.close()
                return jsonify({
                    'error': f'Please wait {secs} seconds before requesting another email.',
                    'cooldown': secs
                }), 429
        except Exception:
            pass

    # Issue new token
    token   = _gen_token()
    expiry  = _token_expiry()
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    conn.execute(
        "UPDATE users SET verification_token=?, verification_token_expiry=?, last_verification_sent=? WHERE id=?",
        (token, expiry, now_str, user['id'])
    )
    conn.commit()
    conn.close()

    send_verification_email(user['name'], email, token)
    return jsonify({'message': 'Verification email resent. Please check your inbox.'}), 200


# ── Me ────────────────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid  = int(get_jwt_identity())
    conn = get_db()
    user = conn.execute("SELECT id,name,email,role FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    return jsonify({'error': 'User not found'}), 404
