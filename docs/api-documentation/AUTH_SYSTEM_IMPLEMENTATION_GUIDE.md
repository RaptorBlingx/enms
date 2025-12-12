# 🔐 Complete Authentication System Implementation Guide

**Version:** 1.0  
**Last Updated:** December 11, 2025  
**Tested On:** ENMS Demo Platform

---

## 📋 Overview

Production-ready authentication system with user registration, email verification, JWT sessions, admin dashboard, role-based access, and SMTP email notifications.

---

## 🎯 Core Features

- User registration & email verification (24-hour token expiry)
- Secure login with JWT sessions (7-day expiration)
- Password hashing with bcrypt (12 rounds)
- Admin dashboard with user management
- Real-time admin notifications on new signups
- Password reset functionality
- Role-based access control (admin/user)
- Session tracking & audit logs
- Professional HTML email templates

---

## 🏗️ Architecture & Routing

### Landing Page Strategy
**Main entry point:** `auth.html` (Login/Registration page)

When users first visit the website, they land on the authentication page. Public pages (About, ISO 50001, Contact) are accessible without authentication, similar to a marketing website structure.

**Public Routes (No Auth Required):**
- `/auth.html` - Main landing page (Login/Signup forms)
- `/about.html` - About page
- `/iso50001.html` - ISO 50001 Alignment page
- `/contact.html` - Contact page
- `/verify-email.html` - Email verification handler
- `/reset-password.html` - Password reset handler

**Protected Routes (Auth Required):**
- `/index.html` - Main application dashboard
- `/admin/dashboard.html` - Admin panel (restricted to ADMIN_EMAILS)
- All other application pages

**Frontend Navigation:**
Add header navigation to auth.html and public pages with links to About, ISO50001, Contact. After login, redirect to `/index.html`.

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE public.demo_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    organization VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    mobile VARCHAR(50),
    country VARCHAR(100) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_sent_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    password_reset_token VARCHAR(255),
    password_reset_sent_at TIMESTAMP WITH TIME ZONE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    ip_address_signup VARCHAR(50),
    user_agent TEXT,
    CONSTRAINT email_lowercase CHECK (email = LOWER(email))
);

CREATE INDEX idx_demo_users_email ON public.demo_users(email);
CREATE INDEX idx_demo_users_verification_token ON public.demo_users(verification_token);
CREATE INDEX idx_demo_users_password_reset_token ON public.demo_users(password_reset_token);
CREATE INDEX idx_demo_users_role ON public.demo_users(role);
```

### Sessions Table
```sql
CREATE TABLE public.demo_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.demo_users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_demo_sessions_user_id ON public.demo_sessions(user_id);
CREATE INDEX idx_demo_sessions_token ON public.demo_sessions(session_token);
```

### Audit Log Table
```sql
CREATE TABLE public.demo_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.demo_users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(50),
    user_agent TEXT,
    metadata JSONB
);

CREATE INDEX idx_demo_audit_log_user_id ON public.demo_audit_log(user_id);
CREATE INDEX idx_demo_audit_log_action ON public.demo_audit_log(action);
```

---

## 🔧 Environment Variables

```bash
# PostgreSQL Database
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# JWT Authentication
JWT_SECRET=your_super_secret_jwt_key_change_in_production

# Frontend URL (for email links)
FRONTEND_URL=https://yourdomain.com

# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=swe.mohamad.jarad@gmail.com
SMTP_PASSWORD=miuv tazo cgzm tlbs
SMTP_FROM_EMAIL=swe.mohamad.jarad@gmail.com
SMTP_FROM_NAME=ENMS Demo Platform

# Admin & Notifications
ADMIN_EMAILS=swe.mohamad.jarad@gmail.com,umut.ogur@aartimuhendislik.com
SIGNUP_ALERT_RECIPIENTS=swe.mohamad.jarad@gmail.com,umut.ogur@aartimuhendislik.com
```

**Gmail App Password Setup:**
1. Enable 2FA on Gmail
2. Visit: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Use 16-character password in `SMTP_PASSWORD`

---

## 🐍 Backend Core Functions

### Password Management
```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

### JWT Tokens
```python
def generate_token(user_id: int, email: str, role: str = 'user') -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=168),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
```

