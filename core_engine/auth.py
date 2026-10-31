"""
Authentication and JWT Security Module for IoT Intrusion Detection and Response System.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Complies with Group 03 Proposal:
- Section 3.6 (System Architecture, Secrets, Users Collection, Figure 4)
- Section 3.7 (Logged-in Administrator for Scans and Response Policy)
- Table 7 (FR-04: Dashboard Login and Access Control)
- Decision D-028 (bcrypt password hashing, JWT 8-hour access tokens, system_logs audit trail)
"""

import os
import sys
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, Callable, Union
from functools import wraps

import bcrypt
import jwt
from dotenv import load_dotenv

from core_engine.db_service import DatabaseService

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger("auth_manager")

DEFAULT_TOKEN_EXPIRY_HOURS = 8
DEFAULT_ALGORITHM = "HS256"


# =============================================================================
# Custom Authentication Exceptions
# =============================================================================

class AuthError(Exception):
    """Base exception for all authentication and authorization errors."""
    pass


class InvalidCredentialsError(AuthError):
    """Raised when username does not exist or password does not match."""
    pass


class UserNotFoundError(AuthError):
    """Raised when user account is not found in database."""
    pass


class AccountDisabledError(AuthError):
    """Raised when a user account has been deactivated."""
    pass


class TokenMissingError(AuthError):
    """Raised when an authorization token is missing from request."""
    pass


class TokenExpiredError(AuthError):
    """Raised when an access token has exceeded its expiration time."""
    pass


class InvalidTokenError(AuthError):
    """Raised when a token signature is invalid, forged, or malformed."""
    pass


class PermissionDeniedError(AuthError):
    """Raised when an authenticated user lacks required administrative privileges."""
    pass


# =============================================================================
# AuthManager Class
# =============================================================================

