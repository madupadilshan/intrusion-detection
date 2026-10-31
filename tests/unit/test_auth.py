"""
Unit tests for Authentication and Secrets Management module.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Complies with Proposal Section 3.6, Section 3.7, and FR-04:
- bcrypt password hashing & verification
- JWT creation, decoding, expiration, and signature tampering resilience
- User authentication and system_logs audit trail logging
- Flask route protection decorators (@token_required and @admin_required)
- CLI admin provisioning (tools/create_admin.py)
"""

import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify

from core_engine.auth import (
    AuthManager,
    AuthError,
    InvalidCredentialsError,
    UserNotFoundError,
    AccountDisabledError,
    TokenMissingError,
    TokenExpiredError,
    InvalidTokenError,
    PermissionDeniedError,
)
from tools.create_admin import create_or_update_admin


TEST_SECRET = "super_secret_test_key_for_jwt_auth_testing_12345"


@pytest.fixture
def auth_mgr():
    """Provides an AuthManager instance configured with a known test secret and mock DB."""
    mock_db = MagicMock()
    mock_db.is_connected.return_value = True
    return AuthManager(db_service=mock_db, secret_key=TEST_SECRET, token_expiry_hours=8)


# =============================================================================
# 1. Password Hashing and Verification (bcrypt)
# =============================================================================

def test_hash_password_valid():
    """Verify that bcrypt produces valid hash with salt and work factor."""
    password = "SecureAdminPassword!2026"
    pw_hash = AuthManager.hash_password(password, rounds=10)

    assert pw_hash.startswith("$2b$")
    assert pw_hash != password
    # Verification succeeds with correct password
    assert AuthManager.verify_password(password, pw_hash) is True
    # Verification fails with wrong password
    assert AuthManager.verify_password("WrongPassword123", pw_hash) is False


def test_hash_password_length_enforcement():
    """Verify minimum 8 characters requirement."""
    with pytest.raises(ValueError, match="at least 8 characters"):
        AuthManager.hash_password("short1")

    with pytest.raises(ValueError, match="non-empty string"):
        AuthManager.hash_password("")


def test_verify_password_edge_cases():
    """Verify edge cases in password verification."""
    assert AuthManager.verify_password("", "some_hash") is False
    assert AuthManager.verify_password("password", "") is False
    assert AuthManager.verify_password("password", "invalid_hash_format") is False


# =============================================================================
# 2. JWT Token Issuance and Verification
# =============================================================================

def test_token_creation_and_decoding(auth_mgr):
    """Verify JWT token claims and standard decoding."""
    token = auth_mgr.create_token(username="admin_user", role="admin")
    assert isinstance(token, str)

    payload = auth_mgr.decode_token(token)
    assert payload["sub"] == "admin_user"
    assert payload["role"] == "admin"
    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload
    assert payload["exp"] > payload["iat"]


def test_token_with_bearer_prefix(auth_mgr):
    """Verify that 'Bearer <token>' format is parsed seamlessly."""
    token = auth_mgr.create_token(username="analyst_alice", role="analyst")
    bearer_token = f"Bearer {token}"

    payload = auth_mgr.decode_token(bearer_token)
    assert payload["sub"] == "analyst_alice"
    assert payload["role"] == "analyst"


def test_token_expiration(auth_mgr):
    """Verify that expired tokens raise TokenExpiredError."""
    # Create token that expired 1 hour ago
    expired_token = auth_mgr.create_token(
        username="admin_user",
        expiry_hours=-1,
    )

    with pytest.raises(TokenExpiredError, match="expired"):
        auth_mgr.decode_token(expired_token)


def test_token_signature_tampering(auth_mgr):
    """Verify that forged tokens or wrong secrets raise InvalidTokenError."""
    token = auth_mgr.create_token(username="admin_user", role="admin")

    # Decode with a different secret
    other_mgr = AuthManager(secret_key="completely_different_forged_secret_key_123")
    with pytest.raises(InvalidTokenError):
        other_mgr.decode_token(token)

    # Tampered payload string
    tampered_token = token[:-5] + "AAAAA"
    with pytest.raises(InvalidTokenError):
        auth_mgr.decode_token(tampered_token)