### Email Verification
```python
def send_verification_email(email: str, token: str, full_name: str) -> bool:
    verification_link = f"{FRONTEND_URL}/verify-email.html?token={token}"
    # Send professional HTML email with verification link
    # Token expires in 24 hours
```

### Admin Notification
```python
def send_signup_notification(user_data: dict) -> bool:
    recipients = SIGNUP_ALERT_RECIPIENTS
    # Send email to all recipients with:
    # - Full name, email, organization, position, mobile, country
    # - IP address and timestamp for security
```

### User Registration
```python
def register_user(email, password, organization, full_name, position, mobile, country, ip_address, user_agent):
    # 1. Validate email and password (min 8 chars)
    # 2. Check if email already exists
    # 3. Determine role: 'admin' if email in ADMIN_EMAILS, else 'user'
    # 4. Hash password and generate verification token
    # 5. Insert into database
    # 6. Send verification email to user
    # 7. Send signup notification to admins
    # 8. Return success response
```

### Admin Access Control
```python
@wraps(f)
def require_admin(f):
    # 1. Extract JWT token from Authorization header
    # 2. Verify token validity
    # 3. Check if user email is in ADMIN_EMAILS allowlist
    # 4. Query database to verify role='admin' and is_active=true
    # 5. Return 403 if any check fails
```

---

## 🌐 Flask API Endpoints

```python
POST /api/auth/register      # User registration
POST /api/auth/login         # User login (returns JWT token)
POST /api/auth/verify-email  # Verify email with token
POST /api/auth/forgot-password
POST /api/auth/reset-password
POST /api/auth/logout

GET  /api/admin/users        # List users (paginated, searchable) - @require_admin
GET  /api/admin/stats        # User statistics - @require_admin
GET  /api/admin/export-users # Export CSV - @require_admin
```

---

## 🎨 Frontend Structure

```
frontend/
├── auth.html              # Landing page: Login & Registration (MAIN ENTRY)
├── about.html            # Public page
├── iso50001.html         # Public page
├── contact.html          # Public page
├── verify-email.html     # Email verification handler
├── reset-password.html   # Password reset handler
├── index.html            # Main dashboard (protected)
└── admin/
    └── dashboard.html    # Admin panel (protected, admin-only)
```

**Navigation Header (auth.html and public pages):**
- Logo
- Links: Home | About | ISO 50001 | Contact
- Login/Signup buttons (if on auth.html, show tabs)

**Session Management:**
- Store JWT token in `localStorage.getItem('auth_token')`
- Store user data in `localStorage.getItem('user_data')`
- Protected pages check for valid token on load
- Admin pages verify `user.role === 'admin'` and email in allowlist

**Admin Dashboard Features:**
- User statistics cards (total, verified, new today, active 7 days)
- Searchable user table with horizontal scroll
- Pagination (20 users per page)
- User details: ID, Name, Email, Mobile, Organization, Country, Status, Role, Created, Last Login
- Export users to CSV

---

## 🔒 Security Checklist

- [ ] Strong JWT_SECRET (64+ random characters)
- [ ] HTTPS enabled in production
- [ ] SMTP credentials as app password, not regular password
- [ ] Admin allowlist configured in ADMIN_EMAILS
- [ ] Password minimum 8 characters (consider complexity rules)
- [ ] Email lowercase constraint in database
- [ ] Parameterized SQL queries (prevent injection)
- [ ] Rate limiting on auth endpoints
- [ ] CORS properly configured

---

## 🚀 Quick Implementation Steps

1. Create database tables (run SQL schema)
2. Set all environment variables in `.env`
3. Implement `auth_service.py` with core functions
4. Create Flask API endpoints in `app.py`
5. Build `auth.html` with login/signup forms
6. Add verification and password reset pages
7. Create admin dashboard
8. Test full flow: register → verify email → login → admin access
9. Verify admin receives signup notification emails

---

## 📚 Dependencies

```txt
Flask==3.0.0
flask-cors==4.0.0
psycopg2-binary==2.9.9
PyJWT==2.8.0
bcrypt==4.1.1
email-validator==2.1.0
gunicorn==21.2.0
```

---

