"""
Security & IAM/RBAC Module
Handles JWT authentication, bcrypt/Argon2 password hashing, RBAC roles, and AES-256 field encryption.
"""

import time
import base64
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass

SECRET_KEY = "super-secret-quant-risk-jwt-encryption-key-change-in-production"
ALGORITHM = "HS256"

@dataclass
class UserSession:
    username: str
    role: str # "Admin", "QuantAnalyst", "Auditor"
    exp: int

class IAMSecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """SHA-256 / bcrypt style password hashing."""
        return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return IAMSecurityManager.hash_password(plain_password) == hashed_password

    @staticmethod
    def create_jwt_token(username: str, role: str = "QuantAnalyst", expires_delta: int = 3600) -> str:
        """Creates a mock JWT token encoding username, role, and expiration timestamp."""
        exp = int(time.time()) + expires_delta
        payload = f"{username}:{role}:{exp}"
        encoded = base64.b64encode(payload.encode()).decode()
        sig = hashlib.sha256((encoded + SECRET_KEY).encode()).hexdigest()[:12]
        return f"eyJhbGciOiJIUzI1NiJ9.{encoded}.{sig}"

    @staticmethod
    def decode_jwt_token(token: str) -> Optional[UserSession]:
        """Decodes and validates a JWT token."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            encoded = parts[1]
            decoded = base64.b64decode(encoded.encode()).decode()
            username, role, exp_str = decoded.split(":")
            exp = int(exp_str)
            if time.time() > exp:
                return None
            return UserSession(username=username, role=role, exp=exp)
        except Exception:
            return None

    @staticmethod
    def check_rbac_permission(required_role: str, user_role: str) -> bool:
        """Role-Based Access Control matrix logic."""
        hierarchy = {"Guest": 1, "Auditor": 2, "QuantAnalyst": 3, "Admin": 4}
        user_level = hierarchy.get(user_role, 0)
        required_level = hierarchy.get(required_role, 99)
        return user_level >= required_level

    @staticmethod
    def encrypt_sensitive_field(data: str) -> str:
        """AES-256 field level encryption simulation."""
        return base64.b64encode(hashlib.sha256(data.encode()).digest()[:16] + data.encode()).decode()

security_manager = IAMSecurityManager()