def test_token_missing(auth_mgr):
    """Verify that missing token raises TokenMissingError."""
    with pytest.raises(TokenMissingError):
        auth_mgr.decode_token("")

    with pytest.raises(TokenMissingError):
        auth_mgr.decode_token("   ")


# =============================================================================
# 3. User Authentication and Audit Logging
# =============================================================================

def test_authenticate_success(auth_mgr):
    """Test successful login: updates last login, logs AUTH_LOGIN_SUCCESS, returns token."""
    raw_password = "CorrectAdminPassword2026!"
    hashed_pw = AuthManager.hash_password(raw_password)

    auth_mgr.db.get_user_by_username.return_value = {
        "username": "admin",
        "password_hash": hashed_pw,
        "role": "admin",
        "is_active": True,
    }

    result = auth_mgr.authenticate("admin", raw_password, client_ip="192.168.50.10")

    assert "token" in result
    assert result["username"] == "admin"
    assert result["role"] == "admin"
    assert result["token_type"] == "Bearer"

    # Verify last_login update called
    auth_mgr.db.update_last_login.assert_called_once_with("admin")

    # Verify system_logs event recorded
    auth_mgr.db.log_system_event.assert_called_once_with(
        actor="admin",
        event="AUTH_LOGIN_SUCCESS",
        outcome="SUCCESS",
        details={
            "role": "admin",
            "client_ip": "192.168.50.10",
            "auth_method": "bcrypt_jwt",
        },
    )


def test_authenticate_wrong_password(auth_mgr):
    """Test failed login due to wrong password: logs AUTH_LOGIN_FAIL."""
    hashed_pw = AuthManager.hash_password("ValidPassword2026!")

    auth_mgr.db.get_user_by_username.return_value = {
        "username": "admin",
        "password_hash": hashed_pw,
        "role": "admin",
        "is_active": True,
    }

    with pytest.raises(InvalidCredentialsError, match="Invalid username or password"):
        auth_mgr.authenticate("admin", "WrongPassword999", client_ip="10.0.0.99")

    # Verify audit failure log
    auth_mgr.db.log_system_event.assert_called_once_with(
        actor="admin",
        event="AUTH_LOGIN_FAIL",
        outcome="FAILURE",
        details={"reason": "invalid_password", "client_ip": "10.0.0.99"},
    )


def test_authenticate_user_not_found(auth_mgr):
    """Test failed login due to nonexistent user."""
    auth_mgr.db.get_user_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError, match="Invalid username or password"):
        auth_mgr.authenticate("nonexistent_user", "AnyPassword123!", client_ip="10.0.0.55")

    auth_mgr.db.log_system_event.assert_called_once_with(
        actor="nonexistent_user",
        event="AUTH_LOGIN_FAIL",
        outcome="FAILURE",
        details={"reason": "user_not_found", "client_ip": "10.0.0.55"},
    )


def test_authenticate_deactivated_account(auth_mgr):
    """Test failed login due to inactive account."""
    hashed_pw = AuthManager.hash_password("ValidPassword2026!")

    auth_mgr.db.get_user_by_username.return_value = {
        "username": "disabled_user",
        "password_hash": hashed_pw,
        "role": "operator",
        "is_active": False,
    }

    with pytest.raises(AccountDisabledError, match="deactivated"):
        auth_mgr.authenticate("disabled_user", "ValidPassword2026!", client_ip="192.168.50.15")

    auth_mgr.db.log_system_event.assert_called_once_with(
        actor="disabled_user",
        event="AUTH_LOGIN_FAIL",
        outcome="FAILURE",
        details={"reason": "account_disabled", "client_ip": "192.168.50.15"},
    )


# =============================================================================
# 4. Flask Route Protection Decorators
# =============================================================================

@pytest.fixture
def app_client(auth_mgr):
    """Provides a test Flask application equipped with auth decorators."""
    app = Flask(__name__)

    @app.route("/api/public")
    def public_route():
        return jsonify({"status": "open"})

    @app.route("/api/protected")
    @auth_mgr.token_required
    def protected_route(current_user):
        return jsonify({"status": "protected", "user": current_user["sub"]})

    @app.route("/api/admin-only")
    @auth_mgr.admin_required
    def admin_route():
        return jsonify({"status": "admin_granted"})

    with app.test_client() as client:
        yield client


