# Authentication System - ENMS Platform

## Overview

Production-ready authentication system with user registration, email verification, JWT sessions, admin dashboard, and role-based access control.

## Features

- ✅ User registration with email verification
- ✅ Secure login with JWT tokens (7-day expiration)
- ✅ Password hashing with bcrypt (12 rounds)
- ✅ Admin dashboard with user management
- ✅ Real-time admin notifications on new signups
- ✅ Password reset functionality
- ✅ Role-based access control (admin/user)
- ✅ Session tracking & audit logs
- ✅ Professional HTML email templates

## Quick Start

### 1. Initialize Database

The database schema is automatically created when you start the services. The file `database/init/05-auth-schema.sql` contains all table definitions.

### 2. Configure Environment Variables

Ensure the following variables are set in your `.env` file:

```bash
# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_change_in_production
JWT_EXPIRATION_HOURS=168

# Frontend URL (for email links)
FRONTEND_URL=http://10.33.10.109:8080

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_specific_password
SMTP_FROM_EMAIL=your.email@gmail.com
SMTP_FROM_NAME=ENMS Demo Platform

# Admin Configuration
ADMIN_EMAILS=admin1@example.com,admin2@example.com
SIGNUP_ALERT_RECIPIENTS=admin1@example.com,admin2@example.com
```

### 3. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check auth service logs
docker-compose logs -f auth-service

# Check if service is healthy
curl http://localhost:5000/api/auth/health
```

### 4. Access Frontend

- **Main Landing Page**: http://localhost:8080/auth.html
- **Admin Dashboard**: http://localhost:8080/admin/dashboard.html
- **Email Verification**: http://localhost:8080/verify-email.html?token=...
- **Password Reset**: http://localhost:8080/reset-password.html?token=...

## API Endpoints

### Public Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-email` - Verify email with token
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/health` - Health check

### Admin Endpoints (Requires Admin Role)

- `GET /api/admin/stats` - Get user statistics
- `GET /api/admin/users` - List users (paginated, searchable)
- `GET /api/admin/users/:id` - Get user details
- `POST /api/admin/users/:id/toggle-active` - Activate/deactivate user
- `GET /api/admin/export-users` - Export users to CSV

## Testing

### 1. Register a New User

```bash
curl -X POST http://localhost:8080/api/auth/register \
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

Expected Response:
```json
{
  "success": true,
  "message": "Registration successful. Please check your email to verify your account.",
  "user_id": 1,
  "role": "user"
}
```

### 2. Check Email

- User receives verification email with link
- Admins receive signup notification email

### 3. Verify Email

Click the link in the verification email or:

```bash
curl -X POST http://localhost:8080/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "your_verification_token"}'
```

### 4. Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Expected Response:
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User",
    "organization": "Test Org",
    "role": "user"
  }
}
```

### 5. Access Admin Dashboard

If your email is in `ADMIN_EMAILS`, you can access the admin dashboard at:
http://localhost:8080/admin/dashboard.html

### 6. Test Admin API

```bash
# Get user statistics
curl -X GET http://localhost:8080/api/admin/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List users
curl -X GET "http://localhost:8080/api/admin/users?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Search users
curl -X GET "http://localhost:8080/api/admin/users?search=test&page=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Schema

### Tables

1. **demo_users** - User accounts and profiles
2. **demo_sessions** - Active JWT sessions
3. **demo_audit_log** - Audit trail of user actions

### Key Fields

**demo_users:**
- `id` - Primary key
- `email` - Unique email (lowercase)
- `password_hash` - Bcrypt hashed password
- `full_name`, `organization`, `position`, `country` - Profile info
- `email_verified` - Boolean flag
- `role` - 'user' or 'admin'
- `is_active` - Account status
- `created_at`, `last_login` - Timestamps

## Security Features

✅ Password hashing with bcrypt (12 rounds)  
✅ JWT tokens with expiration  
✅ Email verification required  
✅ Admin role verification (environment variable + database)  
✅ Rate limiting on auth endpoints  
✅ CORS configured  
✅ SQL injection prevention (parameterized queries)  
✅ Session tracking and audit logs  
✅ IP address and user agent logging  

## Admin Configuration

To grant admin access:

1. Add email to `ADMIN_EMAILS` in `.env`:
   ```bash
   ADMIN_EMAILS=admin@example.com,another@example.com
   ```

2. Restart auth service:
   ```bash
   docker-compose restart auth-service
   ```

3. When the user registers with that email, they automatically get `role='admin'`

4. Admin access is verified at two levels:
   - Frontend checks user role and email allowlist
   - Backend decorator `@require_admin` validates on every request

## Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication on Gmail
2. Generate App Password:
   - Go to: https://myaccount.google.com/apppasswords
   - Create password for "Mail"
3. Use the 16-character password in `SMTP_PASSWORD`

### Email Templates

Professional HTML templates are included for:
- Email verification
- Password reset
- Admin signup notifications

## Troubleshooting

### Emails Not Sending

```bash
# Check SMTP configuration
docker-compose exec auth-service env | grep SMTP

# Check auth service logs
docker-compose logs auth-service | grep -i email
```

### Admin Access Denied

```bash
# Verify ADMIN_EMAILS is set
docker-compose exec auth-service env | grep ADMIN_EMAILS

# Check user role in database
docker exec -it enms-postgres psql -U $POSTGRES_USER -d enms \
  -c "SELECT email, role FROM demo_users WHERE email = 'your@email.com';"
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify database exists
docker exec -it enms-postgres psql -U $POSTGRES_USER -l

# Check if auth tables exist
docker exec -it enms-postgres psql -U $POSTGRES_USER -d enms \
  -c "\dt demo_*"
```

## Development

### Local Testing

```bash
# Run auth service locally
cd auth-service
pip install -r requirements.txt
python app.py
```

### Hot Reload

For development with auto-reload:

```bash
# Update docker-compose.yml to mount local code
volumes:
  - ./auth-service:/app

# Restart with debug mode
docker-compose restart auth-service
```

## Production Checklist

- [ ] Change `JWT_SECRET` to strong random value (64+ chars)
- [ ] Set `FRONTEND_URL` to production domain
- [ ] Configure SMTP with production email service
- [ ] Update `ADMIN_EMAILS` with real admin emails
- [ ] Enable HTTPS/SSL
- [ ] Review and tighten CORS settings
- [ ] Set up database backups
- [ ] Configure monitoring and alerts
- [ ] Review rate limiting settings
- [ ] Test password reset flow
- [ ] Test email delivery
- [ ] Verify admin dashboard access

## Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
    HTTP/HTTPS
         │
┌────────▼────────┐
│  Nginx Gateway  │  ← /api/auth/* → auth-service:5000
└────────┬────────┘
         │
┌────────▼────────────┐
│  Auth Service       │
│  (Flask/Gunicorn)   │
├─────────────────────┤
│ - Registration      │
│ - Login/Logout      │
│ - Email Verify      │
│ - Password Reset    │
│ - Admin APIs        │
└────────┬────────────┘
         │
    ┌────▼─────┬──────────┐
    │          │          │
┌───▼───┐  ┌──▼──┐  ┌───▼────┐
│ PgSQL │  │SMTP │  │ Redis  │
│ (DB)  │  │Email│  │(Cache) │
└───────┘  └─────┘  └────────┘
```

## License

Part of ENMS Platform - December 2025

## Support

For issues or questions, contact the development team or check the main ENMS documentation.