## 🧪 Testing

```bash
# Register new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123","organization":"Test Org","full_name":"Test User","position":"Developer","mobile":"+1234567890","country":"USA"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# Admin stats
curl -X GET http://localhost:5000/api/admin/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

**Reference Project:** ENMS Demo Platform  
**Date:** December 2025

---

## 🎯 Implementation Notes

This guide is designed to be concise and action-oriented. The implementing agent should have sufficient context to:
- Set up the database schema
- Implement backend authentication logic
- Create frontend auth pages
- Configure email notifications
- Set up admin access controls

The architecture prioritizes security, user experience, and maintainability. All code patterns are production-tested from the ENMS Demo Platform.

### 1. Users Table (`demo_users`)

```sql
CREATE TABLE public.demo_users (
    id SERIAL PRIMARY KEY,
    
    -- Core Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- User Information
    organization VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    mobile VARCHAR(50),
    country VARCHAR(100) NOT NULL,
    
    -- Email Verification
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_sent_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Password Reset
    password_reset_token VARCHAR(255),
    password_reset_sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Role Management
    role VARCHAR(50) DEFAULT 'user', -- 'user', 'admin'
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Account Status
    is_active BOOLEAN DEFAULT TRUE,
    deactivated_at TIMESTAMP WITH TIME ZONE,
    
    -- Tracking
    ip_address_signup VARCHAR(50),
    user_agent TEXT,
    
    CONSTRAINT email_lowercase CHECK (email = LOWER(email))
);

-- Indexes
CREATE INDEX idx_demo_users_email ON public.demo_users(email);
CREATE INDEX idx_demo_users_verification_token ON public.demo_users(verification_token);
CREATE INDEX idx_demo_users_password_reset_token ON public.demo_users(password_reset_token);
CREATE INDEX idx_demo_users_created_at ON public.demo_users(created_at);
CREATE INDEX idx_demo_users_role ON public.demo_users(role);
```

### 2. Sessions Table (`demo_sessions`)

```sql
CREATE TABLE public.demo_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.demo_users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(50),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_demo_sessions_user_id ON public.demo_sessions(user_id);
CREATE INDEX idx_demo_sessions_token ON public.demo_sessions(session_token);
CREATE INDEX idx_demo_sessions_expires_at ON public.demo_sessions(expires_at);
```

### 3. Audit Log Table (`demo_audit_log`)

```sql
CREATE TABLE public.demo_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.demo_users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address VARCHAR(50),
    user_agent TEXT,
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_demo_audit_log_user_id ON public.demo_audit_log(user_id);
CREATE INDEX idx_demo_audit_log_action ON public.demo_audit_log(action);
CREATE INDEX idx_demo_audit_log_timestamp ON public.demo_audit_log(timestamp);
```

---

## 🔧 Environment Variables (.env)

```bash
# PostgreSQL Database
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# JWT Authentication
JWT_SECRET=your_super_secret_jwt_key_change_in_production
JWT_EXPIRATION_HOURS=168  # 7 days

# Frontend URL (for email links)
FRONTEND_URL=https://yourdomain.com

# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_specific_password
SMTP_FROM_EMAIL=your.email@gmail.com
SMTP_FROM_NAME=Your App Name

# Admin & Notifications
ADMIN_EMAILS=admin1@example.com,admin2@example.com
SIGNUP_ALERT_RECIPIENTS=admin1@example.com,admin2@example.com
```

### Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate new app password for "Mail"
4. Use the 16-character password in `SMTP_PASSWORD`

---

## 🐍 Backend Implementation

### File Structure

```
backend/
├── auth_service.py      # Core authentication logic
├── app.py              # Flask API endpoints
└── db_init/
    └── 04_auth_schema.sql  # Database schema
```

### Key Components in `auth_service.py`

```python
import os
import jwt
import bcrypt
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
from flask import request, jsonify

# Configuration from environment
JWT_SECRET = os.environ.get('JWT_SECRET')
SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.environ.get('SMTP_FROM_EMAIL')
SMTP_FROM_NAME = os.environ.get('SMTP_FROM_NAME')
FRONTEND_URL = os.environ.get('FRONTEND_URL')

