import os
import json
import calendar
import smtplib
import secrets
import hashlib
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, redirect, url_for, session, render_template, request, abort, make_response
from authlib.integrations.flask_client import OAuth

# --- START: REMOVE AZURE SSO & TWILIO AUTOMATICALLY ---
import sys
import os

# Remove Azure environment variables if they exist
for k in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "OIDC_DISCOVERY_URL"):
    if k in os.environ:
        os.environ.pop(k, None)

# Remove Twilio environment variables if they exist
for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"):
    if k in os.environ:
        os.environ.pop(k, None)

# Dummy Client class so any remaining Twilio references don't crash
class DummyClient:
    def __init__(self, *args, **kwargs): pass
    def messages(self): return self
    def create(self, *args, **kwargs): pass

# Override Twilio Client if it exists anywhere
try:
    from twilio.rest import Client
    Client = DummyClient
except ImportError:
    pass

# Dummy OAuth class so Azure OAuth references don't crash
# Dummy OAuth class so Azure OAuth references don't crash
class DummyOAuthClient:
    def register(self, *args, **kwargs): return None

class DummyOAuth:
    def __init__(self, app=None):
        # mimic the real constructor
        self.app = app
    def register(self, *args, **kwargs):
        return DummyOAuthClient()

try:
    from authlib.integrations.flask_client import OAuth
except ImportError:
    OAuth = DummyOAuth

print("Azure SSO and Twilio disabled at runtime.", file=sys.stderr)
# --- END: REMOVE AZURE SSO & TWILIO ---

# --- Flask setup ---
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret")

# --- Optional Azure AD SSO ---
oauth = OAuth(app)
if os.environ.get("AZURE_CLIENT_ID") and os.environ.get("AZURE_CLIENT_SECRET") and os.environ.get("AZURE_TENANT_ID"):
    azure = oauth.register(
        name='azure',
        client_id=os.environ.get("AZURE_CLIENT_ID"),
        client_secret=os.environ.get("AZURE_CLIENT_SECRET"),
        server_metadata_url=f'https://login.microsoftonline.com/{os.environ.get("AZURE_TENANT_ID")}/v2.0/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
else:
    print("Azure SSO disabled (missing config)")

# --- Data and configuration (Python-side) ---
# Departments, processes, employees, and shift definitions are now defined fully in Python.
DEPARTMENTS: Dict[str, Dict] = {
    "Service Desk": {
        "processes": {
            "INDIA AND APAC": [
                "Adithya K G","Bandhavi V","Chandru Rajendran","Chandraprakash","Dakshinamoorthy Selvaraj",
                "Harish Kuruba","J Mohan Kumar","Navaneetha Krishnan","Rakesh M","Sandeep Kumar",
                "Sathish Chandran","Sheetham Sahoo","Shilpa C","Shripad L","Sree Hari N","Subhash K"
            ],
            "EMEA AND AMEC": [
                "Arpitha K B","Ashoka K","Jebosh Raju","Kanagavalli Dhamodharan","Kotlapalli Nikhitha",
                "Manohar Kirshna","Ramya J","Sayed Abbas","Shaktivel K","Vaishali Sahu",
                "Venkata Sai Nagendra Batchu"
            ]
        },
        "shifts": {
            "APAC": "5AM to 2PM",
            "Morning": "7AM to 4PM",
            "General": "11AM to 8PM",
            "Afternoon": "3PM to 12AM",
            "Evening": "6PM to 3AM",
            "Night": "8PM to 5AM",
            "Weekend": "7AM to 4PM",
            "PL": "Planned Leave",
            "AL": "Adhoc Leave",
            "Early": "1PM to 10PM",
            "WO": "Weekly Off",
            "Holiday": "Holiday",
            "LWD": "Last Working Day"
        },
        "show_filters": True,
        "password": "service123"
    },
    # Other departments with their specific passwords
    "App Tools": {"processes": {}, "shifts": {}, "show_filters": False, "password": "apptools123"},
    "App Development": {"processes": {}, "shifts": {}, "show_filters": False, "password": "appdev123"},
    "Cloud Ops": {"processes": {}, "shifts": {}, "show_filters": False, "password": "cloudops123"},
    "End User Ops": {"processes": {}, "shifts": {}, "show_filters": False, "password": "enduser123"},
    "Messaging": {"processes": {}, "shifts": {}, "show_filters": False, "password": "messaging123"},
    "Network Team": {"processes": {}, "shifts": {}, "show_filters": False, "password": "network123"},
    "Technology Operation Centre (TOC)": {"processes": {}, "shifts": {}, "show_filters": False, "password": "toc123"},
    "Threat Response Team": {"processes": {}, "shifts": {}, "show_filters": False, "password": "threat123"}
}

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'rota_data.json')
DEPT_CONFIG_FILE = os.path.join(DATA_DIR, 'department_config.json')
PASSWORD_RESET_FILE = os.path.join(DATA_DIR, 'password_reset_tokens.json')
EDITOR_PASSWORD = os.environ.get('EDITOR_PASSWORD', 'editor123')

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.environ.get('SMTP_PORT', '587')),
    'sender_email': os.environ.get('SENDER_EMAIL', 'admin@yourcompany.com'),
    'sender_password': os.environ.get('SENDER_PASSWORD', ''),  # App password for Gmail
    'use_tls': True
}

# SMS Configuration for OTP
SMS_CONFIG = {
    # Multiple SMS provider options - choose one
    'provider': os.environ.get('SMS_PROVIDER', 'twilio'),  # twilio, aws_sns, textlocal, mock
    
    # Twilio Configuration
    'twilio_account_sid': os.environ.get('TWILIO_ACCOUNT_SID', ''),
    'twilio_auth_token': os.environ.get('TWILIO_AUTH_TOKEN', ''),
    'twilio_phone_number': os.environ.get('TWILIO_PHONE_NUMBER', ''),  # Your Twilio phone number
    
    # AWS SNS Configuration (Alternative)
    'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID', ''),
    'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
    'aws_region': os.environ.get('AWS_REGION', 'us-east-1'),
    
    # TextLocal Configuration (Alternative)
    'textlocal_api_key': os.environ.get('TEXTLOCAL_API_KEY', ''),
    'textlocal_sender': os.environ.get('TEXTLOCAL_SENDER', 'TXTLCL'),
}

# Department Admin Email Mapping (Keep for backward compatibility)
DEPARTMENT_ADMIN_EMAILS = {
    'Service Desk': [
        'pruthvi.rajavarmaman@intertrustgroup.com', 
        'vinay.simhav@intertrustgroup.com', 
        'naveen.panchakshari@intertrustgroup.com',
        'tarun.kumar@intertrustgroup.com'
    ],
    'App Tools': ['apptools.admin@yourcompany.com'],
    'App Development': ['appdev.manager@yourcompany.com', 'dev.lead@yourcompany.com'],
    'Cloud Ops': ['cloudops.admin@yourcompany.com'],
    'End User Ops': ['enduser.admin@yourcompany.com'],
    'Messaging': ['messaging.admin@yourcompany.com'],
    'Network Team': ['network.admin@yourcompany.com'],
    'Technology Operation Centre (TOC)': ['toc.admin@yourcompany.com', 'toc.manager@yourcompany.com'],
    'Threat Response Team': ['security.admin@yourcompany.com']
}

