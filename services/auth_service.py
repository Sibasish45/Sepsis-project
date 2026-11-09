"""
User Authentication & Security Service for Sepsis CDSS.
Handles user password hashing, authentication, role verification, and staff account management.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_cursor
from utils.errors import AuthenticationError, ValidationError, ForbiddenError

class AuthService:
    def authenticate_user(self, username, password):
        """
        Authenticates user with username and password.
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s" if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()

        if not user:
            raise AuthenticationError("Invalid username or password.")

        user_dict = dict(user) if isinstance(user, dict) else dict(zip([col[0] for col in cursor.description], user))

        if not user_dict.get("is_active"):
            raise AuthenticationError("User account is inactive. Please contact an Administrator.")

        if not check_password_hash(user_dict["password_hash"], password):
            raise AuthenticationError("Invalid username or password.")

        # Update last login timestamp
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s" if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_dict["id"],)
            )

        # Return user info without password hash
        user_dict.pop("password_hash", None)
        return user_dict

    def register_user(self, username, email, password, full_name, role="NURSE", creator_role="ADMIN"):
        """
        Registers a new staff member (Admin-restricted).
        """
        if creator_role != "ADMIN":
            raise ForbiddenError("Only Administrators can create new user accounts.")

        if role not in ("DOCTOR", "NURSE", "ADMIN"):
            raise ValidationError("Invalid role specified. Must be DOCTOR, NURSE, or ADMIN.")

        hashed_password = generate_password_hash(password)

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, full_name, role, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                """ if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                """
                INSERT INTO users (username, email, password_hash, full_name, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, email, hashed_password, full_name, role, True)
            )
            user_id = cursor.lastrowid

        return {"id": user_id, "username": username, "email": email, "full_name": full_name, "role": role}

    def get_user_by_id(self, user_id):
        """Retrieves user info by ID."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT id, username, email, full_name, role, is_active, last_login, created_at FROM users WHERE id = %s" if not hasattr(cursor, 'execute') or 'sqlite3' not in str(type(cursor)) else
                "SELECT id, username, email, full_name, role, is_active, last_login, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            user = cursor.fetchone()
            if not user:
                return None
            return dict(user) if isinstance(user, dict) else dict(zip([col[0] for col in cursor.description], user))

auth_service_instance = AuthService()
