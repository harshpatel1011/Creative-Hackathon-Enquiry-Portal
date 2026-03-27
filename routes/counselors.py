from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
import bcrypt

counselors_bp = Blueprint('counselors', __name__)

def get_user(conn, uid):
    return conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

@counselors_bp.route('', methods=['GET'])
@jwt_required()
def get_counselors():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Admin only'}), 403
    rows = conn.execute('''
        SELECT u.id, u.name, u.email, u.phone, u.role, u.is_active, u.created_at,
               COUNT(e.id) as enquiry_count
        FROM users u
        LEFT JOIN enquiries e ON e.counselor_id=u.id
        WHERE u.role='counselor'
        GROUP BY u.id
        ORDER BY u.name
    ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@counselors_bp.route('', methods=['POST'])
@jwt_required()
def create_counselor():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Admin only'}), 403
    data = request.get_json()
    required = ['name', 'email', 'password']
    for f in required:
        if not data.get(f):
            conn.close()
            return jsonify({'error': f'{f} is required'}), 400
    existing = conn.execute("SELECT id FROM users WHERE email=?", (data['email'],)).fetchone()
    if existing:
        conn.close()
        return jsonify({'error': 'Email already registered'}), 409
    pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash, role, phone) VALUES (?,?,?,?,?)",
        (data['name'], data['email'], pw_hash, 'counselor', data.get('phone', ''))
    )
    conn.commit()
    row = conn.execute("SELECT id,name,email,phone,role,is_active,created_at FROM users WHERE id=?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@counselors_bp.route('/<int:uid2>', methods=['PUT'])
@jwt_required()
def update_counselor(uid2):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Admin only'}), 403
    data = request.get_json()
    target = conn.execute("SELECT * FROM users WHERE id=? AND role='counselor'", (uid2,)).fetchone()
    if not target:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    if data.get('password'):
        pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
        conn.execute("UPDATE users SET name=?,email=?,phone=?,is_active=?,password_hash=? WHERE id=?",
                     (data.get('name',target['name']),data.get('email',target['email']),data.get('phone',target['phone']),data.get('is_active',target['is_active']),pw_hash,uid2))
    else:
        conn.execute("UPDATE users SET name=?,email=?,phone=?,is_active=? WHERE id=?",
                     (data.get('name',target['name']),data.get('email',target['email']),data.get('phone',target['phone']),data.get('is_active',target['is_active']),uid2))
    conn.commit()
    row = conn.execute("SELECT id,name,email,phone,role,is_active,created_at FROM users WHERE id=?", (uid2,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@counselors_bp.route('/<int:uid2>', methods=['DELETE'])
@jwt_required()
def delete_counselor(uid2):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Admin only'}), 403
    target = conn.execute("SELECT id FROM users WHERE id=? AND role='counselor'", (uid2,)).fetchone()
    if not target:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    conn.execute("DELETE FROM users WHERE id=?", (uid2,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Counselor removed'})
