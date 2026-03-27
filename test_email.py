"""
test_email.py – Quick email system test for Infinity Coders
Sends a branded test email to verify SMTP is working correctly.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from email_utils import (
    send_email, _base_html,
    C_PRIMARY, C_LIGHT, C_MUTED, C_TEXT, C_SUCCESS,
    INSTITUTE_NAME, APP_URL,
    EMAIL_SENDER, EMAIL_PASSWORD
)

TEST_RECIPIENT = "shlksuthar@gmail.com"

print("=" * 55)
print("  Infinity Coders – Email System Test")
print("=" * 55)
print(f"  Sender  : {EMAIL_SENDER}")
print(f"  Password: {'*' * len(EMAIL_PASSWORD) if EMAIL_PASSWORD else '(not set)'}")
print(f"  Sending to: {TEST_RECIPIENT}")
print("=" * 55)

body = f"""
  <div style="text-align:center;margin-bottom:24px;">
    <div style="width:64px;height:64px;border-radius:50%;
                background:rgba(108,43,217,0.12);border:2px solid {C_PRIMARY};
                display:inline-flex;align-items:center;justify-content:center;
                font-size:28px;margin-bottom:12px;">&#128200;</div>
    <h2 style="color:#fff;font-size:22px;font-weight:800;margin:0 0 6px;">
      Email Test Successful!
    </h2>
    <p style="color:{C_MUTED};font-size:14px;margin:0;">
      This is a <strong style="color:#fff;">test email</strong> from the Infinity Coders portal.<br>
      If you are reading this, the email system is working correctly!
    </p>
  </div>

  <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
              border-radius:12px;padding:18px 22px;margin-bottom:24px;">
    <div style="font-size:11px;color:{C_MUTED};font-weight:700;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">
      System Status
    </div>
    <p style="margin:0;font-size:14px;color:{C_TEXT};line-height:2;">
      &#10003; &nbsp;<strong>SMTP Connection:</strong> OK (smtp.gmail.com:465)<br>
      &#10003; &nbsp;<strong>Authentication:</strong> OK<br>
      &#10003; &nbsp;<strong>HTML Email Rendering:</strong> OK<br>
      &#10003; &nbsp;<strong>Branded Template:</strong> OK
    </p>
  </div>

  <p style="font-size:13px;color:{C_MUTED};text-align:center;margin:0;">
    Sent from <strong style="color:{C_TEXT};">{INSTITUTE_NAME}</strong> portal<br>
    <a href="{APP_URL}" style="color:{C_LIGHT};">{APP_URL}</a>
  </p>
"""

result = send_email(
    to=TEST_RECIPIENT,
    subject=f"[{INSTITUTE_NAME}] Test Email - System Check",
    html_body=_base_html("Test Email", body, C_SUCCESS)
)

print()
if result:
    print(f"  [OK]   SUCCESS - Test email delivered to {TEST_RECIPIENT}")
else:
    print(f"  [ERR]  FAILED  - Check .env credentials and try again.")
print()