# Department Admin Phone Numbers for SMS OTP
DEPARTMENT_ADMIN_PHONES = {
    'Service Desk': [
        '+919876543210',  # Pruthvi
        '+919876543211',  # Vinay  
        '+919876543212',  # Naveen
        '+919876543213',  # Tarun
        '+916360747770'   # Test user
    ],
    'App Tools': ['+919876543220'],
    'App Development': ['+919876543230', '+919876543231'],
    'Cloud Ops': ['+919876543240'],
    'End User Ops': ['+919876543250'],
    'Messaging': ['+919876543260'],
    'Network Team': ['+919876543270'],
    'Technology Operation Centre (TOC)': ['+919876543280', '+919876543281'],
    'Threat Response Team': ['+919876543290']
}

# --- Helpers ---
def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

def load_store() -> Dict[str, Dict[str, str]]:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_store(store: Dict[str, Dict[str, str]]) -> None:
    ensure_data_dir()
    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(store, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)

def load_department_config() -> Dict[str, Dict]:
    """Load department configuration from file, fallback to default if not exists"""
    if not os.path.exists(DEPT_CONFIG_FILE):
        return DEPARTMENTS.copy()
    try:
        with open(DEPT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEPARTMENTS.copy()

def save_department_config(config: Dict[str, Dict]) -> None:
    """Save department configuration to file with sorted employees"""
    # Sort all employee lists alphabetically before saving
    for dept_name, dept_data in config.items():
        if 'processes' in dept_data:
            for process_name, employees in dept_data['processes'].items():
                if isinstance(employees, list):
                    employees.sort()  # Sort alphabetically
    
    ensure_data_dir()
    tmp = DEPT_CONFIG_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DEPT_CONFIG_FILE)

