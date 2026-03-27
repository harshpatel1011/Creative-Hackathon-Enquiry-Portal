from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db
from email_utils import send_demo_scheduled, send_demo_updated, send_demo_cancelled

demos_bp = Blueprint('demos', __name__)

def get_user(conn, uid):
    return conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


@demos_bp.route('', methods=['GET'])
@jwt_required()
def get_demos():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    query = '''
        SELECT d.*, e.student_name, e.contact, e.email, e.stream, u.name as counselor_name
        FROM demos d JOIN enquiries e ON d.enquiry_id=e.id LEFT JOIN users u ON d.counselor_id=u.id
        WHERE 1=1
    '''
    params = []
    if user['role'] == 'counselor':
        query += ' AND d.counselor_id = ?'
        params.append(uid)
    status = request.args.get('status', '')
    if status:
        query += ' AND d.status = ?'
        params.append(status)
    query += ' ORDER BY d.demo_date ASC, d.demo_time ASC'
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@demos_bp.route('', methods=['POST'])
@jwt_required()
def schedule_demo():
    uid = int(get_jwt_identity())
    data = request.get_json()
    for f in ['enquiry_id', 'demo_date', 'demo_time']:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    conn = get_db()
    user = get_user(conn, uid)
    enquiry = conn.execute("SELECT * FROM enquiries WHERE id=?", (data['enquiry_id'],)).fetchone()
    if not enquiry:
        conn.close()
        return jsonify({'error': 'Enquiry not found'}), 404

    counselor_id = data.get('counselor_id') or uid
    cursor = conn.execute('''
        INSERT INTO demos (enquiry_id, counselor_id, demo_date, demo_time, mode, location, status)
        VALUES (?,?,?,?,?,?,?)
    ''', (data['enquiry_id'], counselor_id, data['demo_date'], data['demo_time'],
          data.get('mode', 'Online'), data.get('location', ''), 'Scheduled'))
    conn.commit()
    demo_id = cursor.lastrowid

    # Send email notification to student
    if enquiry['email']:
        c = conn.execute("SELECT name FROM users WHERE id=?", (counselor_id,)).fetchone()
        counselor_name = c['name'] if c else 'Your Counselor'
        notified = send_demo_scheduled(
            student_name=enquiry['student_name'],
            student_email=enquiry['email'],
            stream=enquiry['stream'],
            demo_date=data['demo_date'],
            demo_time=data['demo_time'],
            counselor_name=counselor_name,
            mode=data.get('mode', 'Online'),
            location=data.get('location', '')
        )
        if notified:
            conn.execute("UPDATE demos SET notified=1 WHERE id=?", (demo_id,))
            conn.commit()

    row = conn.execute('''
        SELECT d.*, e.student_name, e.contact, e.email, e.stream, u.name as counselor_name
        FROM demos d JOIN enquiries e ON d.enquiry_id=e.id LEFT JOIN users u ON d.counselor_id=u.id WHERE d.id=?
    ''', (demo_id,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@demos_bp.route('/<int:did>', methods=['PUT'])
@jwt_required()
def update_demo(did):
    uid = int(get_jwt_identity())
    data = request.get_json()
    conn = get_db()
    user = get_user(conn, uid)
    demo = conn.execute("SELECT * FROM demos WHERE id=?", (did,)).fetchone()
    if not demo:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    if user['role'] == 'counselor' and demo['counselor_id'] != uid:
        conn.close()
        return jsonify({'error': 'Forbidden'}), 403

    new_date   = data.get('demo_date',   demo['demo_date'])
    new_time   = data.get('demo_time',   demo['demo_time'])
    new_mode   = data.get('mode',        demo['mode'])
    new_loc    = data.get('location',    demo['location'])
    new_status = data.get('status',      demo['status'])
    new_cid    = data.get('counselor_id',demo['counselor_id'])

    conn.execute('''
        UPDATE demos SET demo_date=?,demo_time=?,mode=?,location=?,status=?,counselor_id=? WHERE id=?
    ''', (new_date, new_time, new_mode, new_loc, new_status, new_cid, did))
    conn.commit()

    # Fetch enquiry info for email
    row = conn.execute('''
        SELECT d.*, e.student_name, e.contact, e.email, e.stream, u.name as counselor_name
        FROM demos d JOIN enquiries e ON d.enquiry_id=e.id LEFT JOIN users u ON d.counselor_id=u.id WHERE d.id=?
    ''', (did,)).fetchone()

    # Send appropriate email to student
    if row and row['email']:
        if new_status == 'Cancelled':
            send_demo_cancelled(
                student_name=row['student_name'],
                student_email=row['email'],
                stream=row['stream'],
                demo_date=new_date,
                demo_time=new_time
            )
        elif new_status == 'Scheduled':
            # Date/time changed = reschedule notification
            date_changed = (new_date != demo['demo_date']) or (new_time != demo['demo_time'])
            if date_changed:
                send_demo_updated(
                    student_name=row['student_name'],
                    student_email=row['email'],
                    stream=row['stream'],
                    demo_date=new_date,
                    demo_time=new_time,
                    counselor_name=row['counselor_name'] or 'Your Counselor',
                    mode=new_mode,
                    location=new_loc
                )

    conn.close()
    return jsonify(dict(row))


@demos_bp.route('/<int:did>', methods=['DELETE'])
@jwt_required()
def cancel_demo(did):
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)

    row = conn.execute('''
        SELECT d.*, e.student_name, e.email, e.stream
        FROM demos d JOIN enquiries e ON d.enquiry_id=e.id WHERE d.id=?
    ''', (did,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    if user['role'] == 'counselor' and row['counselor_id'] != uid:
        conn.close()
        return jsonify({'error': 'Forbidden'}), 403

    # Send cancellation email before deleting
    if row['email']:
        send_demo_cancelled(
            student_name=row['student_name'],
            student_email=row['email'],
            stream=row['stream'],
            demo_date=row['demo_date'],
            demo_time=row['demo_time']
        )

    conn.execute("DELETE FROM demos WHERE id=?", (did,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Demo cancelled and student notified'})
