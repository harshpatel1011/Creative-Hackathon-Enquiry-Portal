import sqlite3
import bcrypt
import os

DB_PATH = 'infinity_coders.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _migrate(conn):
    """Run safe ALTER TABLE migrations – skips if column already exists."""
    cursor = conn.cursor()
    # Email verification columns
    migrations = [
        "ALTER TABLE users ADD COLUMN is_email_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN verification_token TEXT",
        "ALTER TABLE users ADD COLUMN verification_token_expiry DATETIME",
        "ALTER TABLE users ADD COLUMN last_verification_sent DATETIME",
    ]
    for sql in migrations:
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception:
            pass  # Column already exists

    # Ensure seeded (admin/counselor) users are pre-verified
    cursor.execute("""
        UPDATE users SET is_email_verified = 1
        WHERE is_email_verified = 0
        AND email IN ('admin@infinitycoders.com','priya@infinitycoders.com')
    """)
    conn.commit()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'counselor')),
            phone TEXT,
            is_active INTEGER DEFAULT 0,
            is_email_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            verification_token_expiry DATETIME,
            last_verification_sent DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT,
            education TEXT,
            stream TEXT NOT NULL,
            source TEXT DEFAULT 'Website',
            status TEXT DEFAULT 'New' CHECK(status IN ('New','Contacted','Interested','Not Interested','Converted')),
            counselor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            followup_date DATE,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS followup_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id INTEGER NOT NULL REFERENCES enquiries(id) ON DELETE CASCADE,
            counselor_id INTEGER REFERENCES users(id),
            note TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS demos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id INTEGER NOT NULL REFERENCES enquiries(id) ON DELETE CASCADE,
            counselor_id INTEGER REFERENCES users(id),
            demo_date DATE NOT NULL,
            demo_time TEXT NOT NULL,
            mode TEXT DEFAULT 'Online',
            location TEXT,
            status TEXT DEFAULT 'Scheduled' CHECK(status IN ('Scheduled','Completed','Cancelled')),
            notified INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Run migrations on existing DB (adds new columns safely)
    _migrate(conn)

    # Seed default admin if not exists
    existing = cursor.execute("SELECT id FROM users WHERE email = 'admin@infinitycoders.com'").fetchone()
    if not existing:
        pw_hash = bcrypt.hashpw('Admin@123'.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, is_active, is_email_verified) VALUES (?, ?, ?, ?, 1, 1)",
            ('Administrator', 'admin@infinitycoders.com', pw_hash, 'admin')
        )
        # Seed sample counselor
        pw_hash2 = bcrypt.hashpw('Counselor@123'.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, phone, is_active, is_email_verified) VALUES (?, ?, ?, ?, ?, 1, 1)",
            ('Priya Sharma', 'priya@infinitycoders.com', pw_hash2, 'counselor', '9876543210')
        )
        # Seed sample enquiries
        sample_enquiries = [
            ('Rahul Verma', '9876543210', 'rahul@gmail.com', 'BSc IT', 'Web Development', 'Website', 'Interested', 2),
            ('Sneha Patel', '8765432109', 'sneha@gmail.com', 'BCA', 'Data Science', 'Social Media', 'New', 2),
            ('Amit Kumar', '7654321098', 'amit@gmail.com', 'BCS', 'Python Full Stack', 'Walk-in', 'Contacted', 2),
            ('Pooja Singh', '6543210987', 'pooja@gmail.com', 'MCA', 'UI / UX Design', 'Referral', 'Converted', 2),
            ('Rohan Das', '5432109876', 'rohan@gmail.com', 'BSc', 'Digital Marketing', 'Website', 'Not Interested', None),
            ('Anjali Mehta', '4321098765', 'anjali@gmail.com', 'BE', 'Java Full Stack', 'Walk-in', 'New', 2),
            ('Karan Shah', '3210987654', 'karan@gmail.com', 'BSc CS', 'Video Editing', 'Social Media', 'Interested', 2),
            ('Deepa Nair', '2109876543', 'deepa@gmail.com', 'MBA', 'Data Science', 'Website', 'Contacted', 2),
        ]
        for e in sample_enquiries:
            cursor.execute(
                "INSERT INTO enquiries (student_name, contact, email, education, stream, source, status, counselor_id) VALUES (?,?,?,?,?,?,?,?)", e
            )
        conn.commit()
        print("[DB] Database seeded with default admin, counselor and sample data.")
    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}")
