"""
email_utils.py - Infinity Coders Unified Email System
======================================================
Version 2.0 - Professional HTML Templates + Error-Free Windows Support
Loads config from .env automatically.

All 7 email types:
  1. Email Verification
  2. Welcome (after verification)
  3. Admin Notification (new signup)
  4. Enquiry Confirmation (student)
  5. Demo Scheduled
  6. Demo Rescheduled / Updated
  7. Demo Cancelled
"""

import smtplib, ssl, os, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
except Exception:
    pass

# ── Config ─────────────────────────────────────────────────────────────────────
EMAIL_SENDER   = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL', 'admin@infinitycoders.com')
APP_URL        = os.environ.get('APP_URL', 'http://localhost:5000')
INSTITUTE_NAME = os.environ.get('INSTITUTE_NAME', 'Infinity Coders')
SMTP_HOST      = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT      = int(os.environ.get('SMTP_PORT', 465))

# ── Safe print helper (Windows cp1252 safe) ───────────────────────────────────
def _safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode('ascii'))


# ── Brand Design Tokens ────────────────────────────────────────────────────────
PRIMARY    = '#7C3AED'
PRIMARY_DK = '#6D28D9'
PRIMARY_LT = '#A78BFA'
SUCCESS    = '#10B981'
SUCCESS_LT = '#34D399'
WARNING    = '#F59E0B'
WARNING_LT = '#FCD34D'
DANGER     = '#EF4444'
DANGER_LT  = '#F87171'
INFO       = '#3B82F6'

BG_OUTER   = '#0a0a18'
BG_CARD    = '#12122a'
BG_INNER   = '#1a1a35'
BORDER     = 'rgba(124,58,237,0.20)'
TEXT_HEAD  = '#FFFFFF'
TEXT_BODY  = '#CBD5E1'
TEXT_MUTED = '#64748B'
TEXT_SUB   = '#94A3B8'


# ══════════════════════════════════════════════════════════════════════════════
#  BASE HTML TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
def _base_html(title: str, body_inner: str,
               accent: str = None, accent_lt: str = None) -> str:
    acc     = accent    or PRIMARY
    acc_lt  = accent_lt or PRIMARY_LT
    year    = 2026

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{title} | {INSTITUTE_NAME}</title>
</head>
<body style="margin:0;padding:0;background:{BG_OUTER};-webkit-font-smoothing:antialiased;">

<!-- Outer wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:{BG_OUTER};padding:32px 16px;">
  <tr>
    <td align="center">

      <!-- Email card -->
      <table width="600" cellpadding="0" cellspacing="0" border="0"
             style="max-width:600px;width:100%;background:{BG_CARD};
                    border-radius:20px;overflow:hidden;
                    border:1px solid {BORDER};
                    box-shadow:0 32px 64px rgba(0,0,0,0.6);">

        <!-- ── HEADER BANNER ── -->
        <tr>
          <td style="background:linear-gradient(135deg,{acc} 0%,{acc_lt} 100%);
                     padding:32px 40px;text-align:center;">
            <!-- Logo mark -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td align="center" style="padding-bottom:12px;">
                  <div style="display:inline-block;width:52px;height:52px;
                              background:rgba(255,255,255,0.15);border-radius:14px;
                              text-align:center;line-height:52px;
                              font-size:26px;font-weight:900;color:#fff;
                              letter-spacing:-1px;">
                    &#8734;
                  </div>
                </td>
              </tr>
              <tr>
                <td align="center">
                  <div style="color:#fff;font-size:20px;font-weight:800;
                              font-family:'Segoe UI',Arial,sans-serif;
                              letter-spacing:0.3px;">
                    {INSTITUTE_NAME}
                  </div>
                  <div style="color:rgba(255,255,255,0.7);font-size:12px;
                              font-family:'Segoe UI',Arial,sans-serif;
                              margin-top:4px;letter-spacing:0.5px;">
                    Smart Enquiry &amp; Demo Scheduling Portal
                  </div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ── BODY ── -->
        <tr>
          <td style="padding:36px 40px;font-family:'Segoe UI',Arial,sans-serif;
                     color:{TEXT_BODY};">
            {body_inner}
          </td>
        </tr>

        <!-- ── FOOTER ── -->
        <tr>
          <td style="background:{BG_INNER};padding:22px 40px;
                     border-top:1px solid {BORDER};text-align:center;">
            <p style="margin:0 0 6px;font-size:12px;color:{TEXT_MUTED};
                      font-family:'Segoe UI',Arial,sans-serif;">
              This is an automated message from
              <strong style="color:{TEXT_SUB};">{INSTITUTE_NAME}</strong>.
              Please do not reply directly to this email.
            </p>
            <p style="margin:0;font-size:12px;font-family:'Segoe UI',Arial,sans-serif;">
              <a href="{APP_URL}" style="color:{acc_lt};text-decoration:none;">
                Visit Portal
              </a>
              &nbsp;&nbsp;&#8226;&nbsp;&nbsp;
              <a href="mailto:{EMAIL_SENDER}"
                 style="color:{acc_lt};text-decoration:none;">
                Contact Support
              </a>
            </p>
            <p style="margin:8px 0 0;font-size:11px;color:{TEXT_MUTED};
                      font-family:'Segoe UI',Arial,sans-serif;">
              &copy; {year} {INSTITUTE_NAME}. All rights reserved.
            </p>
          </td>
        </tr>

      </table>
      <!-- /Email card -->

    </td>
  </tr>
