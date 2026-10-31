"""
CLI Tool to Create and Manage Administrator Accounts.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Complies with Proposal Section 3.6, Section 3.7, and FR-04:
- No open registration page: Admin users are provisioned exclusively via CLI.
- Passwords stored as secure bcrypt hashes.
- Actions audit-logged to MongoDB 'system_logs'.
"""

import os
import sys
import argparse
import getpass
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core_engine.db_service import DatabaseService
from core_engine.auth import AuthManager

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("create_admin")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Provision or reset administrator accounts for IoT IDS Dashboard.",
    )
    parser.add_argument(
        "--username",
        "-u",
        type=str,
        help="Administrator username (default: prompts interactively).",
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        help="Administrator password (if omitted, prompts securely without echoing).",
    )
    parser.add_argument(
        "--role",
        "-r",
        type=str,
        default="admin",
        choices=["admin", "operator", "analyst"],
        help="User authorization role (default: admin).",
    )
    parser.add_argument(
        "--db-name",
        type=str,
        default=os.getenv("DB_NAME", "iot_ids_db"),
        help="Target MongoDB database name (default: from DB_NAME or 'iot_ids_db').",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite password if user already exists.",
    )
    return parser.parse_args()


def create_or_update_admin(
    username: str,
    password: str,
    role: str = "admin",
    db_name: str = "iot_ids_db",
    force: bool = False,
    db_service: DatabaseService = None,
) -> bool:
    """Core logic to provision an administrator account."""
    if not username or not username.strip():
        logger.error("Username cannot be empty.")
        return False

    clean_user = username.strip()

    if not password or len(password) < 8:
        logger.error("Password must be at least 8 characters long.")
        return False

    db = db_service or DatabaseService(db_name=db_name)
    if not db.is_connected():
        logger.error(f"Could not connect to MongoDB database '{db_name}'. Is MongoDB running?")
        return False

    # Check if user already exists
    existing = db.get_user_by_username(clean_user)
    password_hash = AuthManager.hash_password(password)

    if existing:
        if not force:
            logger.warning(
                f"User '{clean_user}' already exists. Use --force to update their password."
            )
            return False

        # Force update password
        success = db.update_user_password(clean_user, password_hash)
        if success:
            db.log_system_event(
                actor="cli_admin",
                event="USER_PASSWORD_RESET",
                outcome="SUCCESS",
                details={"username": clean_user, "role": role},
            )
            logger.info(f"Successfully updated password for existing user '{clean_user}'.")
            return True
        else:
            logger.error(f"Failed to update password for user '{clean_user}'.")
            return False

    # Create new user
    user_id = db.create_user(username=clean_user, password_hash=password_hash, role=role)
    if user_id:
        db.log_system_event(
            actor="cli_admin",
            event="USER_CREATED",
            outcome="SUCCESS",
            details={"username": clean_user, "user_id": user_id, "role": role},
        )
        logger.info(f"Successfully created {role} user '{clean_user}' (user_id: {user_id}).")
        return True
    else:
        logger.error(f"Failed to create user '{clean_user}' in MongoDB.")
        return False


def main():
    args = parse_args()

    username = args.username
    if not username:
        try:
            username = input("Enter administrator username: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(1)

    password = args.password
    if not password:
        try:
            password = getpass.getpass("Enter administrator password (min 8 chars): ")
            password_confirm = getpass.getpass("Confirm password: ")
            if password != password_confirm:
                logger.error("Passwords do not match.")
                sys.exit(1)
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(1)

    success = create_or_update_admin(
        username=username,
        password=password,
        role=args.role,
        db_name=args.db_name,
        force=args.force,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

