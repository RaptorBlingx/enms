"""
Authentication Service API
ENMS Demo Platform
Created: December 11, 2025
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from auth_service import (
    register_user,
    login_user,
    verify_email_token,
    request_password_reset,
    reset_password,
    require_admin,
    get_db_connection,
    verify_token
)
from psycopg2.extras import RealDictCursor
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Configure appropriately for production
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ============================================================================
# Health Check
# ============================================================================

@app.route('/api/auth/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'auth-service',
        'status': 'healthy'
    }), 200

# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'organization', 'full_name', 'position', 'country']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
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
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Registration failed'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        result = login_user(
            email=data['email'],
            password=data['password'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        status_code = 200 if result['success'] else 401
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Login failed'
        }), 500

@app.route('/api/auth/verify-email', methods=['POST'])
def auth_verify_email():
    """Verify email with token"""
    try:
        data = request.get_json()
        
        if not data.get('token'):
            return jsonify({
                'success': False,
                'error': 'Verification token is required'
            }), 400
        
        result = verify_email_token(data['token'])
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Email verification endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Verification failed'
        }), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def auth_forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        result = request_password_reset(data['email'])
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Forgot password endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Request failed'
        }), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def auth_reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        
        if not data.get('token') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'error': 'Token and new password are required'
            }), 400
        
        result = reset_password(data['token'], data['new_password'])
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Reset password endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Password reset failed'
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout user (invalidate session)"""
    try:
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'No authorization token'
            }), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if token_data['valid']:
            # Invalidate session in database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE demo_sessions 
                SET is_active = false 
                WHERE session_token = %s
            """, (token,))
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500

@app.route('/api/auth/verify-token', methods=['POST'])
def auth_verify_token():
    """Verify JWT token validity"""
    try:
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'No authorization token'
            }), 401
        
        token = auth_header.split(' ')[1]
        token_data = verify_token(token)
        
        if token_data['valid']:
            return jsonify({
                'success': True,
                'valid': True,
                'user': token_data['payload']
            }), 200
        else:
            return jsonify({
                'success': False,
                'valid': False,
                'error': token_data['error']
            }), 401
            
    except Exception as e:
        logger.error(f"Token verification endpoint error: {e}")
        return jsonify({
            'success': False,
            'valid': False,
            'error': 'Verification failed'
        }), 500

# ============================================================================
# Admin Endpoints
# ============================================================================

@app.route('/api/admin/stats', methods=['GET'])
@require_admin
def admin_get_stats():
    """Get user statistics (admin only)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(*) FILTER (WHERE email_verified = true) as verified_users,
                COUNT(*) FILTER (WHERE DATE(created_at) = CURRENT_DATE) as new_today,
                COUNT(*) FILTER (WHERE last_login >= NOW() - INTERVAL '7 days') as active_7_days,
                COUNT(*) FILTER (WHERE role = 'admin') as admin_users
            FROM demo_users
            WHERE is_active = true
        """)
        
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': dict(stats)
        }), 200
        
    except Exception as e:
        logger.error(f"Admin stats endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch statistics'
        }), 500

@app.route('/api/admin/users', methods=['GET'])
@require_admin
def admin_get_users():
    """Get paginated user list with search (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '').strip()
        
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build query with search
        where_clause = ""
        params = []
        
        if search:
            where_clause = """
                WHERE (full_name ILIKE %s OR email ILIKE %s OR organization ILIKE %s)
            """
            search_pattern = f'%{search}%'
            params = [search_pattern, search_pattern, search_pattern]
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM demo_users {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['total']
        
        # Get users
        users_query = f"""
            SELECT id, email, full_name, organization, position, mobile, country,
                   email_verified, role, created_at, last_login, is_active
            FROM demo_users
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(users_query, params + [limit, offset])
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert datetime objects to ISO format
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
            if user['last_login']:
                user['last_login'] = user['last_login'].isoformat()
        
        total_pages = (total_count + limit - 1) // limit
        
        return jsonify({
            'success': True,
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Admin users endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch users'
        }), 500

@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@require_admin
def admin_get_user(user_id):
    """Get detailed user information (admin only)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, email, full_name, organization, position, mobile, country,
                   email_verified, verified_at, role, created_at, last_login, is_active,
                   ip_address_signup, deactivated_at
            FROM demo_users
            WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get user's sessions
        cursor.execute("""
            SELECT id, created_at, expires_at, last_activity, ip_address, is_active
            FROM demo_sessions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id,))
        
        sessions = cursor.fetchall()
        
        # Get user's audit log
        cursor.execute("""
            SELECT action, status, timestamp, ip_address, metadata
            FROM demo_audit_log
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (user_id,))
        
        audit_logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convert datetime objects to ISO format
        for key in ['created_at', 'last_login', 'verified_at', 'deactivated_at']:
            if user.get(key):
                user[key] = user[key].isoformat()
        
        for session in sessions:
            for key in ['created_at', 'expires_at', 'last_activity']:
                if session.get(key):
                    session[key] = session[key].isoformat()
        
        for log in audit_logs:
            if log.get('timestamp'):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'user': dict(user),
            'sessions': [dict(s) for s in sessions],
            'audit_logs': [dict(l) for l in audit_logs]
        }), 200
        
    except Exception as e:
        logger.error(f"Admin get user endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user details'
        }), 500

@app.route('/api/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@require_admin
def admin_toggle_user_active(user_id):
    """Activate/deactivate user account (admin only)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT is_active FROM demo_users WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        new_status = not user['is_active']
        deactivated_at = 'NOW()' if not new_status else 'NULL'
        
        cursor.execute(f"""
            UPDATE demo_users
            SET is_active = %s, deactivated_at = {deactivated_at}
            WHERE id = %s
        """, (new_status, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        action = 'activated' if new_status else 'deactivated'
        
        return jsonify({
            'success': True,
            'message': f'User {action} successfully',
            'is_active': new_status
        }), 200
        
    except Exception as e:
        logger.error(f"Admin toggle user endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update user status'
        }), 500

@app.route('/api/admin/export-users', methods=['GET'])
@require_admin
def admin_export_users():
    """Export users to CSV (admin only)"""
    try:
        import csv
        from io import StringIO
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT id, email, full_name, organization, position, mobile, country,
                   email_verified, role, created_at, last_login, is_active
            FROM demo_users
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'id', 'email', 'full_name', 'organization', 'position', 'mobile', 
            'country', 'email_verified', 'role', 'created_at', 'last_login', 'is_active'
        ])
        writer.writeheader()
        
        for user in users:
            user_dict = dict(user)
            if user_dict['created_at']:
                user_dict['created_at'] = user_dict['created_at'].isoformat()
            if user_dict['last_login']:
                user_dict['last_login'] = user_dict['last_login'].isoformat()
            writer.writerow(user_dict)
        
        csv_content = output.getvalue()
        output.close()
        
        from flask import make_response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=users_export.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"Admin export endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to export users'
        }), 500

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('AUTH_SERVICE_PORT', 5000))
    debug = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    
    logger.info(f"Starting Auth Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
