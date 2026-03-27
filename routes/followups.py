from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db

followups_bp = Blueprint('followups', __name__)

def get_user(conn, uid):
    return conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

@followups_bp.route('/<int:enquiry_id>', methods=['GET'])
@jwt_required()
def get_followups(enquiry_id):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] == 'counselor':
        enq = conn.execute("SELECT counselor_id FROM enquiries WHERE id=?", (enquiry_id,)).fetchone()
        if not enq or enq['counselor_id'] != uid:
            conn.close()
            return jsonify({'error': 'Forbidden'}), 403
    rows = conn.execute('''
        SELECT f.*, u.name as counselor_name 
        FROM followup_notes f 
        LEFT JOIN users u ON f.counselor_id=u.id
        WHERE f.enquiry_id=? 
        ORDER BY f.created_at DESC
    ''', (enquiry_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@followups_bp.route('', methods=['POST'])
@jwt_required()
def add_followup():
    uid = int(get_jwt_identity())
    data = request.get_json()
    enquiry_id = data.get('enquiry_id')
    note = data.get('note', '').strip()
    if not enquiry_id or not note:
        return jsonify({'error': 'enquiry_id and note are required'}), 400
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] == 'counselor':
        enq = conn.execute("SELECT counselor_id FROM enquiries WHERE id=?", (enquiry_id,)).fetchone()
        if not enq or enq['counselor_id'] != uid:
            conn.close()
            return jsonify({'error': 'Forbidden'}), 403
    cursor = conn.execute(
        "INSERT INTO followup_notes (enquiry_id, counselor_id, note) VALUES (?,?,?)",
        (enquiry_id, uid, note)
    )
    conn.commit()
    row = conn.execute('''
        SELECT f.*, u.name as counselor_name 
        FROM followup_notes f LEFT JOIN users u ON f.counselor_id=u.id 
        WHERE f.id=?
    ''', (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@followups_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_followup(note_id):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    note = conn.execute("SELECT * FROM followup_notes WHERE id=?", (note_id,)).fetchone()
    if not note:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    if user['role'] != 'admin' and note['counselor_id'] != uid:
        conn.close()
        return jsonify({'error': 'Forbidden'}), 403
    conn.execute("DELETE FROM followup_notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Deleted'})