</table>

</body>
</html>"""


# ── Reusable component: info row ───────────────────────────────────────────────
def _info_row(label: str, value: str, accent: str = None) -> str:
    a = accent or PRIMARY_LT
    return f"""
    <tr>
      <td style="padding:10px 16px 10px 0;color:{TEXT_MUTED};font-size:13px;
                 font-family:'Segoe UI',Arial,sans-serif;
                 border-bottom:1px solid rgba(255,255,255,0.04);
                 white-space:nowrap;width:38%;vertical-align:top;">
        {label}
      </td>
      <td style="padding:10px 0;color:{TEXT_HEAD};font-size:13px;font-weight:600;
                 font-family:'Segoe UI',Arial,sans-serif;
                 border-bottom:1px solid rgba(255,255,255,0.04);
                 vertical-align:top;">
        {value}
      </td>
    </tr>"""


# ── Reusable component: CTA button ────────────────────────────────────────────
def _cta_button(label: str, href: str,
                bg: str = None, bg_lt: str = None) -> str:
    b  = bg    or PRIMARY
    bl = bg_lt or PRIMARY_LT
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr>
        <td align="center" style="padding:8px 0 4px;">
          <a href="{href}"
             style="display:inline-block;padding:16px 48px;
                    background:linear-gradient(135deg,{b},{bl});
                    color:#ffffff;text-decoration:none;font-size:15px;
                    font-weight:700;border-radius:12px;
                    font-family:'Segoe UI',Arial,sans-serif;
                    letter-spacing:0.3px;
                    box-shadow:0 8px 24px rgba(124,58,237,0.35);">
            {label}
          </a>
        </td>
      </tr>
    </table>"""


# ── Reusable component: info card (grey box) ──────────────────────────────────
def _info_card(title: str, rows_html: str, accent: str = None) -> str:
    a = accent or PRIMARY
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="background:{BG_INNER};border:1px solid rgba(255,255,255,0.07);
                  border-radius:14px;margin-bottom:24px;overflow:hidden;">
      <tr>
        <td style="padding:14px 20px 4px;border-bottom:1px solid rgba(255,255,255,0.05);">
          <span style="font-size:11px;color:{TEXT_MUTED};font-weight:700;
                       text-transform:uppercase;letter-spacing:1.2px;
                       font-family:'Segoe UI',Arial,sans-serif;">
            {title}
          </span>
        </td>
      </tr>
      <tr>
        <td style="padding:4px 20px 10px;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            {rows_html}
          </table>
        </td>
      </tr>
    </table>"""


# ── Reusable component: notice / tip box ─────────────────────────────────────
def _notice_box(html: str, color: str = None, bg_alpha: str = '0.07') -> str:
    c = color or WARNING
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td style="background:rgba(0,0,0,{bg_alpha});
                   border-left:3px solid {c};border-radius:0 10px 10px 0;
                   padding:14px 18px;">
          <span style="font-size:13px;color:{TEXT_BODY};line-height:1.6;
                       font-family:'Segoe UI',Arial,sans-serif;">
            {html}
          </span>
        </td>
      </tr>
    </table>"""


