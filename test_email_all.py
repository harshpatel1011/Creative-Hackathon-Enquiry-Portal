"""
test_email_all.py - Infinity Coders: Full Email System Test v2.0
================================================================
Tests all 7 email types from email_utils.py and reports results.
Usage: python test_email_all.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from email_utils import (
    send_verification_email,
    send_welcome_email,
    send_admin_notification,
    send_enquiry_confirmation,
    send_demo_scheduled,
    send_demo_updated,
    send_demo_cancelled,
    EMAIL_SENDER, EMAIL_PASSWORD,
    ADMIN_EMAIL,
)

RECIPIENT  = "shlksuthar@gmail.com"
FAKE_TOKEN = "test-verify-token-abc123xyz456"

TESTS = [
    {
        "id": 1,
        "name": "Email Verification",
        "fn": lambda: send_verification_email(
            user_name="Shlok Suthar",
            user_email=RECIPIENT,
            token=FAKE_TOKEN,
        ),
    },
    {
        "id": 2,
        "name": "Welcome Email (after verification)",
        "fn": lambda: send_welcome_email(
            user_name="Shlok Suthar",
            user_email=RECIPIENT,
        ),
    },
    {
        "id": 3,
        "name": "Admin Notification (new signup) --> admin@infinitycoders.com",
        "fn": lambda: send_admin_notification(
            user_name="Shlok Suthar",
            user_email=RECIPIENT,
            user_phone="+91 98765 43210",
        ),
    },
    {
        "id": 4,
        "name": "Enquiry Confirmation (student)",
        "fn": lambda: send_enquiry_confirmation(
            student_name="Shlok Suthar",
            student_email=RECIPIENT,
            stream="Full Stack Web Development",
            counselor_name="Paresh Patel",
            followup_date="25 March 2026",
        ),
    },
    {
        "id": 5,
        "name": "Demo Scheduled",
        "fn": lambda: send_demo_scheduled(
            student_name="Shlok Suthar",
            student_email=RECIPIENT,
            stream="Full Stack Web Development",
            demo_date="28 March 2026",
            demo_time="11:00 AM",
            counselor_name="Paresh Patel",
            mode="Online",
            location="https://meet.google.com/test-demo-link",
        ),
    },
    {
        "id": 6,
        "name": "Demo Rescheduled / Updated",
        "fn": lambda: send_demo_updated(
            student_name="Shlok Suthar",
            student_email=RECIPIENT,
            stream="Full Stack Web Development",
            demo_date="30 March 2026",
            demo_time="2:00 PM",
            counselor_name="Paresh Patel",
            mode="Online",
            location="https://meet.google.com/test-demo-link",
        ),
    },
    {
        "id": 7,
        "name": "Demo Cancelled",
        "fn": lambda: send_demo_cancelled(
            student_name="Shlok Suthar",
            student_email=RECIPIENT,
            stream="Full Stack Web Development",
            demo_date="30 March 2026",
            demo_time="2:00 PM",
        ),
    },
]

# ── Run tests ─────────────────────────────────────────────────────────────────
sep = "=" * 62
print(sep)
print("  Infinity Coders - Full Email System Test v2.0")
print(sep)
print(f"  Sender      : {EMAIL_SENDER}")
print(f"  Password    : {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else '(not set)'}")
print(f"  Recipient   : {RECIPIENT}")
print(f"  Admin Email : {ADMIN_EMAIL}")
print(f"  Total Tests : {len(TESTS)}")
print(sep)
print()

passed = 0
failed = 0
results = []

for test in TESTS:
    label = f"  [{test['id']}/{len(TESTS)}] {test['name']}"
    print(f"{label}")
    print(f"         ...", end="", flush=True)
    try:
        ok = test["fn"]()
        if ok:
            print("  PASS")
            passed += 1
            results.append((test["name"], "PASS", ""))
        else:
            print("  FAIL (returned False)")
            failed += 1
            results.append((test["name"], "FAIL", "function returned False"))
    except Exception as exc:
        err = str(exc).encode('ascii', errors='replace').decode('ascii')
        print(f"  ERROR: {err}")
        failed += 1
        results.append((test["name"], "ERROR", err))
    print()

print(sep)
print(f"  Results: {passed} passed, {failed} failed  (out of {len(TESTS)})")
print(sep)

if failed == 0:
    print("  [ALL PASS] All emails sent successfully!")
    print(f"  Check inbox: {RECIPIENT}")
else:
    print("  [PARTIAL]  Some emails failed. Details:")
    for name, status, msg in results:
        if status != "PASS":
            print(f"    - {name}: {status}" + (f" -> {msg}" if msg else ""))

print()