def load_reset_tokens():
    """Load password reset tokens from file"""
    if os.path.exists(PASSWORD_RESET_FILE):
        with open(PASSWORD_RESET_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_reset_tokens(tokens):
    """Save password reset tokens to file"""
    ensure_data_dir()
    with open(PASSWORD_RESET_FILE, 'w') as file:
        json.dump(tokens, file, indent=2)

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

def create_reset_token(department, expiry_minutes=30):
    """Create a password reset token for a department"""
    token = generate_reset_token()
    expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
    
    tokens = load_reset_tokens()
    tokens[token] = {
        'department': department,
        'expiry': expiry_time.isoformat(),
        'created': datetime.now().isoformat()
    }
    save_reset_tokens(tokens)
    return token

def validate_reset_token(token):
    """Validate a password reset token"""
    tokens = load_reset_tokens()
    if token not in tokens:
        return None
    
    token_data = tokens[token]
    expiry_time = datetime.fromisoformat(token_data['expiry'])
    
    if datetime.now() > expiry_time:
        # Token expired, remove it
        del tokens[token]
        save_reset_tokens(tokens)
        return None
    
    return token_data['department']

def cleanup_expired_tokens():
    """Remove expired tokens from storage"""
    tokens = load_reset_tokens()
    current_time = datetime.now()
    
    expired_tokens = []
    for token, data in tokens.items():
        expiry_time = datetime.fromisoformat(data['expiry'])
        if current_time > expiry_time:
            expired_tokens.append(token)
    
    for token in expired_tokens:
        del tokens[token]
    
    if expired_tokens:
        save_reset_tokens(tokens)
    
    return len(expired_tokens)

def send_reset_email(department, token):
    """Send password reset email to department administrators"""
    if department not in DEPARTMENT_ADMIN_EMAILS:
        return False, f"No admin emails configured for {department}"
    
    admin_emails = DEPARTMENT_ADMIN_EMAILS[department]
    reset_url = url_for('reset_password', token=token, _external=True)
    
    subject = f"Password Reset Request - {department} Department"
    body = f"""
A password reset has been requested for the {department} department in the Shift Rota application.

Click the link below to reset the password:
{reset_url}

This link will expire in 30 minutes.

If you did not request this reset, please ignore this email.

Best regards,
Shift Rota System
"""
    
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = ', '.join(admin_emails)
        
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            if EMAIL_CONFIG['use_tls']:
                server.starttls()
            
            if EMAIL_CONFIG['sender_password']:
                server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            
            server.send_message(msg)
        
        return True, f"Reset email sent to {len(admin_emails)} administrator(s)"
    
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# ===== SMS OTP FUNCTIONS =====

def generate_otp():
    """Generate a 6-digit OTP"""
    return f"{secrets.randbelow(900000) + 100000:06d}"

def create_otp_token(department, expiry_minutes=10):
    """Create an OTP token for a department"""
    otp_code = generate_otp()
    expiry_time = datetime.now() + timedelta(minutes=expiry_minutes)
    
    tokens = load_reset_tokens()
    # Use OTP as key for easier lookup
    tokens[otp_code] = {
        'type': 'otp',
        'department': department,
        'expiry': expiry_time.isoformat(),
        'created': datetime.now().isoformat(),
        'attempts': 0  # Track failed attempts
    }
    save_reset_tokens(tokens)
    return otp_code

def validate_otp_token(otp_code):
    """Validate an OTP code"""
    tokens = load_reset_tokens()
    if otp_code not in tokens:
        return None, "Invalid OTP code"
    
    token_data = tokens[otp_code]
    
    # Check if it's an OTP token
    if token_data.get('type') != 'otp':
        return None, "Invalid token type"
    
    # Check expiry
    expiry_time = datetime.fromisoformat(token_data['expiry'])
    if datetime.now() > expiry_time:
        # Token expired, remove it
        del tokens[otp_code]
        save_reset_tokens(tokens)
        return None, "OTP code has expired"
    
    # Check attempts (max 3 attempts)
    if token_data.get('attempts', 0) >= 3:
        del tokens[otp_code]
        save_reset_tokens(tokens)
        return None, "Too many failed attempts"
    
    return token_data['department'], "Valid"

def increment_otp_attempts(otp_code):
    """Increment failed attempts for an OTP"""
    tokens = load_reset_tokens()
    if otp_code in tokens:
        tokens[otp_code]['attempts'] = tokens[otp_code].get('attempts', 0) + 1
        save_reset_tokens(tokens)

def consume_otp_token(otp_code):
    """Remove OTP token after successful use"""
    tokens = load_reset_tokens()
    if otp_code in tokens:
        del tokens[otp_code]
        save_reset_tokens(tokens)

def send_otp_sms(department, otp_code):
    """Send OTP via SMS to department administrators"""
    if department not in DEPARTMENT_ADMIN_PHONES:
        return False, f"No admin phones configured for {department}"
    
    admin_phones = DEPARTMENT_ADMIN_PHONES[department]
    
    message = f"""Shift Rota Password Reset

Your OTP: {otp_code}

Department: {department}
Valid for 10 minutes

Do not share this code."""
    
    provider = SMS_CONFIG.get('provider', 'twilio')
    
    try:
        if provider == 'twilio':
            return send_twilio_sms(admin_phones, message)
        elif provider == 'aws_sns':
            return send_aws_sns_sms(admin_phones, message)
        elif provider == 'textlocal':
            return send_textlocal_sms(admin_phones, message)
        else:
            return send_mock_sms(admin_phones, message, otp_code)
    
    except Exception as e:
        return False, f"SMS sending failed: {str(e)}"

def send_twilio_sms(phone_numbers, message):
    """Send SMS using Twilio"""
    try:
        from twilio.rest import Client
        
        client = Client(
            SMS_CONFIG['twilio_account_sid'], 
            SMS_CONFIG['twilio_auth_token']
        )
        
        sent_count = 0
        for phone in phone_numbers:
            client.messages.create(
                body=message,
                from_=SMS_CONFIG['twilio_phone_number'],
                to=phone
            )
            sent_count += 1
        
        return True, f"OTP sent to {sent_count} administrator(s)"
    
    except ImportError:
        return False, "Twilio library not installed. Run: pip install twilio"
    except Exception as e:
        return False, f"Twilio SMS failed: {str(e)}"

def send_aws_sns_sms(phone_numbers, message):
    """Send SMS using AWS SNS"""
    try:
        import boto3
        
        sns = boto3.client(
            'sns',
            aws_access_key_id=SMS_CONFIG['aws_access_key_id'],
            aws_secret_access_key=SMS_CONFIG['aws_secret_access_key'],
            region_name=SMS_CONFIG['aws_region']
        )
        
        sent_count = 0
        for phone in phone_numbers:
            sns.publish(
                PhoneNumber=phone,
                Message=message
            )
            sent_count += 1
        
        return True, f"OTP sent to {sent_count} administrator(s)"
    
    except ImportError:
        return False, "AWS boto3 library not installed. Run: pip install boto3"
    except Exception as e:
        return False, f"AWS SNS SMS failed: {str(e)}"

def send_textlocal_sms(phone_numbers, message):
    """Send SMS using TextLocal"""
    try:
        import urllib.parse
        import urllib.request
        
        api_key = SMS_CONFIG['textlocal_api_key']
        sender = SMS_CONFIG['textlocal_sender']
        
        numbers = ','.join(phone_numbers)
        
        data = urllib.parse.urlencode({
            'apikey': api_key,
            'numbers': numbers,
            'message': message,
            'sender': sender
        })
        
        request = urllib.request.Request('https://api.textlocal.in/send/')
        request.add_data(data.encode('utf-8'))
        
        response = urllib.request.urlopen(request)
        result = response.read().decode('utf-8')
        
        return True, f"OTP sent to {len(phone_numbers)} administrator(s)"
    
    except Exception as e:
        return False, f"TextLocal SMS failed: {str(e)}"

def send_mock_sms(phone_numbers, message, otp_code):
    """Mock SMS sending for development/testing"""
    import logging
    
    logging.info(f"MOCK SMS - Would send to {phone_numbers}")
    logging.info(f"Message: {message}")
    
    # In development, show the OTP in the response
    return True, f"SMS sent to {len(phone_numbers)} number(s). [DEV MODE - OTP: {otp_code}]"

def get_current_departments() -> Dict[str, Dict]:
    """Get current department configuration (either from file or default)"""
    return load_department_config()

def period_key(dept: str, month: int, year: int) -> str:
    return f"{dept}|{month}|{year}"

def get_saved_period(dept: str, month: int, year: int) -> Dict[str, str]:
    store = load_store()
    return store.get(period_key(dept, month, year), {})

def set_saved_period(dept: str, month: int, year: int, data: Dict[str, str]) -> None:
    store = load_store()
    store[period_key(dept, month, year)] = data
    save_store(store)

def get_month_dates(year: int, month: int) -> List[date]:
    """
    Return dates covering full weeks (Mon-Sun) that belong to this month's rota.
    Complete weekly cycles ensure that if a month ends mid-week, that entire week
    belongs to the previous month's rota (you can't change shifts mid-week).
    
    Logic:
    1. Find all days in the calendar month
    2. Find the first Monday that starts a week entirely within or starting in this month
    3. Continue adding complete weeks (Mon-Sun) until we would start a week that
       has its Monday in the next month
    4. If the month ends mid-week, that partial week belongs to the next month's rota
    """
    # Get first and last day of the target month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Find the first Monday that starts a week we want to include
    # This should be the first Monday that falls within the month
    current = first_day
    while current.weekday() != 0:  # 0 = Monday
        current += timedelta(days=1)
        # If we go past the month looking for Monday, start from the first Monday after month start
        if current.month != month:
            # The first day was not Monday and there's no Monday in this month
            # Find the first Monday on or after the 1st
            current = first_day
            while current.weekday() != 0:
                current += timedelta(days=1)
            break
    
    dates: List[date] = []
    
    # Add complete weeks (Monday to Sunday)
    week_start = current
    while True:
        # Check if this week's Monday is still in our target month or 
        # if it's the continuation of a week that started in our month
        if week_start.month != month:
            # If we've moved to the next month, we're done
            break
            
        # Add the complete week (7 days starting from Monday)
        for day_offset in range(7):
            week_day = week_start + timedelta(days=day_offset)
            dates.append(week_day)
        
        # Move to the next Monday
        week_start += timedelta(days=7)
        
        # Safety check: if the next Monday is more than a month away, break
        if week_start > last_day + timedelta(days=31):
            break
    
    return dates

def default_shift_for(d: date) -> str:
    # Saturday=5, Sunday=6
    return 'WO' if d.weekday() in (5, 6) else 'General'

def can_edit() -> bool:
    # Allow edit if Azure user authenticated or department user session present
    return bool(session.get('user')) or bool(session.get('department_user'))

def get_user_department() -> str:
    # Get the department for the current user
    return session.get('department_user', '')

def can_edit_department(dept_name: str) -> bool:
    # Check if user can edit this specific department
    user_dept = get_user_department()
    return bool(session.get('user')) or (user_dept == dept_name)

def parse_filter_list(param_name: str) -> List[str]:
    vals = request.args.getlist(param_name)
    # Clean empty strings
    return [v for v in vals if v]

def build_rows(dept_name: str, month: int, year: int, selected_processes: List[str], selected_shifts: List[str]) -> Tuple[List[Dict], List[Dict[str, str]], Dict[str, str]]:
    departments = get_current_departments()
    dept = departments.get(dept_name)
    if not dept or not dept.get('processes'):
        return [], [], {}

    dates = get_month_dates(year, month)
    date_headers: List[Dict[str, str]] = []
    for d in dates:
        date_headers.append({
            'date_str': d.isoformat(),
            'weekday': d.strftime('%a'),
            'day': str(d.day),
            'month_short': d.strftime('%b')
        })

    saved = get_saved_period(dept_name, month, year)
    rows = []
    for process, employees in dept['processes'].items():
        if selected_processes and process not in selected_processes:
            continue
        for emp in employees:
            cells = []
            row_has_selected_shift = False
            for d in dates:
                key = f"{process}|{emp}|{d.isoformat()}"
                current = saved.get(key) or default_shift_for(d)
                cells.append({
                    'date_str': d.isoformat(),
                    'value': current,
                    'key': key,
                })
                if selected_shifts and (current in selected_shifts):
                    row_has_selected_shift = True
            if selected_shifts and not row_has_selected_shift:
                continue
            rows.append({
                'process': process,
                'employee': emp,
                'cells': cells
            })

    return rows, date_headers, dept['shifts']

# --- Routes ---
@app.route('/')
def index():
    # Clear department-specific session when returning to home page
    session.pop('department_user', None)
    
    # If SSO enabled, redirect unauthenticated users as before
    if 'azure' in globals() and 'user' not in session:
        return redirect(url_for('login'))
    
    departments = list(get_current_departments().keys())
    # Default to current month/year
    today = date.today()
    return render_template('index.html', departments=departments, default_month=today.month, default_year=today.year, can_edit=can_edit())

@app.route('/dept')
def department():
    name = request.args.get('name')
    departments = get_current_departments()
    if not name or name not in departments:
        abort(404)
    try:
        month = int(request.args.get('month') or date.today().month)
        year = int(request.args.get('year') or date.today().year)
    except ValueError:
        abort(400)

    selected_processes = parse_filter_list('process')
    selected_shifts = parse_filter_list('shift')

    rows, date_headers, shifts = build_rows(name, month, year, selected_processes, selected_shifts)
    dept = departments[name]
    
    # Check if user can edit this specific department
    can_edit_dept = can_edit_department(name)
    user_dept = get_user_department()
    
    # If user is logged into a different department, show read-only
    if user_dept and user_dept != name:
        can_edit_dept = False

    return render_template(
        'dept.html',
        dept_name=name,
        month=month,
        year=year,
        rows=rows,
        date_headers=date_headers,
        shifts=shifts,
        all_processes=list(dept.get('processes', {}).keys()),
        all_shifts=list(shifts.keys()),
        selected_processes=selected_processes,
        selected_shifts=selected_shifts,
        show_filters=bool(dept.get('show_filters')),
        can_edit=can_edit_dept,
        user_department=user_dept,
        is_authenticated_for_dept=(user_dept == name)
    )

@app.route('/update', methods=['POST'])
def update():
    name = request.form.get('name')
    departments = get_current_departments()
    if not name or name not in departments:
        abort(404)
    try:
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
    except (TypeError, ValueError):
        abort(400)

    # Check if user can edit this specific department
    if not can_edit_department(name):
        abort(403)

    saved = get_saved_period(name, month, year)

    # Expect field names like: cell[PROCESS][EMPLOYEE][YYYY-MM-DD]
    for k, v in request.form.items():
        if not k.startswith('cell['):
            continue
        # Parse using a simple bracket split
        # k format: cell[process][employee][date]
        try:
            # Remove leading 'cell[' and trailing ']'
            inner = k[5:-1]
            process, employee, date_str = inner.split('][')
        except Exception:
            continue
        cell_key = f"{process}|{employee}|{date_str}"
        if v:
            saved[cell_key] = v
        else:
            # Empty selection removes override (fall back to default)
            if cell_key in saved:
                saved.pop(cell_key)

    set_saved_period(name, month, year, saved)

    # Preserve filters if posted (optional)
    qp = {'name': name, 'month': month, 'year': year}
    # Add back any posted filter params
    for p in request.form.getlist('process'):
        qp.setdefault('process', [])
        qp['process'].append(p)
    for s in request.form.getlist('shift'):
        qp.setdefault('shift', [])
        qp['shift'].append(s)

    # Build redirect URL with multiple values if present
    from urllib.parse import urlencode
    query_parts = []
    for key, val in qp.items():
        if isinstance(val, list):
            for item in val:
                query_parts.append((key, item))
        else:
            query_parts.append((key, str(val)))
    return redirect(url_for('department') + '?' + urlencode(query_parts))

@app.route('/export')
def export_csv():
    name = request.args.get('name')
    departments = get_current_departments()
    if not name or name not in departments:
        abort(404)
    try:
        month = int(request.args.get('month') or date.today().month)
        year = int(request.args.get('year') or date.today().year)
    except ValueError:
        abort(400)

    selected_processes = parse_filter_list('process')
    selected_shifts = parse_filter_list('shift')
    rows, date_headers, _ = build_rows(name, month, year, selected_processes, selected_shifts)

    # Build CSV text
    headers = ['Process', 'Employee'] + [f"{h['weekday']} {h['day']} {h['month_short']}" for h in date_headers]
    lines = []
    lines.append(','.join(['"' + h.replace('"', '""') + '"' for h in headers]))
    for row in rows:
        cols = [row['process'], row['employee']] + [c['value'] for c in row['cells']]
        esc = ['"' + str(x).replace('"', '""') + '"' for x in cols]
        lines.append(','.join(esc))
    csv_text = '\n'.join(lines) + '\n'

    resp = make_response(csv_text)
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = f'attachment; filename="{name}_ShiftRota_{year}-{month:02d}.csv"'
    return resp

# --- Department-specific login ---
@app.route('/department-login', methods=['POST'])
def department_login():
    """Handle AJAX department-specific login requests"""
    from flask import jsonify
    
    department = request.form.get('department', '')
    password = request.form.get('password', '')
    
    if not department or not password:
        return jsonify({'success': False, 'message': 'Department and password are required.'})
    
    departments = get_current_departments()
    if department not in departments:
        return jsonify({'success': False, 'message': 'Invalid department.'})
    
    dept_password = departments[department].get('password', '')
    if password == dept_password:
        # Clear any existing sessions
        session.pop('user', None)
        session.pop('editor', None)
        session.pop('department_user', None)
        
        # Set department-specific session
        session['department_user'] = department
        return jsonify({'success': True, 'message': f'Logged into {department}'})
    else:
        return jsonify({'success': False, 'message': 'Invalid password for this department.'})

@app.route('/local-login', methods=['GET', 'POST'])
def local_login():
    message = None
    if request.method == 'POST':
        department = request.form.get('department', '')
        password = request.form.get('password', '')
        
        # Check global admin password
        if password == EDITOR_PASSWORD:
            session['editor'] = True
            return redirect(url_for('index'))
        
        # Check department-specific password
        departments = get_current_departments()
        if department and department in departments:
            dept_password = departments[department].get('password', '')
            if password == dept_password:
                session['department_user'] = department
                return redirect(url_for('index'))
        
        message = 'Invalid department or password.'
    
    departments = list(get_current_departments().keys())
    return render_template('login.html', message=message, can_edit=can_edit(), departments=departments)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Azure user (if any)
    session.pop('editor', None)  # Local editor session
    session.pop('department_user', None)  # Department user session
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    message = None
    success = False
    error = False
    
    # Clean up expired tokens on each request
    cleanup_expired_tokens()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'send_reset_email':
            department = request.form.get('department', '').strip()
            
            if not department:
                message = 'Please select a department.'
                error = True
            elif department not in get_current_departments():
                message = 'Invalid department selected.'
                error = True
            else:
                # Create reset token
                token = create_reset_token(department)
                
                # Send email
                email_sent, email_message = send_reset_email(department, token)
                
                if email_sent:
                    message = f'Password reset email sent! {email_message}'
                    success = True
                else:
                    message = f'Failed to send reset email: {email_message}'
                    error = True
        
        elif action == 'send_sms_otp':
            department = request.form.get('department', '').strip()
            
            if not department:
                message = 'Please select a department.'
                error = True
            elif department not in get_current_departments():
                message = 'Invalid department selected.'
                error = True
            elif department not in DEPARTMENT_ADMIN_PHONES:
                message = f'SMS OTP is not configured for {department}. Please use email reset or contact administrator.'
                error = True
            else:
                # Create OTP token
                otp_code = create_otp_token(department)
                
                # Send SMS
                sms_sent, sms_message = send_otp_sms(department, otp_code)
                
                if sms_sent:
                    message = f'OTP sent via SMS to {department} administrators! {sms_message}'
                    success = True
                else:
                    message = f'Failed to send OTP: {sms_message}'
                    error = True
        
        elif action == 'verify_otp':
            department = request.form.get('department', '').strip()
            otp_code = request.form.get('otp_code', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not all([department, otp_code, new_password, confirm_password]):
                message = 'All fields are required for OTP verification.'
                error = True
            elif new_password != confirm_password:
                message = 'Passwords do not match.'
                error = True
            elif len(new_password) < 6:
                message = 'Password must be at least 6 characters long.'
                error = True
            else:
                # Validate OTP
                validated_dept, validation_message = validate_otp_token(otp_code)
                
                if not validated_dept:
                    # Increment attempt counter
                    increment_otp_attempts(otp_code)
                    message = f'OTP verification failed: {validation_message}'
                    error = True
                elif validated_dept != department:
                    message = 'OTP does not match the selected department.'
                    error = True
                else:
                    # OTP is valid, update password
                    departments = get_current_departments()
                    departments[department]['password'] = new_password
                    save_department_config(departments)
                    
                    # Remove used OTP
                    consume_otp_token(otp_code)
                    
                    message = f'Password for {department} has been successfully updated using SMS OTP!'
                    success = True
        
        elif action == 'emergency_request':
            requester_name = request.form.get('requester_name', '').strip()
            department = request.form.get('department', '').strip()
            email = request.form.get('email', '').strip()
            reason = request.form.get('reason', '').strip()
            
            if not all([requester_name, department, email, reason]):
                message = 'All fields are required for emergency access request.'
                error = True
            else:
                # In a real application, this would send an email or create a ticket
                # For demo purposes, we'll just show a success message
                message = f'Emergency access request submitted successfully! An administrator will review your request for {department} access and respond to {email} within 24 hours.'
                success = True
                
                # Log the request (in production, this would go to a proper logging system)
                import logging
                logging.info(f'Emergency access request: {requester_name} ({email}) requesting {department} access. Reason: {reason}')
    
    departments = list(get_current_departments().keys())
    return render_template('forgot_password.html', 
                         message=message, 
                         success=success,
                         error=error,
                         departments=departments)

@app.route('/debug-forgot-password')
def debug_forgot_password():
    """Debug route to check template version"""
    return "Template version: 2FA Email Reset Integration Active - Check lines 15-38 in forgot_password.html"

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token validation"""
    # Clean up expired tokens
    cleanup_expired_tokens()
    
    # Validate token
    department = validate_reset_token(token)
    
    if not department:
        return render_template('password_reset.html', 
                             error="Invalid or expired reset token. Please request a new password reset.",
                             token_valid=False)
    
    message = None
    success = False
    error = False
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not new_password:
            message = 'Password cannot be empty.'
            error = True
        elif new_password != confirm_password:
            message = 'Passwords do not match.'
            error = True
        elif len(new_password) < 6:
            message = 'Password must be at least 6 characters long.'
            error = True
        else:
            # Update password
            departments = get_current_departments()
            departments[department]['password'] = new_password
            save_department_config(departments)
            
            # Remove used token
            tokens = load_reset_tokens()
            if token in tokens:
                del tokens[token]
                save_reset_tokens(tokens)
            
            message = f'Password for {department} has been successfully updated!'
            success = True
    
    return render_template('password_reset.html', 
                         department=department,
                         token=token,
                         token_valid=True,
                         message=message,
                         success=success,
                         error=error)

@app.route('/department-settings', methods=['GET', 'POST'])
def department_settings():
    # Only allow access if user is logged in
    if not can_edit():
        abort(403)
    
    user_dept = get_user_department()
    is_admin = bool(session.get('editor'))
    
    # If not admin, can only access own department settings
    if not is_admin and not user_dept:
        abort(403)
    
    departments = get_current_departments()
    message = None
    success = False
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_password':
            target_dept = request.form.get('target_department', user_dept)
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Security check: non-admin users can only change their own dept password
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not new_password:
                message = 'Password cannot be empty.'
            elif new_password != confirm_password:
                message = 'Passwords do not match.'
            elif len(new_password) < 6:
                message = 'Password must be at least 6 characters long.'
            else:
                # Update password in department config
                departments[target_dept]['password'] = new_password
                save_department_config(departments)
                message = f'Password updated successfully for {target_dept}!'
                success = True
        
        elif action == 'add_employee':
            target_dept = request.form.get('target_department', user_dept)
            process = request.form.get('process', '').strip()
            employee_name = request.form.get('employee_name', '').strip()
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not process or not employee_name:
                message = 'Process and employee name are required.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            else:
                if process not in departments[target_dept]['processes']:
                    departments[target_dept]['processes'][process] = []
                
                if employee_name not in departments[target_dept]['processes'][process]:
                    departments[target_dept]['processes'][process].append(employee_name)
                    # Sort employees alphabetically
                    departments[target_dept]['processes'][process].sort()
                    save_department_config(departments)
                    message = f'Employee "{employee_name}" added to {process} in {target_dept}!'
                    success = True
                else:
                    message = f'Employee "{employee_name}" already exists in {process}.'
        
        elif action == 'remove_employee':
            target_dept = request.form.get('target_department', user_dept)
            process = request.form.get('process', '')
            employee_name = request.form.get('employee_name', '')
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if target_dept in departments and process in departments[target_dept]['processes']:
                if employee_name in departments[target_dept]['processes'][process]:
                    departments[target_dept]['processes'][process].remove(employee_name)
                    # Clean up empty processes
                    if not departments[target_dept]['processes'][process]:
                        del departments[target_dept]['processes'][process]
                    save_department_config(departments)
                    message = f'Employee "{employee_name}" removed from {process} in {target_dept}!'
                    success = True
                else:
                    message = 'Employee not found.'
            else:
                message = 'Process not found.'
        
        elif action == 'add_shift':
            target_dept = request.form.get('target_department', user_dept)
            shift_code = request.form.get('shift_code', '').strip()
            shift_description = request.form.get('shift_description', '').strip()
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not shift_code or not shift_description:
                message = 'Shift code and description are required.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            elif shift_code in departments[target_dept]['shifts']:
                message = f'Shift code "{shift_code}" already exists.'
            else:
                departments[target_dept]['shifts'][shift_code] = shift_description
                save_department_config(departments)
                message = f'Shift "{shift_code}" added to {target_dept}!'
                success = True
        
        elif action == 'remove_shift':
            target_dept = request.form.get('target_department', user_dept)
            shift_code = request.form.get('shift_code', '')
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if target_dept in departments and shift_code in departments[target_dept]['shifts']:
                del departments[target_dept]['shifts'][shift_code]
                save_department_config(departments)
                message = f'Shift "{shift_code}" removed from {target_dept}!'
                success = True
            else:
                message = 'Shift not found.'
        
        elif action == 'edit_employee':
            target_dept = request.form.get('target_department', user_dept)
            old_process = request.form.get('old_process', '')
            old_employee = request.form.get('old_employee', '')
            new_process = request.form.get('new_process', '').strip()
            new_employee = request.form.get('new_employee', '').strip()
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not old_process or not old_employee or not new_process or not new_employee:
                message = 'All employee fields are required.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            elif old_process not in departments[target_dept]['processes']:
                message = 'Original process not found.'
            elif old_employee not in departments[target_dept]['processes'][old_process]:
                message = 'Original employee not found.'
            else:
                # Check if new employee name already exists in the new process (unless it's the same employee)
                if new_process in departments[target_dept]['processes']:
                    if new_employee in departments[target_dept]['processes'][new_process] and (old_process != new_process or old_employee != new_employee):
                        message = f'Employee "{new_employee}" already exists in {new_process}.'
                    else:
                        # Remove from old location
                        departments[target_dept]['processes'][old_process].remove(old_employee)
                        
                        # Clean up empty process
                        if not departments[target_dept]['processes'][old_process]:
                            del departments[target_dept]['processes'][old_process]
                        
                        # Add to new location
                        if new_process not in departments[target_dept]['processes']:
                            departments[target_dept]['processes'][new_process] = []
                        departments[target_dept]['processes'][new_process].append(new_employee)
                        # Sort employees alphabetically
                        departments[target_dept]['processes'][new_process].sort()
                        
                        save_department_config(departments)
                        message = f'Employee updated from "{old_process}:{old_employee}" to "{new_process}:{new_employee}" in {target_dept}!'
                        success = True
                else:
                    # New process doesn't exist, create it
                    departments[target_dept]['processes'][old_process].remove(old_employee)
                    
                    # Clean up empty process
                    if not departments[target_dept]['processes'][old_process]:
                        del departments[target_dept]['processes'][old_process]
                    
                    departments[target_dept]['processes'][new_process] = [new_employee]
                    # Sort employees alphabetically (though it's just one employee, good practice)
                    departments[target_dept]['processes'][new_process].sort()
                    save_department_config(departments)
                    message = f'Employee updated from "{old_process}:{old_employee}" to "{new_process}:{new_employee}" in {target_dept}!'
                    success = True
        
        elif action == 'add_user':
            target_dept = request.form.get('target_department', user_dept)
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            role = request.form.get('role', '').strip()
            initial_password = request.form.get('initial_password', '')
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not username or not email or not role or not initial_password:
                message = 'All user fields are required.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            elif role not in ['viewer', 'editor', 'admin']:
                message = 'Invalid role specified.'
            elif role == 'admin' and not is_admin:
                message = 'Only system administrators can create admin users.'
            elif len(initial_password) < 6:
                message = 'Password must be at least 6 characters long.'
            else:
                # Initialize users dict if it doesn't exist
                if 'users' not in departments[target_dept]:
                    departments[target_dept]['users'] = {}
                
                # Check if username already exists
                existing_usernames = [u['username'] for u in departments[target_dept]['users'].values()]
                if username in existing_usernames:
                    message = f'Username "{username}" already exists in {target_dept}.'
                else:
                    # Generate unique user ID
                    import uuid
                    user_id = str(uuid.uuid4())
                    
                    # Hash password (simple hash for demo - use proper hashing in production)
                    import hashlib
                    password_hash = hashlib.sha256(initial_password.encode()).hexdigest()
                    
                    departments[target_dept]['users'][user_id] = {
                        'username': username,
                        'email': email,
                        'role': role,
                        'password_hash': password_hash,
                        'active': True,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    save_department_config(departments)
                    message = f'User "{username}" added successfully to {target_dept}!'
                    success = True
        
        elif action == 'edit_user':
            target_dept = request.form.get('target_department', user_dept)
            user_id = request.form.get('user_id', '').strip()
            new_email = request.form.get('new_email', '').strip()
            new_role = request.form.get('new_role', '').strip()
            reset_password = request.form.get('reset_password', '')
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not user_id:
                message = 'Please select a user to edit.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            elif 'users' not in departments[target_dept] or user_id not in departments[target_dept]['users']:
                message = 'User not found.'
            elif new_role and new_role not in ['viewer', 'editor', 'admin']:
                message = 'Invalid role specified.'
            elif new_role == 'admin' and not is_admin:
                message = 'Only system administrators can assign admin roles.'
            elif reset_password and len(reset_password) < 6:
                message = 'Password must be at least 6 characters long.'
            else:
                user_data = departments[target_dept]['users'][user_id]
                old_username = user_data['username']
                changes = []
                
                # Update email if provided
                if new_email:
                    user_data['email'] = new_email
                    changes.append(f'email to {new_email}')
                
                # Update role if provided
                if new_role:
                    user_data['role'] = new_role
                    changes.append(f'role to {new_role}')
                
                # Reset password if provided
                if reset_password:
                    import hashlib
                    user_data['password_hash'] = hashlib.sha256(reset_password.encode()).hexdigest()
                    changes.append('password')
                
                if changes:
                    user_data['updated_at'] = datetime.now().isoformat()
                    save_department_config(departments)
                    message = f'User "{old_username}" updated: {', '.join(changes)}!'
                    success = True
                else:
                    message = 'No changes specified.'
        
        elif action == 'remove_user':
            target_dept = request.form.get('target_department', user_dept)
            user_id = request.form.get('user_id', '').strip()
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not user_id:
                message = 'Please select a user to remove.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            elif 'users' not in departments[target_dept] or user_id not in departments[target_dept]['users']:
                message = 'User not found.'
            else:
                removed_username = departments[target_dept]['users'][user_id]['username']
                del departments[target_dept]['users'][user_id]
                
                save_department_config(departments)
                message = f'User "{removed_username}" removed from {target_dept}!'
                success = True
        
        elif action == 'edit_shift':
            target_dept = request.form.get('target_department', user_dept)
            old_shift_code = request.form.get('old_shift_code', '')
            new_shift_code = request.form.get('new_shift_code', '').strip()
            new_shift_description = request.form.get('new_shift_description', '').strip()
            
            if not is_admin and target_dept != user_dept:
                abort(403)
            
            if not old_shift_code or not new_shift_code or not new_shift_description:
                message = 'All shift fields are required.'
            elif target_dept not in departments:
                message = 'Invalid department.'
            elif old_shift_code not in departments[target_dept]['shifts']:
                message = 'Original shift not found.'
            elif new_shift_code in departments[target_dept]['shifts'] and old_shift_code != new_shift_code:
                message = f'Shift code "{new_shift_code}" already exists.'
            else:
                # Remove old shift if code changed
                if old_shift_code != new_shift_code:
                    del departments[target_dept]['shifts'][old_shift_code]
                
                # Add/update new shift
                departments[target_dept]['shifts'][new_shift_code] = new_shift_description
                save_department_config(departments)
                message = f'Shift updated from "{old_shift_code}" to "{new_shift_code}: {new_shift_description}" in {target_dept}!'
                success = True
        
        # Reload departments after changes
        departments = get_current_departments()
    
    available_departments = [user_dept] if user_dept and not is_admin else list(departments.keys())
    
    return render_template('department_settings.html', 
                         message=message, 
                         success=success,
                         user_department=user_dept,
                         is_admin=is_admin,
                         available_departments=available_departments,
                         departments=departments,
                         can_edit=can_edit())

@app.route('/minimal-settings')
def minimal_settings():
    """Minimal test page for department settings"""
    user_dept = get_user_department()
    is_admin = bool(session.get('editor'))
    
    try:
        departments = get_current_departments()
        available_departments = [user_dept] if user_dept and not is_admin else list(departments.keys())
    except Exception as e:
        departments = {'error': str(e)}
        available_departments = []
    
    return render_template('minimal_settings.html',
                         user_department=user_dept,
                         is_admin=is_admin,
                         available_departments=available_departments,
                         departments=departments,
                         can_edit=can_edit)

@app.route('/debug-settings')
def debug_settings():
    """Debug page to check department settings data"""
    user_dept = get_user_department()
    is_admin = bool(session.get('editor'))
    
    try:
        departments = get_current_departments()
        available_departments = [user_dept] if user_dept and not is_admin else list(departments.keys())
    except Exception as e:
        departments = {'error': str(e)}
        available_departments = []
    
    return render_template('debug_settings.html',
                         user_department=user_dept,
                         is_admin=is_admin,
                         available_departments=available_departments,
                         departments=departments,
                         can_edit=can_edit)

@app.route('/test-edit-features')
def test_edit_features():
    """Diagnostic page to test if edit features are working"""
    from datetime import datetime
    import os
    
    # Check if template has edit features
    try:
        with open('templates/department_settings.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        edit_employee_exists = 'action="edit_employee"' in template_content
        edit_shift_exists = 'action="edit_shift"' in template_content
        warning_css_exists = 'btn-warning' in template_content
    except:
        edit_employee_exists = edit_shift_exists = warning_css_exists = False
    
    # Check if backend routes exist
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        backend_routes_exist = "action == 'edit_employee'" in app_content and "action == 'edit_shift'" in app_content
    except:
        backend_routes_exist = False
    
    # Check if config file exists
    config_exists = os.path.exists('department_config.json')
    
    # Get current session info
    user_dept = get_user_department()
    is_admin = bool(session.get('editor'))
    
    # Get departments data
    try:
        departments = get_current_departments()
        available_departments = [user_dept] if user_dept and not is_admin else list(departments.keys())
    except:
        departments = {}
        available_departments = []
    
    return render_template('test_edit_features.html',
                         timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         edit_employee_exists=edit_employee_exists,
                         edit_shift_exists=edit_shift_exists,
                         warning_css_exists=warning_css_exists,
                         backend_routes_exist=backend_routes_exist,
                         config_exists=config_exists,
                         user_department=user_dept,
                         is_admin=is_admin,
                         available_departments=available_departments,
                         departments=departments)

# --- Azure AD SSO routes (guarded) ---
@app.route('/login')
def login():
    if 'azure' not in globals():
        abort(404)
    return azure.authorize_redirect(url_for('authorize', _external=True))

@app.route('/authorize')
def authorize():
    if 'azure' not in globals():
        abort(404)
    token = azure.authorize_access_token()
    user = azure.parse_id_token(token)
    session['user'] = user
    return redirect(url_for('index'))

def calculate_allowance_period(month: int, year: int) -> Tuple[date, date]:
    """
    Calculate the allowance period from 26th of previous month to 25th of current month
    """
    if month == 1:
        start_date = date(year - 1, 12, 26)
    else:
        start_date = date(year, month - 1, 26)
    
    end_date = date(year, month, 25)
    return start_date, end_date

def get_dates_in_allowance_period(start_date: date, end_date: date) -> List[date]:
    """
    Get all dates in the allowance period
    """
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def calculate_night_shift_allowances(dept_name: str, month: int, year: int, shift_type: str) -> Dict:
    """
    Calculate night shift allowances for EST or PST shifts
    """
    start_date, end_date = calculate_allowance_period(month, year)
    period_dates = get_dates_in_allowance_period(start_date, end_date)
    
    # Define which shifts belong to which categories
    est_shifts = ['APAC', 'Afternoon']
    pst_shifts = ['Evening', 'Night']
    
    target_shifts = est_shifts if shift_type == 'EST' else pst_shifts
    
    # Load saved data for all months in the period
    employee_data = {}
    
    # Group dates by month to load the right data
    months_data = {}
    for d in period_dates:
        month_key = (d.year, d.month)
        if month_key not in months_data:
            months_data[month_key] = []
        months_data[month_key].append(d)
    
    # Load data for each month in the period
    all_saved_data = {}
    for (y, m), dates_in_month in months_data.items():
        saved = get_saved_period(dept_name, m, y)
        all_saved_data.update(saved)
    
    # Get department employees
    dept = DEPARTMENTS.get(dept_name, {})
    processes = dept.get('processes', {})
    
    for process, employees in processes.items():
        for emp in employees:
            employee_data[emp] = {'dates': [], 'total_days': 0}
            
            for d in period_dates:
                key = f"{process}|{emp}|{d.isoformat()}"
                shift = all_saved_data.get(key) or default_shift_for(d)
                
                if shift in target_shifts:
                    employee_data[emp]['dates'].append({
                        'date': d.isoformat(),
                        'shift': shift,
                        'weekday': d.strftime('%a')
                    })
                    employee_data[emp]['total_days'] += 1
    
    # Filter out employees with no qualifying shifts
    employee_data = {emp: data for emp, data in employee_data.items() if data['total_days'] > 0}
    
    return {
        'shift_type': shift_type,
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': end_date.strftime('%Y-%m-%d'),
        'target_shifts': target_shifts,
        'employees': employee_data
    }

def calculate_weekend_allowances(dept_name: str, month: int, year: int) -> Dict:
    """
    Calculate weekend allowances (both Saturday and Sunday = 1 shift, single day = 0.5 shift)
    """
    start_date, end_date = calculate_allowance_period(month, year)
    period_dates = get_dates_in_allowance_period(start_date, end_date)
    
    # Load saved data for all months in the period
    months_data = {}
    for d in period_dates:
        month_key = (d.year, d.month)
        if month_key not in months_data:
            months_data[month_key] = []
        months_data[month_key].append(d)
    
    all_saved_data = {}
    for (y, m), dates_in_month in months_data.items():
        saved = get_saved_period(dept_name, m, y)
        all_saved_data.update(saved)
    
    # Get department employees
    dept = DEPARTMENTS.get(dept_name, {})
    processes = dept.get('processes', {})
    
    employee_data = {}
    
    for process, employees in processes.items():
        for emp in employees:
            employee_data[emp] = {'weekends': [], 'total_allowances': 0.0}
            
            # Group dates by weekend (Saturday-Sunday pairs)
            weekends = {}
            for d in period_dates:
                if d.weekday() in [5, 6]:  # Saturday=5, Sunday=6
                    # Find the Saturday of this weekend
                    if d.weekday() == 5:  # Saturday
                        weekend_start = d
                    else:  # Sunday
                        weekend_start = d - timedelta(days=1)
                    
                    weekend_key = weekend_start.isoformat()
                    if weekend_key not in weekends:
                        weekends[weekend_key] = {'saturday': None, 'sunday': None, 'worked_days': []}
                    
                    key = f"{process}|{emp}|{d.isoformat()}"
                    shift = all_saved_data.get(key) or default_shift_for(d)
                    
                    # Check if actually worked (not WO, PL, AL, Holiday)
                    non_work_shifts = ['WO', 'PL', 'AL', 'Holiday']
                    if shift not in non_work_shifts:
                        if d.weekday() == 5:  # Saturday
                            weekends[weekend_key]['saturday'] = {'date': d, 'shift': shift}
                            weekends[weekend_key]['worked_days'].append(d)
                        else:  # Sunday
                            weekends[weekend_key]['sunday'] = {'date': d, 'shift': shift}
                            weekends[weekend_key]['worked_days'].append(d)
            
            # Calculate allowances for each weekend
            for weekend_start, weekend_data in weekends.items():
                worked_saturday = weekend_data['saturday'] is not None
                worked_sunday = weekend_data['sunday'] is not None
                
                if worked_saturday or worked_sunday:
                    if worked_saturday and worked_sunday:
                        allowance = 1.0  # Full weekend
                    else:
                        allowance = 0.5  # Half weekend
                    
                    employee_data[emp]['weekends'].append({
                        'weekend_start': weekend_start,
                        'saturday': weekend_data['saturday'],
                        'sunday': weekend_data['sunday'],
                        'allowance': allowance,
                        'worked_days': len(weekend_data['worked_days'])
                    })
                    employee_data[emp]['total_allowances'] += allowance
    
    # Filter out employees with no weekend work
    employee_data = {emp: data for emp, data in employee_data.items() if data['total_allowances'] > 0}
    
    return {
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': end_date.strftime('%Y-%m-%d'),
        'employees': employee_data
    }

@app.route('/night-shift-allowances')
def night_shift_allowances():
    dept = request.args.get('dept')
    month = int(request.args.get('month', date.today().month))
    year = int(request.args.get('year', date.today().year))
    shift_type = request.args.get('type', 'EST')
    
    if dept != 'Service Desk':
        abort(404)
    
    if not can_edit():
        abort(403)
    
    allowances_data = calculate_night_shift_allowances(dept, month, year, shift_type)
    
    return render_template('allowances.html', 
                         allowances_data=allowances_data,
                         dept_name=dept,
                         month=month,
                         year=year,
                         allowance_type='night_shift',
                         can_edit=can_edit())

@app.route('/weekend-allowances')
def weekend_allowances():
    dept = request.args.get('dept')
    month = int(request.args.get('month', date.today().month))
    year = int(request.args.get('year', date.today().year))
    
    if dept != 'Service Desk':
        abort(404)
    
    if not can_edit():
        abort(403)
    
    allowances_data = calculate_weekend_allowances(dept, month, year)
    
    return render_template('allowances.html', 
                         allowances_data=allowances_data,
                         dept_name=dept,
                         month=month,
                         year=year,
                         allowance_type='weekend',
                         can_edit=can_edit())

@app.route('/export-allowances')
def export_allowances():
    """Export allowances data as CSV"""
    dept = request.args.get('dept')
    month = int(request.args.get('month', date.today().month))
    year = int(request.args.get('year', date.today().year))
    allowance_type = request.args.get('type', 'EST')  # EST, PST, or Weekend
    
    if dept != 'Service Desk':
        abort(404)
    
    if not can_edit():
        abort(403)
    
    # Generate CSV based on allowance type
    if allowance_type in ['EST', 'PST']:
        # Night shift allowances
        allowances_data = calculate_night_shift_allowances(dept, month, year, allowance_type)
        csv_text = generate_night_shift_csv(allowances_data, allowance_type)
        filename = f"{dept}_{allowance_type}_Allowances_{year}-{month:02d}.csv"
    else:
        # Weekend allowances
        allowances_data = calculate_weekend_allowances(dept, month, year)
        csv_text = generate_weekend_allowances_csv(allowances_data)
        filename = f"{dept}_Weekend_Allowances_{year}-{month:02d}.csv"
    
    resp = make_response(csv_text)
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp

def generate_night_shift_csv(allowances_data, shift_type):
    """Generate CSV for night shift allowances (EST/PST)"""
    lines = []
    
    # Header information
    lines.append(f'"Night Shift Allowances - {shift_type}"')
    lines.append(f'"Period: {allowances_data["period_start"]} to {allowances_data["period_end"]}"')
    lines.append(f'"Target Shifts: {", ".join(allowances_data["target_shifts"])}"')
    lines.append('')  # Empty line
    
    # Table headers
    lines.append('"Employee Name","Total Days","Shift Details"')
    
    # Employee data
    for employee, data in allowances_data['employees'].items():
        shift_details = []
        for shift_info in data['dates']:
            shift_details.append(f"{shift_info['date']} ({shift_info['weekday']}): {shift_info['shift']}")
        
        shift_details_str = '; '.join(shift_details)
        lines.append(f'"{employee}","{data["total_days"]}","{shift_details_str}"')
    
    # Summary
    lines.append('')  # Empty line
    lines.append('"Summary"')
    total_employees = len(allowances_data['employees'])
    total_allowance_days = sum(data['total_days'] for data in allowances_data['employees'].values())
    lines.append(f'"Total Employees with {shift_type} Shifts: {total_employees}"')
    lines.append(f'"Total {shift_type} Shift Days: {total_allowance_days}"')
    
    return '\n'.join(lines) + '\n'

def generate_weekend_allowances_csv(allowances_data):
    """Generate CSV for weekend allowances"""
    lines = []
    
    # Header information
    lines.append('"Weekend Allowances Report"')
    lines.append(f'"Period: {allowances_data["period_start"]} to {allowances_data["period_end"]}"')
    lines.append('"Allowance Rules: Full Weekend (Sat+Sun) = 1.0, Single Day = 0.5"')
    lines.append('')  # Empty line
    
    # Table headers
    lines.append('"Employee Name","Total Allowances","Weekend Details"')
    
    # Employee data
    for employee, data in allowances_data['employees'].items():
        weekend_details = []
        for weekend in data['weekends']:
            weekend_start = datetime.fromisoformat(weekend['weekend_start']).strftime('%Y-%m-%d')
            days_worked = []
            if weekend['saturday']:
                days_worked.append(f"Sat({weekend['saturday']['shift']})")
            if weekend['sunday']:
                days_worked.append(f"Sun({weekend['sunday']['shift']})")
            
            weekend_details.append(f"{weekend_start}: {'+'.join(days_worked)} = {weekend['allowance']}")
        
        weekend_details_str = '; '.join(weekend_details)
        lines.append(f'"{employee}","{data["total_allowances"]}","{weekend_details_str}"')
    
    # Summary
    lines.append('')  # Empty line
    lines.append('"Summary"')
    total_employees = len(allowances_data['employees'])
    total_allowances = sum(data['total_allowances'] for data in allowances_data['employees'].values())
    lines.append(f'"Total Employees with Weekend Work: {total_employees}"')
    lines.append(f'"Total Weekend Allowances: {total_allowances}"')
    
    return '\n'.join(lines) + '\n'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