def test_protected_route_missing_token(app_client):
    """Verify that requests lacking authorization header get 401 Unauthorized."""
    resp = app_client.get("/api/protected")
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["error"] == "Unauthorized"
    assert "missing" in data["message"].lower()


def test_protected_route_valid_token(app_client, auth_mgr):
    """Verify that requests with valid bearer token succeed."""
    token = auth_mgr.create_token(username="test_admin", role="admin")
    resp = app_client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "protected"
    assert data["user"] == "test_admin"


def test_protected_route_query_param_token(app_client, auth_mgr):
    """Verify token passed via ?token= query parameter (for Socket.IO handshake)."""
    token = auth_mgr.create_token(username="socket_client", role="operator")
    resp = app_client.get(f"/api/protected?token={token}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"] == "socket_client"


def test_protected_route_expired_token(app_client, auth_mgr):
    """Verify expired token gets 401 with TOKEN_EXPIRED code."""
    expired_token = auth_mgr.create_token("admin_user", expiry_hours=-2)
    resp = app_client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["code"] == "TOKEN_EXPIRED"


def test_admin_route_authorization(app_client, auth_mgr):
    """Verify role-based access control: operator gets 403 Forbidden, admin gets 200 OK."""
    op_token = auth_mgr.create_token(username="operator_bob", role="operator")
    admin_token = auth_mgr.create_token(username="admin_alice", role="admin")

    # Operator access denied
    resp_op = app_client.get(
        "/api/admin-only",
        headers={"Authorization": f"Bearer {op_token}"},
    )
    assert resp_op.status_code == 403
    data_op = resp_op.get_json()
    assert data_op["code"] == "INSUFFICIENT_PRIVILEGES"

    # Admin access granted
    resp_admin = app_client.get(
        "/api/admin-only",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_admin.status_code == 200
    data_admin = resp_admin.get_json()
    assert data_admin["status"] == "admin_granted"


# =============================================================================
# 5. CLI Admin Provisioning (tools/create_admin.py)
# =============================================================================

def test_cli_create_admin_new_user():
    """Verify create_or_update_admin creates new user."""
    mock_db = MagicMock()
    mock_db.is_connected.return_value = True
    mock_db.get_user_by_username.return_value = None
    mock_db.create_user.return_value = "new-uuid-12345"

    success = create_or_update_admin(
        username="new_admin",
        password="SuperStrongPassword2026!",
        role="admin",
        force=False,
        db_service=mock_db,
    )

    assert success is True
    mock_db.create_user.assert_called_once()
    mock_db.log_system_event.assert_called_once_with(
        actor="cli_admin",
        event="USER_CREATED",
        outcome="SUCCESS",
        details={"username": "new_admin", "user_id": "new-uuid-12345", "role": "admin"},
    )


def test_cli_create_admin_existing_user_without_force():
    """Verify create_or_update_admin warns and returns False if user exists without --force."""
    mock_db = MagicMock()
    mock_db.is_connected.return_value = True
    mock_db.get_user_by_username.return_value = {"username": "existing_user"}

    success = create_or_update_admin(
        username="existing_user",
        password="SuperStrongPassword2026!",
        role="admin",
        force=False,
        db_service=mock_db,
    )

    assert success is False
    mock_db.create_user.assert_not_called()


def test_cli_create_admin_existing_user_with_force():
    """Verify create_or_update_admin updates password with --force."""
    mock_db = MagicMock()
    mock_db.is_connected.return_value = True
    mock_db.get_user_by_username.return_value = {"username": "existing_user"}
    mock_db.update_user_password.return_value = True

    success = create_or_update_admin(
        username="existing_user",
        password="NewPasswordReset2026!",
        role="admin",
        force=True,
        db_service=mock_db,
    )

    assert success is True
    mock_db.update_user_password.assert_called_once()
    mock_db.log_system_event.assert_called_once_with(
        actor="cli_admin",
        event="USER_PASSWORD_RESET",
        outcome="SUCCESS",
        details={"username": "existing_user", "role": "admin"},
    )


def test_cli_create_admin_short_password():
    """Verify rejection of password shorter than 8 characters."""
    mock_db = MagicMock()
    mock_db.is_connected.return_value = True

    success = create_or_update_admin(
        username="admin",
        password="short",
        db_service=mock_db,
    )

    assert success is False
    mock_db.create_user.assert_not_called()
