from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
from email_utils import send_enquiry_confirmation
import csv
import io

enquiries_bp = Blueprint('enquiries', __name__)

def get_user(conn, user_id):
    return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

@enquiries_bp.route('', methods=['GET'])
@jwt_required()
def get_enquiries():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    base_query = '''
        SELECT e.*, u.name as counselor_name 
        FROM enquiries e 
        LEFT JOIN users u ON e.counselor_id = u.id
        WHERE 1=1
    '''
    params = []
    if user['role'] == 'counselor':
        base_query += ' AND e.counselor_id = ?'
        params.append(uid)
    search = request.args.get('search', '')
    if search:
        base_query += ' AND (e.student_name LIKE ? OR e.contact LIKE ? OR e.email LIKE ?)'
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    status = request.args.get('status', '')
    if status:
        base_query += ' AND e.status = ?'
        params.append(status)
    stream = request.args.get('stream', '')
    if stream:
        base_query += ' AND e.stream = ?'
        params.append(stream)
    counselor_id = request.args.get('counselor_id', '')
    if counselor_id and user['role'] == 'admin':
        base_query += ' AND e.counselor_id = ?'
        params.append(counselor_id)
    base_query += ' ORDER BY e.created_at DESC'
    rows = conn.execute(base_query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@enquiries_bp.route('', methods=['POST'])
@jwt_required()
def add_enquiry():
    uid = int(get_jwt_identity())
    data = request.get_json()
    required = ['student_name', 'contact', 'stream']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400
    conn = get_db()
    user = get_user(conn, uid)
    counselor_id = data.get('counselor_id') or (uid if user['role'] == 'counselor' else None)

    cursor = conn.execute('''
        INSERT INTO enquiries (student_name, contact, email, education, stream, source, status, counselor_id, followup_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['student_name'], data['contact'], data.get('email', ''),
        data.get('education', ''), data['stream'], data.get('source', 'Website'),
        data.get('status', 'New'), counselor_id,
        data.get('followup_date'), data.get('notes', '')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    row = conn.execute("SELECT e.*, u.name as counselor_name FROM enquiries e LEFT JOIN users u ON e.counselor_id=u.id WHERE e.id=?", (new_id,)).fetchone()
    conn.close()

    # Send confirmation email to student if email provided
    student_email = data.get('email', '')
    if student_email:
        send_enquiry_confirmation(
            student_name=data['student_name'],
            student_email=student_email,
            stream=data['stream'],
            counselor_name=row['counselor_name'] or '',
            followup_date=data.get('followup_date', '')
        )

    return jsonify(dict(row)), 201

@enquiries_bp.route('/<int:eid>', methods=['GET'])
@jwt_required()
def get_enquiry(eid):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    row = conn.execute("SELECT e.*, u.name as counselor_name FROM enquiries e LEFT JOIN users u ON e.counselor_id=u.id WHERE e.id=?", (eid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    if user['role'] == 'counselor' and row['counselor_id'] != uid:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(dict(row))

@enquiries_bp.route('/<int:eid>', methods=['PUT'])
@jwt_required()
def update_enquiry(eid):
    uid = int(get_jwt_identity())
    data = request.get_json()
    conn = get_db()
    user = get_user(conn, uid)
    row = conn.execute("SELECT * FROM enquiries WHERE id=?", (eid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    if user['role'] == 'counselor' and row['counselor_id'] != uid:
        conn.close()
        return jsonify({'error': 'Forbidden'}), 403
    conn.execute('''
        UPDATE enquiries SET 
            student_name=?, contact=?, email=?, education=?, stream=?, source=?,
            status=?, counselor_id=?, followup_date=?, notes=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    ''', (
        data.get('student_name', row['student_name']),
        data.get('contact', row['contact']),
        data.get('email', row['email']),
        data.get('education', row['education']),
        data.get('stream', row['stream']),
        data.get('source', row['source']),
        data.get('status', row['status']),
        data.get('counselor_id', row['counselor_id']),
        data.get('followup_date', row['followup_date']),
        data.get('notes', row['notes']),
        eid
    ))
    conn.commit()
    updated = conn.execute("SELECT e.*, u.name as counselor_name FROM enquiries e LEFT JOIN users u ON e.counselor_id=u.id WHERE e.id=?", (eid,)).fetchone()
    conn.close()
    return jsonify(dict(updated))

@enquiries_bp.route('/<int:eid>', methods=['DELETE'])
@jwt_required()
def delete_enquiry(eid):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Admin only'}), 403
    row = conn.execute("SELECT id FROM enquiries WHERE id=?", (eid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    conn.execute("DELETE FROM enquiries WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Deleted successfully'})

@enquiries_bp.route('/export/csv', methods=['GET'])
@jwt_required()
def export_csv():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] != 'admin':
        conn.close()
        return jsonify({'error': 'Admin only'}), 403
    rows = conn.execute('''
        SELECT e.id, e.student_name, e.contact, e.email, e.education, e.stream, e.source,
               e.status, u.name as counselor, e.followup_date, e.notes, e.created_at
        FROM enquiries e LEFT JOIN users u ON e.counselor_id=u.id
        ORDER BY e.created_at DESC
    ''').fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID','Student Name','Contact','Email','Education','Stream','Source','Status','Counselor','Follow-up Date','Notes','Created At'])
    for r in rows:
        writer.writerow(list(r))
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=enquiries_export.csv'}
    )
