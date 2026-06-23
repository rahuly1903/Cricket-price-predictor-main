"""Authentication helpers."""

import hashlib
import secrets

from services import storage


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, digest = password_hash.split("$", 1)
    except ValueError:
        return False
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return secrets.compare_digest(computed.hex(), digest)


def register_user(username: str, email: str, password: str) -> tuple[dict | None, str | None]:
    username = username.strip()
    email = email.strip()

    if len(username) < 3:
        return None, "Username must be at least 3 characters."
    if "@" not in email:
        return None, "Please enter a valid email address."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if storage.username_exists(username):
        return None, "Username already exists."
    if storage.email_exists(email):
        return None, "Email already registered."

    user = storage.create_record(
        "users",
        {
            "username": username,
            "email": email,
            "password_hash": hash_password(password),
            "club_id": None,
        },
    )
    return user, None


def authenticate_user(username_or_email: str, password: str) -> tuple[dict | None, str | None]:
    identifier = username_or_email.strip().lower()
    users = storage.get_all("users")
    user = next(
        (
            u
            for u in users
            if u.get("username", "").lower() == identifier or u.get("email", "").lower() == identifier
        ),
        None,
    )
    if not user or not verify_password(password, user.get("password_hash", "")):
        return None, "Invalid username/email or password."
    return user, None
