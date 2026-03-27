from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db

analytics_bp = Blueprint('analytics', __name__)

def get_user(conn, uid):
    return conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()

def count_enquiries(conn, is_counselor, uid, extra_where='', extra_params=None):
    """Helper to count enquiries with optional counselor filter and extra condition."""
    params = []
    where_parts = []
    if is_counselor:
        where_parts.append("counselor_id=?")
        params.append(uid)
    if extra_where:
        where_parts.append(extra_where)
        if extra_params:
            params.extend(extra_params)
    where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
    sql = f"SELECT COUNT(*) FROM enquiries {where}"
    return conn.execute(sql, params).fetchone()[0]

@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    is_c = user['role'] == 'counselor'

    total = count_enquiries(conn, is_c, uid)
    converted = count_enquiries(conn, is_c, uid, "status='Converted'")
    interested = count_enquiries(conn, is_c, uid, "status='Interested'")
    new_count = count_enquiries(conn, is_c, uid, "status='New'")
    contacted = count_enquiries(conn, is_c, uid, "status='Contacted'")
    not_interested = count_enquiries(conn, is_c, uid, "status='Not Interested'")
    conversion_rate = round((converted / total * 100) if total > 0 else 0, 1)

    if is_c:
        demos_today = conn.execute(
            "SELECT COUNT(*) FROM demos WHERE counselor_id=? AND demo_date=date('now')", [uid]
        ).fetchone()[0]
    else:
        demos_today = conn.execute(
            "SELECT COUNT(*) FROM demos WHERE demo_date=date('now')"
        ).fetchone()[0]

    conn.close()
    return jsonify({
        'total': total, 'converted': converted, 'interested': interested,
        'new': new_count, 'contacted': contacted, 'not_interested': not_interested,
        'conversion_rate': conversion_rate, 'demos_today': demos_today
    })

@analytics_bp.route('/stream-wise', methods=['GET'])
@jwt_required()
def stream_wise():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] == 'counselor':
        rows = conn.execute("SELECT stream, COUNT(*) as count FROM enquiries WHERE counselor_id=? GROUP BY stream ORDER BY count DESC", [uid]).fetchall()
    else:
        rows = conn.execute("SELECT stream, COUNT(*) as count FROM enquiries GROUP BY stream ORDER BY count DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@analytics_bp.route('/monthly', methods=['GET'])
@jwt_required()
def monthly():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] == 'counselor':
        rows = conn.execute('''
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count,
                   SUM(CASE WHEN status='Converted' THEN 1 ELSE 0 END) as converted
            FROM enquiries WHERE counselor_id=?
            GROUP BY month ORDER BY month DESC LIMIT 12
        ''', [uid]).fetchall()
    else:
        rows = conn.execute('''
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count,
                   SUM(CASE WHEN status='Converted' THEN 1 ELSE 0 END) as converted
            FROM enquiries GROUP BY month ORDER BY month DESC LIMIT 12
        ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in reversed(rows)])

@analytics_bp.route('/status-wise', methods=['GET'])
@jwt_required()
def status_wise():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] == 'counselor':
        rows = conn.execute("SELECT status, COUNT(*) as count FROM enquiries WHERE counselor_id=? GROUP BY status", [uid]).fetchall()
    else:
        rows = conn.execute("SELECT status, COUNT(*) as count FROM enquiries GROUP BY status").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@analytics_bp.route('/recent-enquiries', methods=['GET'])
@jwt_required()
def recent_enquiries():
    uid = int(get_jwt_identity())
    conn = get_db()
    user = get_user(conn, uid)
    if user['role'] == 'counselor':
        rows = conn.execute('''
            SELECT e.id, e.student_name, e.stream, e.status, e.created_at, u.name as counselor_name
            FROM enquiries e LEFT JOIN users u ON e.counselor_id=u.id
            WHERE e.counselor_id=? ORDER BY e.created_at DESC LIMIT 10
        ''', [uid]).fetchall()
    else:
        rows = conn.execute('''
            SELECT e.id, e.student_name, e.stream, e.status, e.created_at, u.name as counselor_name
            FROM enquiries e LEFT JOIN users u ON e.counselor_id=u.id
            ORDER BY e.created_at DESC LIMIT 10
        ''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