# Admin configuration
ADMIN_EMAILS = [email.strip().lower() for email in os.environ.get(
    'ADMIN_EMAILS', ''
).split(',') if email.strip()]

SIGNUP_ALERT_RECIPIENTS = [email.strip().lower() for email in os.environ.get(
    'SIGNUP_ALERT_RECIPIENTS', ''
).split(',') if email.strip()]
```

### Core Functions to Implement

1. **Password Hashing**
```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

2. **JWT Token Management**
```python
def generate_token(user_id: int, email: str, role: str = 'user') -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=168),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return {'valid': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError as e:
        return {'valid': False, 'error': f'Invalid token: {str(e)}'}
```

3. **Email Verification**
```python
def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)

def send_verification_email(email: str, token: str, full_name: str) -> bool:
    verification_link = f"{FRONTEND_URL}/verify-email.html?token={token}"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Verify Your Account'
    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = email
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Hello {full_name},</h2>
        <p>Thank you for registering! Please verify your email:</p>
        <a href="{verification_link}" style="display: inline-block; padding: 12px 24px; 
           background: #3b82f6; color: white; text-decoration: none; border-radius: 6px;">
           Verify Email Address
        </a>
        <p>Link expires in 24 hours.</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    
    return True
```

4. **Admin Signup Notification**
```python
def send_signup_notification(user_data: dict) -> bool:
    recipients = SIGNUP_ALERT_RECIPIENTS
    if not recipients:
        return True
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'New User Registration'
    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg['To'] = ', '.join(recipients)
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>New User Registration</h2>
        <div style="background: #f8fafc; padding: 16px; border-radius: 6px;">
            <p><strong>Name:</strong> {user_data.get('full_name')}</p>
            <p><strong>Email:</strong> {user_data.get('email')}</p>
            <p><strong>Organization:</strong> {user_data.get('organization')}</p>
            <p><strong>Position:</strong> {user_data.get('position')}</p>
            <p><strong>Mobile:</strong> {user_data.get('mobile')}</p>
            <p><strong>Country:</strong> {user_data.get('country')}</p>
            <p><strong>IP:</strong> {user_data.get('ip_address')}</p>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    
    return True
```

5. **User Registration**
```python
def register_user(email: str, password: str, organization: str, full_name: str,
                 position: str, mobile: str, country: str, ip_address: str = None,
                 user_agent: str = None) -> dict:
    
    # Validate & normalize email
    email = email.lower().strip()
    
    # Validate password
    if len(password) < 8:
        return {'success': False, 'error': 'Password must be at least 8 characters'}
    
    # Determine role
    user_role = 'admin' if email in ADMIN_EMAILS else 'user'
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check existing user
    cursor.execute("SELECT id FROM demo_users WHERE email = %s", (email,))
    if cursor.fetchone():
        return {'success': False, 'error': 'Email already registered'}
    
    # Hash password & generate token
    password_hash = hash_password(password)
    verification_token = generate_verification_token()
    
    # Insert user
    cursor.execute("""
        INSERT INTO demo_users 
        (email, password_hash, organization, full_name, position, mobile, country, role,
         verification_token, verification_sent_at, ip_address_signup, user_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
        RETURNING id, email, full_name
    """, (email, password_hash, organization, full_name, position, mobile, country,
          user_role, verification_token, ip_address, user_agent))
    
    user = cursor.fetchone()
    conn.commit()
    
    # Send emails
    send_verification_email(email, verification_token, full_name)
    send_signup_notification({
        'full_name': full_name,
        'email': email,
        'organization': organization,
        'position': position,
        'mobile': mobile,
        'country': country,
        'ip_address': ip_address,
        'user_agent': user_agent
    })
    
    return {
        'success': True,
        'message': 'Registration successful. Check your email to verify.',
        'user_id': user['id']
    }
```

6. **Admin Access Control**
```python
def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token'}), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if not token_data['valid']:
            return jsonify({'error': token_data['error']}), 401
        
        user_email = token_data['payload'].get('email', '').lower()
        
        # Check admin allowlist
        if user_email not in ADMIN_EMAILS:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Verify role in database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT role, is_active FROM demo_users WHERE email = %s",
            (user_email,)
        )
        user_row = cursor.fetchone()
        
        if not user_row or user_row['role'] != 'admin' or not user_row['is_active']:
            return jsonify({'error': 'Admin access required'}), 403
        
        request.user = token_data['payload']
        return f(*args, **kwargs)
    
    return decorated_function
```