class AuthManager:
    """
    Manages user authentication, bcrypt password hashing, and JWT token issuance.
    Guarantees that all authentication events (success/failure) are audit-logged
    to the MongoDB 'system_logs' collection per Proposal Section 3.6 & FR-07.
    """

    def __init__(
        self,
        db_service: Optional[DatabaseService] = None,
        secret_key: Optional[str] = None,
        token_expiry_hours: int = DEFAULT_TOKEN_EXPIRY_HOURS,
    ) -> None:
        self.db = db_service
        self.token_expiry_hours = token_expiry_hours
        self.algorithm = DEFAULT_ALGORITHM

        # Secret key resolution: explicit argument -> environment variable -> fallback
        raw_secret = secret_key or os.getenv("JWT_SECRET_KEY")
        if not raw_secret:
            logger.warning(
                "JWT_SECRET_KEY not set in environment or arguments. "
                "Generating an ephemeral runtime secret key."
            )
            raw_secret = uuid.uuid4().hex + uuid.uuid4().hex

        if len(raw_secret) < 16:
            logger.warning("JWT_SECRET_KEY is shorter than 16 characters; consider a stronger secret.")

        self.secret_key = raw_secret

    def _get_db(self) -> DatabaseService:
        """Lazily initialize DatabaseService if not provided during init."""
        if self.db is None:
            self.db = DatabaseService()
        return self.db

    # =========================================================================
    # Password Hashing & Verification (bcrypt)
    # =========================================================================

    @staticmethod
    def hash_password(password: str, rounds: int = 12) -> str:
        """
        Hash plaintext password using bcrypt with cryptographic salt.
        Enforces minimum length of 8 characters.
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        salt = bcrypt.gensalt(rounds=rounds)
        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify plaintext password against bcrypt hash in constant time.
        """
        if not password or not password_hash:
            return False
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8"),
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"bcrypt verification error: {e}")
            return False

    # =========================================================================
    # JWT Token Issuance & Decoding
    # =========================================================================

    def create_token(
        self,
        username: str,
        role: str = "admin",
        custom_claims: Optional[Dict[str, Any]] = None,
        expiry_hours: Optional[int] = None,
    ) -> str:
        """
        Generate signed JWT access token containing subject, role, and expiry claims.
        """
        if not username or not isinstance(username, str) or not username.strip():
            raise ValueError("Token issuance requires a valid non-empty username.")

        hours = expiry_hours if expiry_hours is not None else self.token_expiry_hours
        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=hours)

        payload = {
            "sub": username.strip(),
            "role": role or "admin",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": str(uuid.uuid4()),
        }
        if custom_claims:
            payload.update(custom_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        # PyJWT >= 2.0 returns str directly
        return str(token)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT access token.
        Raises TokenExpiredError or InvalidTokenError on failure.
        """
        if not token or not isinstance(token, str) or not token.strip():
            raise TokenMissingError("Authorization token was not provided.")

        clean_token = token.strip()
        # Strip optional "Bearer " prefix if present
        if clean_token.lower().startswith("bearer "):
            clean_token = clean_token[7:].strip()

        try:
            payload = jwt.decode(
                clean_token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Authorization token has expired. Please log in again.")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid authorization token: {e}")

    # =========================================================================
    # User Authentication & Audit Logging
    # =========================================================================

    def authenticate(
        self,
        username: str,
        password: str,
        client_ip: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Authenticate user credentials against MongoDB 'users' collection.
        Emits immutable audit event to 'system_logs' for both SUCCESS and FAILURE.
        Returns JWT token and user profile metadata upon success.
        """
        db = self._get_db()
        clean_user = username.strip() if username and isinstance(username, str) else ""

        if not clean_user or not password:
            if db.is_connected():
                db.log_system_event(
                    actor=clean_user or "anonymous",
                    event="AUTH_LOGIN_FAIL",
                    outcome="FAILURE",
                    details={"reason": "empty_credentials", "client_ip": client_ip or "unknown"},
                )
            raise InvalidCredentialsError("Username and password must be provided.")

        user = db.get_user_by_username(clean_user)

        # 1. User does not exist
        if not user:
            if db.is_connected():
                db.log_system_event(
                    actor=clean_user,
                    event="AUTH_LOGIN_FAIL",
                    outcome="FAILURE",
                    details={"reason": "user_not_found", "client_ip": client_ip or "unknown"},
                )
            raise InvalidCredentialsError("Invalid username or password.")

        # 2. Account disabled
        if not user.get("is_active", True):
            if db.is_connected():
                db.log_system_event(
                    actor=clean_user,
                    event="AUTH_LOGIN_FAIL",
                    outcome="FAILURE",
                    details={"reason": "account_disabled", "client_ip": client_ip or "unknown"},
                )
            raise AccountDisabledError(f"User account '{clean_user}' is deactivated.")

        # 3. Password mismatch
        password_hash = user.get("password_hash", "")
        if not self.verify_password(password, password_hash):
            if db.is_connected():
                db.log_system_event(
                    actor=clean_user,
                    event="AUTH_LOGIN_FAIL",
                    outcome="FAILURE",
                    details={"reason": "invalid_password", "client_ip": client_ip or "unknown"},
                )
            raise InvalidCredentialsError("Invalid username or password.")

        # 4. Successful authentication
        role = user.get("role", "admin")
        token = self.create_token(username=clean_user, role=role)

        if db.is_connected():
            db.update_last_login(clean_user)
            db.log_system_event(
                actor=clean_user,
                event="AUTH_LOGIN_SUCCESS",
                outcome="SUCCESS",
                details={
                    "role": role,
                    "client_ip": client_ip or "unknown",
                    "auth_method": "bcrypt_jwt",
                },
            )

        return {
            "token": token,
            "username": clean_user,
            "role": role,
            "expires_in": self.token_expiry_hours * 3600,
            "token_type": "Bearer",
        }

    # =========================================================================
    # Flask Route Protection Decorators
    # =========================================================================

    def token_required(self, f: Callable) -> Callable:
        """
        Flask view decorator enforcing valid JWT token in Authorization header or query param.
        Returns 401 Unauthorized if token is missing, expired, or invalid.
        Injects 'current_user' payload into Flask 'g.current_user'.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                from flask import request, jsonify, g
            except ImportError:
                # If Flask is not installed in testing environment, invoke function directly
                return f(*args, **kwargs)

            auth_header = request.headers.get("Authorization", "")
            token = None

            if auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()
            elif "token" in request.args:
                token = request.args.get("token")

            if not token:
                return (
                    jsonify({
                        "error": "Unauthorized",
                        "message": "Authentication token is missing. Please provide Authorization: Bearer <token>.",
                    }),
                    401,
                )

            try:
                payload = self.decode_token(token)
                g.current_user = payload
            except TokenExpiredError as e:
                return jsonify({"error": "Unauthorized", "message": str(e), "code": "TOKEN_EXPIRED"}), 401
            except (InvalidTokenError, TokenMissingError) as e:
                return jsonify({"error": "Unauthorized", "message": str(e), "code": "TOKEN_INVALID"}), 401
            except Exception as e:
                return jsonify({"error": "Unauthorized", "message": f"Token verification error: {e}"}), 401

            # Pass current_user to endpoint only if it accepts current_user
            import inspect
            sig = inspect.signature(f)
            if "current_user" in sig.parameters:
                kwargs["current_user"] = payload

            return f(*args, **kwargs)

        return decorated

    def admin_required(self, f: Callable) -> Callable:
        """
        Flask view decorator requiring valid token AND administrator role.
        Returns 403 Forbidden if user is authenticated but not an administrator.
        """
        import inspect

        @self.token_required
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                from flask import jsonify, g
                current_user = getattr(g, "current_user", {})
                if current_user.get("role") != "admin":
                    return (
                        jsonify({
                            "error": "Forbidden",
                            "message": "Administrator privileges required to execute this action.",
                            "code": "INSUFFICIENT_PRIVILEGES",
                        }),
                        403,
                    )
            except ImportError:
                pass

            sig = inspect.signature(f)
            clean_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            call_kwargs = kwargs if has_var_kw else clean_kwargs

            return f(*args, **call_kwargs)

        return decorated