# ── Reusable component: status badge ─────────────────────────────────────────
def _badge(text: str, color: str, bg_alpha: str = '0.12') -> str:
    return (
        f'<span style="display:inline-block;background:rgba(0,0,0,{bg_alpha});'
        f'border:1px solid {color};color:{color};'
        f'font-size:11px;font-weight:700;padding:3px 12px;'
        f'border-radius:99px;letter-spacing:0.5px;">'
        f'{text}</span>'
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CORE SEND FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def send_email(to: str, subject: str, html_body: str) -> bool:
    """Send branded HTML email via SMTP SSL. Returns True on success."""

    if not to or '@' not in to:
        _safe_print(f"[EMAIL] Skipped: invalid recipient '{to}'")
        return False

    if not EMAIL_SENDER or not EMAIL_PASSWORD or 'yourapppassword' in EMAIL_PASSWORD:
        _safe_print(
            f"[EMAIL] WARNING: Email not configured. "
            f"Set EMAIL_SENDER & EMAIL_PASSWORD in .env"
        )
        _safe_print(f"[EMAIL] Would send to: {to}  |  Subject: {subject}")
        return False

    try:
        msg = MIMEMultipart('alternative')
        # Always encode subject as UTF-8 to support non-ASCII chars safely
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From']    = f'{INSTITUTE_NAME} <{EMAIL_SENDER}>'
        msg['To']      = to
        msg['X-Mailer'] = f'{INSTITUTE_NAME} Portal Mailer v2.0'
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to, msg.as_bytes())

        _safe_print(f"[EMAIL] OK  -> '{subject}'  => {to}")
        return True

    except smtplib.SMTPAuthenticationError:
        _safe_print(
            "[EMAIL] AUTH ERROR: Wrong email/password. "
            "Check .env -> EMAIL_SENDER & EMAIL_PASSWORD"
        )
        return False
    except smtplib.SMTPRecipientsRefused as e:
        _safe_print(f"[EMAIL] RECIPIENT ERROR: {e}")
        return False
    except smtplib.SMTPException as e:
        _safe_print(f"[EMAIL] SMTP ERROR: {e}")
        return False
    except Exception as e:
        _safe_print(f"[EMAIL] ERROR sending to {to}: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  1. EMAIL VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════
def send_verification_email(user_name: str, user_email: str,
                             token: str) -> bool:
    verify_url = f"{APP_URL}/api/auth/verify-email/{token}"

    body = f"""
    <!-- Hero -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:28px;">
      <tr>
        <td align="center" style="padding-bottom:16px;">
          <div style="width:72px;height:72px;border-radius:50%;
                      background:rgba(124,58,237,0.12);
                      border:2px solid {PRIMARY};
                      text-align:center;line-height:70px;font-size:32px;">
            &#9993;
          </div>
        </td>
      </tr>
      <tr>
        <td align="center">
          <h1 style="margin:0 0 8px;color:{TEXT_HEAD};font-size:24px;
                     font-weight:800;font-family:'Segoe UI',Arial,sans-serif;">
            Verify Your Email
          </h1>
          <p style="margin:0;color:{TEXT_SUB};font-size:15px;
                    font-family:'Segoe UI',Arial,sans-serif;line-height:1.5;">
            Hello, <strong style="color:{TEXT_HEAD};">{user_name}</strong>!
            You are one step away from activating your account.
          </p>
        </td>
      </tr>
    </table>

    <!-- CTA -->
    {_cta_button('Verify My Email Address', verify_url)}

    <!-- Security notice -->
    {_notice_box(
        f'<strong style="color:{TEXT_HEAD};">Security notice:</strong> '
        f'This verification link is valid for <strong style="color:{TEXT_HEAD};">24 hours</strong>. '
        f'If you did not create an account with {INSTITUTE_NAME}, '
        f'you can safely ignore this email.',
        WARNING
    )}

    <!-- Fallback link -->
    <p style="margin:0;font-size:12px;color:{TEXT_MUTED};text-align:center;
              font-family:'Segoe UI',Arial,sans-serif;line-height:1.7;">
      Button not working? Copy and paste this link into your browser:<br>
      <a href="{verify_url}"
         style="color:{PRIMARY_LT};word-break:break-all;">{verify_url}</a>
    </p>
    """

    return send_email(
        to=user_email,
        subject=f"Verify your email - {INSTITUTE_NAME}",
        html_body=_base_html("Verify Email", body)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  2. WELCOME EMAIL (after verification)
# ══════════════════════════════════════════════════════════════════════════════
def send_welcome_email(user_name: str, user_email: str) -> bool:
    features = [
        ('&#128203;', 'Manage Enquiries',
         'Organise and track all student enquiries in one place.'),
        ('&#128197;', 'Schedule Demos',
         'Book, update, or cancel demo sessions with a few clicks.'),
        ('&#128202;', 'Analytics Dashboard',
         'Monitor performance metrics and counselor activity.'),
        ('&#128276;', 'Smart Notifications',
         'Auto-email students on every status change.'),
    ]

    feature_rows = ''
    for icon, title, desc in features:
        feature_rows += f"""
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="width:44px;vertical-align:top;">
                  <div style="width:36px;height:36px;border-radius:10px;
                              background:rgba(124,58,237,0.12);
                              text-align:center;line-height:36px;font-size:18px;">
                    {icon}
                  </div>
                </td>
                <td style="vertical-align:top;padding-left:4px;">
                  <div style="color:{TEXT_HEAD};font-size:13px;font-weight:700;
                               font-family:'Segoe UI',Arial,sans-serif;
                               margin-bottom:2px;">{title}</div>
                  <div style="color:{TEXT_MUTED};font-size:12px;
                               font-family:'Segoe UI',Arial,sans-serif;">{desc}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    body = f"""
    <!-- Hero -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td align="center" style="padding-bottom:14px;">
          <div style="width:72px;height:72px;border-radius:50%;
                      background:rgba(16,185,129,0.12);
                      border:2px solid {SUCCESS};
                      text-align:center;line-height:70px;font-size:32px;">
            &#127881;
          </div>
        </td>
      </tr>
      <tr>
        <td align="center">
          <h1 style="margin:0 0 8px;color:{TEXT_HEAD};font-size:24px;
                     font-weight:800;font-family:'Segoe UI',Arial,sans-serif;">
            Welcome aboard, {user_name}!
          </h1>
          <p style="margin:0;color:{TEXT_SUB};font-size:14px;
                    font-family:'Segoe UI',Arial,sans-serif;line-height:1.5;">
            Your email is verified and your account is now
            <strong style="color:{SUCCESS};">fully active</strong>.
            Here is what you can do with {INSTITUTE_NAME}:
          </p>
        </td>
      </tr>
    </table>

    <!-- Features card -->
    {_info_card('What You Can Do', feature_rows, SUCCESS)}

    <!-- CTA -->
    {_cta_button('Go to My Dashboard', f'{APP_URL}/login.html', SUCCESS, SUCCESS_LT)}

    <p style="margin:20px 0 0;font-size:12px;color:{TEXT_MUTED};text-align:center;
              font-family:'Segoe UI',Arial,sans-serif;">
      Need help getting started? Reply to this email or visit our portal.
    </p>
    """

    return send_email(
        to=user_email,
        subject=f"Welcome to {INSTITUTE_NAME} - Your Account is Active!",
        html_body=_base_html("Welcome!", body, SUCCESS, SUCCESS_LT)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  3. ADMIN NOTIFICATION (new signup)
# ══════════════════════════════════════════════════════════════════════════════
def send_admin_notification(user_name: str, user_email: str,
                             user_phone: str = '') -> bool:
    from datetime import datetime
    now = datetime.now().strftime('%d %b %Y at %I:%M %p')

    rows = (
        _info_row('Full Name',   user_name) +
        _info_row('Email',
                  f'<a href="mailto:{user_email}" '
                  f'style="color:{PRIMARY_LT};text-decoration:none;">'
                  f'{user_email}</a>') +
        _info_row('Phone',       user_phone if user_phone else '&#8212;') +
        _info_row('Registered',  now) +
        _info_row('Status',      _badge('Pending Verification', WARNING))
    )

    body = f"""
    <!-- Alert banner -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td style="background:rgba(124,58,237,0.10);
                   border:1px solid rgba(124,58,237,0.25);
                   border-radius:14px;padding:18px 22px;">
          <p style="margin:0 0 4px;font-size:11px;color:{TEXT_MUTED};
                    font-weight:700;text-transform:uppercase;letter-spacing:1.2px;
                    font-family:'Segoe UI',Arial,sans-serif;">
            New Counselor Signup Alert
          </p>
          <p style="margin:0;font-size:22px;font-weight:800;color:{TEXT_HEAD};
                    font-family:'Segoe UI',Arial,sans-serif;">
            {user_name}
          </p>
          <p style="margin:6px 0 0;font-size:13px;color:{TEXT_SUB};
                    font-family:'Segoe UI',Arial,sans-serif;">
            Awaiting email verification to activate account.
          </p>
        </td>
      </tr>
    </table>

    <!-- Details card -->
    {_info_card('Counselor Details', rows)}

    <!-- Notice -->
    {_notice_box(
        f'<strong style="color:{TEXT_HEAD};">Auto-activation:</strong> '
        f'The account will activate automatically once the counselor '
        f'verifies their email address. No action required from your side.',
        INFO
    )}

    <!-- CTA -->
    {_cta_button('Open Admin Panel', f'{APP_URL}/admin/index.html')}
    """

    return send_email(
        to=ADMIN_EMAIL,
        subject=f"[{INSTITUTE_NAME}] New Counselor Signup - {user_name}",
        html_body=_base_html("New Signup Alert", body)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  4. ENQUIRY CONFIRMATION (student)
# ══════════════════════════════════════════════════════════════════════════════
def send_enquiry_confirmation(student_name: str, student_email: str,
                               stream: str, counselor_name: str = '',
                               followup_date: str = '') -> bool:
    if not student_email:
        return False

    rows = _info_row('Student Name', student_name)
    rows += _info_row('Course Interest', stream)
    if counselor_name:
        rows += _info_row('Assigned Counselor', counselor_name)
    if followup_date:
        rows += _info_row('Follow-up Date', followup_date)

    next_steps = [
        'Our counselor will contact you on your registered number shortly.',
        'You may receive a demo session invitation via email.',
        'Keep an eye on your inbox for updates from us.',
    ]
    steps_html = ''.join(
        f'<tr><td style="padding:6px 0;color:{TEXT_BODY};font-size:13px;'
        f'font-family:\'Segoe UI\',Arial,sans-serif;">'
        f'<span style="color:{SUCCESS};margin-right:8px;">&#10003;</span>{s}'
        f'</td></tr>'
        for s in next_steps
    )

    body = f"""
    <!-- Hero -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td align="center" style="padding-bottom:14px;">
          <div style="width:72px;height:72px;border-radius:50%;
                      background:rgba(16,185,129,0.12);
                      border:2px solid {SUCCESS};
                      text-align:center;line-height:70px;font-size:32px;">
            &#10003;
          </div>
        </td>
      </tr>
      <tr>
        <td align="center">
          <h1 style="margin:0 0 8px;color:{TEXT_HEAD};font-size:24px;
                     font-weight:800;font-family:'Segoe UI',Arial,sans-serif;">
            Enquiry Received!
          </h1>
          <p style="margin:0;color:{TEXT_SUB};font-size:14px;
                    font-family:'Segoe UI',Arial,sans-serif;line-height:1.5;">
            Thank you, <strong style="color:{TEXT_HEAD};">{student_name}</strong>.
            We have successfully received your enquiry and will be in touch soon.
          </p>
        </td>
      </tr>
    </table>

    <!-- Enquiry details -->
    {_info_card('Enquiry Details', rows, SUCCESS)}

    <!-- Next steps -->
    {_info_card('What Happens Next', steps_html, SUCCESS)}

    <p style="margin:0;font-size:13px;color:{TEXT_MUTED};text-align:center;
              font-family:'Segoe UI',Arial,sans-serif;">
      Questions? Call us or reply to this email.<br>
      <strong style="color:{TEXT_SUB};">{INSTITUTE_NAME} Team</strong>
    </p>
    """

    return send_email(
        to=student_email,
        subject=f"[{INSTITUTE_NAME}] Enquiry Received - {stream}",
        html_body=_base_html("Enquiry Confirmed", body, SUCCESS, SUCCESS_LT)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  5. DEMO SCHEDULED
# ══════════════════════════════════════════════════════════════════════════════
def send_demo_scheduled(student_name: str, student_email: str,
                         stream: str, demo_date: str, demo_time: str,
                         counselor_name: str, mode: str,
                         location: str = '') -> bool:
    if not student_email:
        return False

    rows = (
        _info_row('Student',      student_name) +
        _info_row('Course',       stream) +
        _info_row('Date',         demo_date) +
        _info_row('Time',         demo_time) +
        _info_row('Mode',         mode)
    )
    if location:
        rows += _info_row(
            'Location / Link',
            f'<a href="{location}" style="color:{PRIMARY_LT};">{location}</a>'
        )
    rows += _info_row('Counselor', counselor_name)

    body = f"""
    <!-- Hero -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td align="center" style="padding-bottom:14px;">
          <div style="width:72px;height:72px;border-radius:50%;
                      background:rgba(124,58,237,0.12);
                      border:2px solid {PRIMARY};
                      text-align:center;line-height:70px;font-size:32px;">
            &#128197;
          </div>
        </td>
      </tr>
      <tr>
        <td align="center">
          <h1 style="margin:0 0 8px;color:{TEXT_HEAD};font-size:24px;
                     font-weight:800;font-family:'Segoe UI',Arial,sans-serif;">
            Demo Session Confirmed!
          </h1>
          <p style="margin:0;color:{TEXT_SUB};font-size:14px;
                    font-family:'Segoe UI',Arial,sans-serif;line-height:1.5;">
            Great news, <strong style="color:{TEXT_HEAD};">{student_name}</strong>!
            Your demo session has been scheduled. See the details below.
          </p>
        </td>
      </tr>
    </table>

    <!-- Session details card -->
    {_info_card('Session Details', rows)}

    <!-- Reminder -->
    {_notice_box(
        f'<strong style="color:{TEXT_HEAD};">Reminder:</strong> '
        f'Please be available at least 5 minutes before your session. '
        f'If you need to reschedule, contact us at least 2 hours in advance.',
        WARNING
    )}

    <p style="margin:0 0 4px;font-size:13px;color:{TEXT_MUTED};text-align:center;
              font-family:'Segoe UI',Arial,sans-serif;">
      We look forward to seeing you at the session!
    </p>
    <p style="margin:0;font-size:13px;color:{TEXT_SUB};text-align:center;
              font-weight:700;font-family:'Segoe UI',Arial,sans-serif;">
      {INSTITUTE_NAME} Team
    </p>
    """

    return send_email(
        to=student_email,
        subject=f"[{INSTITUTE_NAME}] Demo Scheduled - {demo_date} at {demo_time}",
        html_body=_base_html("Demo Confirmed", body)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  6. DEMO RESCHEDULED / UPDATED
# ══════════════════════════════════════════════════════════════════════════════
def send_demo_updated(student_name: str, student_email: str,
                       stream: str, demo_date: str, demo_time: str,
                       counselor_name: str, mode: str,
                       location: str = '') -> bool:
    if not student_email:
        return False

    rows = (
        _info_row('Student',      student_name) +
        _info_row('Course',       stream) +
        _info_row('New Date',     demo_date) +
        _info_row('New Time',     demo_time) +
        _info_row('Mode',         mode)
    )
    if location:
        rows += _info_row(
            'Location / Link',
            f'<a href="{location}" style="color:{WARNING_LT};">{location}</a>'
        )
    rows += _info_row('Counselor', counselor_name)

    body = f"""
    <!-- Hero -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td align="center" style="padding-bottom:14px;">
          <div style="width:72px;height:72px;border-radius:50%;
                      background:rgba(245,158,11,0.12);
                      border:2px solid {WARNING};
                      text-align:center;line-height:70px;font-size:32px;">
            &#128260;
          </div>
        </td>
      </tr>
      <tr>
        <td align="center">
          <h1 style="margin:0 0 8px;color:{TEXT_HEAD};font-size:24px;
                     font-weight:800;font-family:'Segoe UI',Arial,sans-serif;">
            Demo Session Rescheduled
          </h1>
          <p style="margin:0;color:{TEXT_SUB};font-size:14px;
                    font-family:'Segoe UI',Arial,sans-serif;line-height:1.5;">
            Hi <strong style="color:{TEXT_HEAD};">{student_name}</strong>,
            your demo session has been updated.
            Please take note of the new date and time below.
          </p>
        </td>
      </tr>
    </table>

    <!-- Updated session details -->
    {_info_card('Updated Session Details', rows, WARNING)}

    <!-- Apology notice -->
    {_notice_box(
        f'We sincerely apologize for any inconvenience caused by this change. '
        f'If the new time does not work for you, please contact us and we will '
        f'find a better slot.',
        WARNING
    )}

    <p style="margin:0 0 4px;font-size:13px;color:{TEXT_MUTED};text-align:center;
              font-family:'Segoe UI',Arial,sans-serif;">
      Apologies for the inconvenience. See you at the new time!
    </p>
    <p style="margin:0;font-size:13px;color:{TEXT_SUB};text-align:center;
              font-weight:700;font-family:'Segoe UI',Arial,sans-serif;">
      {INSTITUTE_NAME} Team
    </p>
    """

    return send_email(
        to=student_email,
        subject=f"[{INSTITUTE_NAME}] Demo Rescheduled - {demo_date} at {demo_time}",
        html_body=_base_html("Demo Rescheduled", body, WARNING, WARNING_LT)
    )


# ══════════════════════════════════════════════════════════════════════════════
#  7. DEMO CANCELLED
# ══════════════════════════════════════════════════════════════════════════════
def send_demo_cancelled(student_name: str, student_email: str,
                         stream: str, demo_date: str,
                         demo_time: str) -> bool:
    if not student_email:
        return False

    rows = (
        _info_row('Student',          student_name) +
        _info_row('Course',           stream) +
        _info_row('Cancelled Date',   demo_date) +
        _info_row('Cancelled Time',   demo_time) +
        _info_row('Status',           _badge('CANCELLED', DANGER))
    )

    body = f"""
    <!-- Hero -->
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-bottom:24px;">
      <tr>
        <td align="center" style="padding-bottom:14px;">
          <div style="width:72px;height:72px;border-radius:50%;
                      background:rgba(239,68,68,0.12);
                      border:2px solid {DANGER};
                      text-align:center;line-height:70px;font-size:32px;">
            &#10060;
          </div>
        </td>
      </tr>
      <tr>
        <td align="center">
          <h1 style="margin:0 0 8px;color:{TEXT_HEAD};font-size:24px;
                     font-weight:800;font-family:'Segoe UI',Arial,sans-serif;">
            Demo Session Cancelled
          </h1>
          <p style="margin:0;color:{TEXT_SUB};font-size:14px;
                    font-family:'Segoe UI',Arial,sans-serif;line-height:1.5;">
            Hi <strong style="color:{TEXT_HEAD};">{student_name}</strong>,
            unfortunately your upcoming demo session has been cancelled.
          </p>
        </td>
      </tr>
    </table>

    <!-- Cancelled session details -->
    {_info_card('Cancelled Session Details', rows, DANGER)}

    <!-- Reschedule offer -->
    {_notice_box(
        f'<strong style="color:{TEXT_HEAD};">We will reach out to you.</strong> '
        f'Our team will contact you at the earliest opportunity to reschedule '
        f'at a time that works best for you. We apologize for the inconvenience.',
        INFO
    )}

    <p style="margin:0 0 4px;font-size:13px;color:{TEXT_MUTED};text-align:center;
              font-family:'Segoe UI',Arial,sans-serif;">
      We are sorry for the disruption — your time is valuable to us.
    </p>
    <p style="margin:0;font-size:13px;color:{TEXT_SUB};text-align:center;
              font-weight:700;font-family:'Segoe UI',Arial,sans-serif;">
      {INSTITUTE_NAME} Team
    </p>
    """

    return send_email(
        to=student_email,
        subject=f"[{INSTITUTE_NAME}] Demo Session Cancelled",
        html_body=_base_html("Demo Cancelled", body, DANGER, DANGER_LT)
    )