---

## 🌐 Flask API Endpoints (`app.py`)

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from auth_service import *

app = Flask(__name__)
CORS(app)

# Registration
@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json()
    
    result = register_user(
        email=data['email'],
        password=data['password'],
        organization=data['organization'],
        full_name=data['full_name'],
        position=data['position'],
        mobile=data.get('mobile', ''),
        country=data['country'],
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )
    
    return jsonify(result), 201 if result['success'] else 400

# Login
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    
    result = login_user(
        email=data['email'],
        password=data['password'],
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')
    )
    
    return jsonify(result), 200 if result['success'] else 401

# Email Verification
@app.route('/api/auth/verify-email', methods=['POST'])
def auth_verify_email():
    data = request.get_json()
    result = verify_email_token(data['token'])
    return jsonify(result), 200 if result['success'] else 400

# Admin: Get Users
@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_get_users():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    search = request.args.get('search', '')
    
    # Query users with pagination
    # Implementation here...
    
    return jsonify({'success': True, 'users': users, 'pagination': pagination})

# Admin: Get Stats
@app.route('/api/admin/stats', methods=['GET'])
@require_admin
def admin_get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_users,
            COUNT(*) FILTER (WHERE email_verified = true) as verified_users,
            COUNT(*) FILTER (WHERE DATE(created_at) = CURRENT_DATE) as new_today,
            COUNT(*) FILTER (WHERE last_login >= NOW() - INTERVAL '7 days') as active_7_days
        FROM demo_users
    """)
    
    stats = cursor.fetchone()
    return jsonify({'success': True, 'stats': stats})
```

---

## 🎨 Frontend Implementation

### File Structure

```
frontend/
├── auth.html              # Login & Registration page
├── verify-email.html      # Email verification page
├── reset-password.html    # Password reset page
└── admin/
    └── dashboard.html     # Admin dashboard
```

### Key Frontend Features

1. **Responsive auth forms** with real-time validation
2. **Password strength indicator**
3. **Professional error handling**
4. **Loading states** during API calls
5. **Session management** with localStorage
6. **Auto-redirect** after successful actions
7. **Admin dashboard** with:
   - User statistics cards
   - Searchable user table
   - Pagination
   - Horizontal scroll for mobile
   - Export functionality

### Frontend JavaScript Pattern

```javascript
const API_BASE = '/api';

// Registration
async function handleRegister(formData) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (data.success) {
        showSuccess('Check your email to verify your account');
        setTimeout(() => switchToLogin(), 3000);
    } else {
        showError(data.error);
    }
}

// Login
async function handleLogin(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    });
    
    const data = await response.json();
    
    if (data.success) {
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        window.location.href = '/index.html';
    } else {
        showError(data.error);
    }
}

// Admin check
function checkAdminAccess() {
    const token = localStorage.getItem('auth_token');
    const user = JSON.parse(localStorage.getItem('user_data') || '{}');
    
    const ALLOWED_ADMINS = ['admin1@example.com', 'admin2@example.com'];
    
    if (!token || user.role !== 'admin' || !ALLOWED_ADMINS.includes(user.email.toLowerCase())) {
        window.location.href = '/auth.html';
        return false;
    }
    return true;
}
```

---

## 📧 Email Templates

### Verification Email Structure
- **Subject:** "Verify Your Account"
- **Content:** 
  - Personalized greeting
  - Clear call-to-action button
  - Expiration notice (24 hours)
  - Professional branding
  - Fallback plain text link

### Admin Notification Email Structure
- **Subject:** "New User Registration"
- **Content:**
  - All user details in structured format
  - Timestamp
  - IP address for security
  - Direct admin panel link (optional)

---

## 🔒 Security Best Practices

1. **Password Requirements:**
   - Minimum 8 characters
   - Consider adding complexity rules (uppercase, numbers, symbols)

2. **Token Security:**
   - Verification tokens: 32-byte URL-safe
   - JWT tokens: 7-day expiration
   - Store tokens securely (never in localStorage for sensitive apps)

3. **Email Security:**
   - Use app-specific passwords for Gmail
   - Never commit SMTP credentials
   - Implement rate limiting on email sends

4. **Admin Access:**
   - Allowlist-based (environment variable)
   - Double-check: frontend + backend
   - Verify active status in database

5. **Database Security:**
   - Use parameterized queries (prevent SQL injection)
   - Index sensitive fields
   - Regular backups
   - Lowercase email constraint

---

## 🚀 Deployment Checklist

### Before Production:

- [ ] Change all default secrets/passwords
- [ ] Set strong `JWT_SECRET` (64+ random characters)
- [ ] Configure production SMTP credentials
- [ ] Set correct `FRONTEND_URL`
- [ ] Configure `ADMIN_EMAILS` with real admin emails
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Test email delivery in production
- [ ] Verify admin access restrictions
- [ ] Test registration flow end-to-end
- [ ] Set up monitoring/logging
- [ ] Configure rate limiting
- [ ] Review CORS settings

---

## 🧪 Testing Guide

### 1. Registration Flow
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "organization": "Test Org",
    "full_name": "Test User",
    "position": "Developer",
    "mobile": "+1234567890",
    "country": "USA"
  }'
```

### 2. Email Verification
```bash
curl -X POST http://localhost:5000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "your_verification_token"}'
```

### 3. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### 4. Admin Access
```bash
curl -X GET http://localhost:5000/api/admin/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🐛 Troubleshooting

### Emails Not Sending
- Check SMTP credentials
- Verify Gmail app password is correct
- Check server firewall allows port 587
- Look for errors in application logs
- Test SMTP connection manually

### Admin Access Denied
- Verify email in `ADMIN_EMAILS` environment variable
- Check database role is set to 'admin'
- Restart application after env changes
- Clear browser cache/localStorage
- Check JWT token hasn't expired

### Database Connection Issues
- Verify PostgreSQL is running
- Check database credentials
- Ensure database exists
- Run schema initialization scripts
- Check network connectivity

---

## 📝 Customization Tips

1. **Branding:** Update email templates with your logo and colors
2. **Password Policy:** Modify validation rules as needed
3. **Session Duration:** Adjust JWT expiration time
4. **Email Provider:** Can use SendGrid, Mailgun, etc. instead of Gmail
5. **Frontend Theme:** Customize CSS variables for your brand
6. **Additional Fields:** Add custom user fields to registration
7. **Multi-factor Auth:** Can be added as enhancement
8. **OAuth Integration:** Can add Google/GitHub login

---

## 📚 Dependencies

### Python (requirements.txt)
```
Flask==3.0.0
flask-cors==4.0.0
psycopg2-binary==2.9.9
PyJWT==2.8.0
bcrypt==4.1.1
email-validator==2.1.0
gunicorn==21.2.0
```

### System Requirements
- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (optional but recommended)
- SMTP server access

---

## 💡 Additional Resources

- **bcrypt docs:** https://github.com/pyca/bcrypt/
- **PyJWT docs:** https://pyjwt.readthedocs.io/
- **Flask docs:** https://flask.palletsprojects.com/
- **Gmail SMTP setup:** https://support.google.com/mail/answer/7126229
- **PostgreSQL docs:** https://www.postgresql.org/docs/

---

## 📄 License & Credits

This implementation guide is based on production-tested code from ENMS Demo Platform.  
Feel free to adapt and customize for your project needs.

**Author:** AI Assistant  
**Project Reference:** ENMS Demo Authentication System  
**Date:** December 2025

---

## ✅ Quick Start Summary

1. **Setup Database:** Run SQL schema scripts
2. **Configure Environment:** Set all `.env` variables
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Initialize Backend:** Deploy Flask app with gunicorn
5. **Deploy Frontend:** Serve HTML files via Nginx
6. **Test Registration:** Sign up a test user
7. **Check Emails:** Verify verification and admin notification emails
8. **Access Admin:** Login with admin email and access `/admin` dashboard
9. **Production Deploy:** Follow deployment checklist

---

**🎉 You now have a complete, production-ready authentication system!**
